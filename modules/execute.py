import discord
from discord.ext import commands
import subprocess


class ExecuteModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def execute(self, ctx, *, code: str):
        if ctx.author.id in [357283670047850497, 232199554622029824]:
            proc = subprocess.Popen(['python', '-c', code], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            if stdout.decode("utf-8"):
                await ctx.send(f'Ваш код выполнен!\n```{stdout.decode("utf-8")}```')
            if stderr.decode("utf-8"):
                await ctx.send(f'Ошибка:\n```{stderr.decode("utf-8")}```')
            proc.kill()
        else:
            await ctx.send('Недостаточно прав!')


def setup(bot):
    bot.add_cog(ExecuteModule(bot))
