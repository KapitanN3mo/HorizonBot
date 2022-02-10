import os
import importlib
import discord
from discord.ext import commands
import subprocess
from assets import emojis
from modules.permissions import *


class ExecuteModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @developer_permission_required
    async def execute(self, ctx, *, code: str):
        proc = subprocess.Popen(['python', '-c', code], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if stdout.decode("utf-8"):
            await ctx.send(f'Ваш код выполнен!\n```{stdout.decode("utf-8")}```')
        if stderr.decode("utf-8"):
            await ctx.send(f'Ошибка:\n```{stderr.decode("utf-8")}```')
        proc.kill()

    @commands.command()
    @developer_permission_required
    async def run_script(self, ctx: commands.Context, script_name, *args):
        if script_name + '.py' in os.listdir('scripts'):
            script = importlib.import_module(f'scripts.{script_name}')
            script = script.Script(self.bot)
            self.bot.loop.create_task(script.run(ctx, *args))
        else:
            await ctx.send(f'{emojis.exclamation}`Скрипт не найден!`')

    @commands.command()
    @developer_permission_required
    async def scripts(self, ctx: commands.Context):
        embed = discord.Embed(title='Список установленных скриптов', colour=discord.Colour(0x00FF9E))
        text = ''
        for script in os.listdir('scripts'):
            if script == '__init__.py' or script == '__pycache__':
                continue
            text += script.replace('.py', '') + '\n'
        embed.description = text
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ExecuteModule(bot))
