import os
import importlib
import subprocess
import core
import dt
from permissions import *
from assets import emojis
import disnake
import memory_profiler


class ExecuteModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def ping(self, inter: disnake.CommandInteraction):
        """Посмотреть статус"""
        emb = disnake.Embed(title='🏓 PONG!', colour=disnake.Colour.green())
        work_time = dt.get_msk_datetime() - core.Bot.start_time
        work_seconds = work_time.seconds
        work_minutes = work_seconds // 60
        work_seconds -= work_minutes * 60
        work_hours = work_minutes // 60
        work_minutes -= work_hours * 60
        work_days = work_hours // 24
        work_hours -= work_days * 24
        emb.add_field(name='⌚Время работы',
                      value=f'```{str(work_days) + " дней " if work_time.days > 0 else ""}'
                            f'{str(work_hours) + " часов " if work_hours > 0 else ""}'
                            f'{str(work_minutes) + " минут " if work_minutes > 0 else ""}'
                            f'{str(work_seconds) + " секунд " if work_seconds > 0 else ""}```')
        emb.add_field(name='🎛 Задержка', value=f'```{str(self.bot.latency * 1000).split(".")[0]} ms```')
        emb.add_field(name='📊 Использование памяти', value=f'```{str(memory_profiler.memory_usage()[0])[:4]} Mb```')
        gr_info = core.Bot.get_garbage_info()
        emb.add_field(name='📦 Буфер задач',
                      value=f'```Последняя очистка: {(dt.get_msk_datetime() - gr_info["last_work"]).seconds} секунд назад\n'
                            f'Период очистки: {gr_info["delay"]} секунд\n'
                            f'Очищено задач: {gr_info["deleted_task_count"]}\n'
                            f'Текущее кол-во задач: {gr_info["work_task_count"]}```')
        emb.set_footer(text=f'Статус', icon_url=self.bot.user.display_avatar)
        emb.timestamp = dt.get_msk_datetime()
        await inter.send(embed=emb)

    @commands.slash_command()
    @developer_permission_required
    async def execute(self, inter: disnake.CommandInteraction):
        """Передаёт код Python на исполнение"""
        await inter.response.send_modal(modal=ExecuteModalWindow())

    @commands.slash_command()
    @developer_permission_required
    async def run_script(self, inter: disnake.CommandInteraction, script_name, *args):
        """Выполнить скрипт"""
        if script_name + '.py' in os.listdir('scripts'):
            script = importlib.import_module(f'scripts.{script_name}')
            script = script.Script(self.bot)
            self.bot.loop.create_task(script.run(inter, *args))
        else:
            await inter.send(f'{emojis.exclamation}`Скрипт не найден!`')

    @commands.slash_command()
    @developer_permission_required
    async def scripts(self, inter: disnake.CommandInteraction):
        """Показывает список установленных скриптов"""
        embed = disnake.Embed(title='Список установленных скриптов', colour=disnake.Colour(0x00FF9E))
        text = ''
        for script in os.listdir('scripts'):
            if script == '__init__.py' or script == '__pycache__':
                continue
            text += script.replace('.py', '') + '\n'
        embed.description = text
        await inter.send(embed=embed)


class ExecuteModalWindow(disnake.ui.Modal):
    def __init__(self):
        cmp = [
            disnake.ui.TextInput(
                label='Ведите ваш код',
                custom_id='code_input',
                style=disnake.TextInputStyle.long,
                required=True
            )
        ]
        super(ExecuteModalWindow, self).__init__(title='Python execute', components=cmp)

    async def callback(self, interaction: disnake.ModalInteraction, /) -> None:
        await interaction.response.defer()
        proc = subprocess.Popen(['python', '-c', interaction.text_values['code_input']], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if stdout.decode("utf-8"):
            await interaction.send(f'Ваш код выполнен!\n```{stdout.decode("utf-8")}```')
        elif stderr.decode("utf-8"):
            await interaction.send(f'Ошибка:\n```{stderr.decode("utf-8")}```')
        else:
            await interaction.send(f'{emojis.exclamation}`Нет результатов выполнения`')
        proc.kill()


def setup(bot):
    bot.add_cog(ExecuteModule(bot))
