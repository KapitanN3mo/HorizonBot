import disnake
import peewee
from disnake.ext import commands
import datetime
from permissions import admin_permission_required
import core
import database
from assets import emojis


class Scheduler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    @admin_permission_required
    async def create_schedule(self, inter: disnake.CommandInteraction, name: str, expiration: str):
        try:
            date = datetime.datetime.strptime(expiration, '%d.%m.%Y')
        except:
            await inter.send('Ошибка: Некорректная запись даты.')
            return
        try:
            database.Schedule.insert(guild=inter.guild.id,
                                     name=name,
                                     expiration=date,
                                     author=database.User.get(database.User.user_id == inter.author.id,
                                                              database.User.guild_id == inter.guild.id)).execute()
        except peewee.IntegrityError:
            await inter.send(f'{emojis.exclamation}`Задача с именем {name} уже существует!`')
        except Exception as ex:
            await inter.send(f'{emojis.exclamation}`Ошибка БД: {ex}`')
        else:
            await inter.send(f'{emojis.white_check_mark} `Задача {name} создана!`')

    @commands.slash_command()
    @admin_permission_required
    async def scheduler(self, inter: disnake.CommandInteraction):
        view = SchedulerView(inter.guild)
        view.interaction = inter
        await inter.send(view=view, embed=view.emb)

    @commands.slash_command()
    @admin_permission_required
    async def edit_task(self, inter: disnake.CommandInteraction, schedule_name: str,
                        task_id: int,
                        new_executor: disnake.Member = None,
                        new_text: str = None):
        if new_text is None and new_executor is None:
            await inter.send(f'Нет изменений')
            return
        schedule = database.Schedule.get_or_none(database.Schedule.name == schedule_name,
                                                 database.Schedule.guild == inter.id)
        if schedule is None:
            await inter.send(f'План с именем {schedule_name} не обнаружен')
            return
        task = database.Task.get_or_none(database.Task.schedule == schedule, database.Task.task_number == task_id)
        if task is None:
            await inter.send('Такой задачи нет')
        else:
            if new_executor is not None:
                task.executor = database.User.get(database.User.user_id == new_executor.id,
                                                  database.User.guild_id == inter.guild_id)
            if new_text is not None:
                task.text = new_text
            task.save()
            await inter.send('Задача изменена')

    @commands.slash_command()
    @admin_permission_required
    async def create_task(self, inter: disnake.CommandInteraction, block_name: str, executor: disnake.Member,
                          text: str):
        tasks = [*database.Schedule.select().where(database.Schedule.guild == inter.guild_id,
                                                   database.Schedule.get(database.Schedule.guild == inter.guild_id,
                                                                         database.Schedule.name == block_name))]
        start_number = -1
        if len(tasks) > 0:
            start_number = sorted(tasks, key=lambda task: task.task_number)[-1].task_number

        database.Task.insert(
            schedule=database.Schedule.get(database.Schedule.guild == inter.guild_id,
                                           database.Schedule.name == block_name),
            text=text,
            task_number=start_number + 1,
            executor=database.User.get(database.User.guild_id == inter.guild_id, database.User.user_id == executor.id),
        ).execute()
        await inter.send('Ok', ephemeral=True)

    @create_task.autocomplete('block_name')
    async def block_name_autocomplete(self, inter: disnake.CommandInteraction, string: str):
        string = string.lower()
        return [block.name for block in database.Schedule.select().where(database.Schedule.guild == inter.guild_id) if
                string in block.name]


class SchedulerView(disnake.ui.View):
    def __init__(self, guild: disnake.Guild):
        super(SchedulerView, self).__init__()
        self.interaction = None
        self.guild = guild
        self.schedules = []
        self.emb = disnake.Embed()
        self.index = 0
        self.next_button = disnake.ui.Button(style=disnake.ButtonStyle.blurple, emoji='▶')
        self.next_button.callback = self.next_button
        self.back_button = disnake.ui.Button(style=disnake.ButtonStyle.blurple, emoji='◀')
        self.back_button.callback = self.back_button
        self.render()

    def render(self):
        emb = disnake.Embed(color=disnake.Color.red(), description='')
        schedules = [*database.Schedule.select().where(database.Schedule.guild == self.guild.id)]
        if len(schedules) == 0:
            emb.description = "Планов нет"
        else:
            self.clear_items()
            self.next_button.disabled = True
            self.next_button.callback = self.next_callback
            self.back_button.disabled = True
            self.back_button.callback = self.back_callback
            if 0 < self.index:
                self.back_button.disabled = False
            elif self.index < len(schedules) - 1:
                self.next_button.disabled = False
            self.add_item(self.back_button)
            self.add_item(self.next_button)
            schedule = schedules[self.index]
            tasks = [*database.Task.select().where(database.Task.schedule == schedule)]
            counter = 0
            author = self.guild.get_member(schedule.author.user_id)
            emb.set_author(name=author.display_name, icon_url=author.display_avatar)
            emb.title = f'План: {schedule.name}\n'
            emb.set_footer(text=f'Задача {self.index + 1} из {len(schedules)}',
                           icon_url=core.Bot.get_bot().user.display_avatar)
            if len(tasks) == 0:
                emb.description += '```В этом плане нет задач```'
            else:
                for task in tasks:
                    executor = self.guild.get_member(task.executor.user_id)
                    emb.description += f'```[{counter}] Задача для {executor.display_name}\n-> {task.text}\n```'
                    counter += 1
            emb.add_field(name="Срок", value=f'```{(schedule.expiration - datetime.datetime.now()).days} дней```')

        self.emb = emb

    async def next_callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.index += 1
        self.render()
        await inter.edit_original_message(view=self, embed=self.emb)
        self.interaction = inter

    async def back_callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.index -= 1
        self.render()
        await inter.edit_original_message(view=self, embed=self.emb)
        self.interaction = inter

    async def on_timeout(self) -> None:
        for item in self.children:
            try:
                item.disabled = True
            except:
                pass
        await self.interaction.edit_original_message(view=self, embed=self.emb)


def setup(bot):
    bot.add_cog(Scheduler(bot))
