import disnake
import peewee
from disnake.ext import commands
import datetime
from permissions import admin_permission_required
import core
import database
from assets import emojis

task_status = {'created': '🟡',
               'on_work': '📝',
               'complete': '✅',
               'canceled': '❌',
               'on_pause': '⏸'}
status_translate = {'created': 'Добавлена',
                    'on_work': 'В работе',
                    'complete': 'Готова',
                    'canceled': 'Отменена',
                    'on_pause': 'Приостановлена'}


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
        view = MainTaskView(inter.guild)
        view.interaction = inter
        await inter.send(view=view, embed=view.emb)

    @commands.slash_command()
    @admin_permission_required
    async def create_task(self, inter: disnake.CommandInteraction, block_name: str, executor: disnake.Member,
                          text: str):
        tasks = [*database.Task.select().where(
            database.Task.schedule == database.Schedule.get(database.Schedule.guild == inter.guild_id,
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
            author=database.User.get(database.User.guild_id == inter.guild_id, database.User.user_id == inter.author.id)
        ).execute()
        await inter.send('Ok', ephemeral=True)

    @create_task.autocomplete('block_name')
    async def block_name_autocomplete(self, inter: disnake.CommandInteraction, string: str):
        string = string.lower()
        return [block.name for block in database.Schedule.select().where(database.Schedule.guild == inter.guild_id) if
                string in block.name]


class MainTaskView(disnake.ui.View):
    def __init__(self, guild: disnake.Guild):
        super(MainTaskView, self).__init__()
        self.interaction = None
        self.guild = guild
        self.emb = disnake.Embed()

        self.next_button = disnake.ui.Button(style=disnake.ButtonStyle.blurple, emoji='▶', row=0)
        self.next_button.callback = self.next_button_callback
        self.back_button = disnake.ui.Button(style=disnake.ButtonStyle.blurple, emoji='◀', row=0)
        self.back_button.callback = self.back_button_callback
        self.update_button = disnake.ui.Button(style=disnake.ButtonStyle.green, emoji='🔁', row=0)
        self.update_button.callback = self.update_callback
        self.set_user_filter_button = disnake.ui.Button(style=disnake.ButtonStyle.green, emoji='👁', row=1)
        self.set_user_filter_button.callback = self.set_user_filter_callback
        self.reset_user_filter_button = disnake.ui.Button(style=disnake.ButtonStyle.gray, emoji='👁', row=1)
        self.reset_user_filter_button.callback = self.set_user_filter_callback
        self.edit_button = disnake.ui.Button(style=disnake.ButtonStyle.red, emoji='📝', row=1)
        self.edit_button.callback = self.edit_callback

        self.index = 0
        self.user_filter = None
        self.render()

    def gen_embed(self, schedules):
        emb = disnake.Embed(color=disnake.Color.red(), description='')
        if len(schedules) == 0:
            emb.description = "Планов нет"
        else:
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
                    if self.user_filter is not None and self.user_filter.id != executor.id:
                        continue
                    emb.description += f'```[{counter}] Задача для {executor.display_name}\n-> {task.text} [{task_status[task.status]}]\n```'
                    counter += 1
                if counter == 0:
                    emb.description = '```В этом плане нет задач для вас```'
            emb.add_field(name="Срок", value=f'```{(schedule.expiration - datetime.datetime.now()).days} дней```')
        self.emb = emb

    def render(self):
        schedules = [*database.Schedule.select().where(database.Schedule.guild == self.guild.id)]
        self.gen_embed(schedules)
        self.clear_items()
        if len(schedules) > 0:
            self.next_button.disabled = True
            self.back_button.disabled = True
            if 0 < self.index:
                self.back_button.disabled = False
            elif self.index < len(schedules) - 1:
                self.next_button.disabled = False
            self.add_item(self.back_button)
            self.add_item(self.next_button)
        self.add_item(self.update_button)
        if self.user_filter is None:
            self.add_item(self.set_user_filter_button)
        else:
            self.add_item(self.reset_user_filter_button)
        self.add_item(self.edit_button)

    async def set_user_filter_callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.user_filter = inter.author
        self.render()
        await inter.edit_original_message(view=self, embed=self.emb)

    async def reset_filter_callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.user_filter = None
        self.render()
        await inter.edit_original_message(view=self, embed=self.emb)

    async def edit_callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.user_filter = inter.author
        self.render()
        await inter.edit_original_message(view=self, embed=self.emb)

    async def update_callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.render()
        await inter.edit_original_message(view=self, embed=self.emb)

    async def next_button_callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.index += 1
        self.render()
        await inter.edit_original_message(view=self, embed=self.emb)
        self.interaction = inter

    async def back_button_callback(self, inter: disnake.MessageInteraction):
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


class TaskEditView(disnake.ui.View):
    def __init__(self, task: database.Task, inter: disnake.MessageInteraction):
        super(TaskEditView, self).__init__()
        self.task = task
        self.inter = inter
        self.guild = inter.guild
        self.embed = disnake.Embed()

    def gen_embed(self):
        emb = disnake.Embed()
        emb.set_author(name=self.inter.author.display_name, icon_url=self.inter.author.display_avatar)
        emb.description = f'```{self.task.text}```'
        emb.add_field(name='Статус', value=f'[{task_status[self.task.status]}] - {status_translate[self.task.status]}')
        emb.add_field(name='Исполнитель', value=self.guild.get_member(self.task.executor.user_id))
        self.embed = emb

    @disnake.ui.button(style=disnake.ButtonStyle.red, emoji=task_status['canceled'], row=0)
    async def set_canceled_status_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        pass

    @disnake.ui.button(style=disnake.ButtonStyle.gray, emoji=task_status['on_work'], row=0)
    async def set_on_work_status_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        pass

    @disnake.ui.button(style=disnake.ButtonStyle.gray, emoji=task_status['on_pause'], row=0)
    async def set_on_pause_status_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        pass

    @disnake.ui.button(style=disnake.ButtonStyle.green, emoji=task_status['complete'], row=0)
    async def set_complete_status_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        pass

    @disnake.ui.button(style=disnake.ButtonStyle.blurple, emoji='🤝', row=1)
    async def change_executor_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        pass

    @disnake.ui.button(style=disnake.ButtonStyle.blurple, emoji='📝', row=1)
    async def edit_task_text_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        pass

    def render(self):
        pass


class EditTaskDataModal(disnake.ui.Modal):
    def __init__(self, task: database.Task):
        components = [
            disnake.ui.TextInput(
                label='Задание',
                custom_id='task_text',
                style=disnake.TextInputStyle.long,
                value=task.text,
                required=True
            )
        ]
        super(EditTaskDataModal, self).__init__()


def setup(bot):
    bot.add_cog(Scheduler(bot))
