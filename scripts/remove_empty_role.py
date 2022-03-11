import disnake
from disnake.ext import commands
from assets import emojis


class Script:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def run(self, ctx: commands.Context, args=None):
        await ctx.send(f'{emojis.white_check_mark}`Скрипт выполняется`')
        counter = 0
        for role in ctx.guild.roles:
            bot_member = ctx.guild.get_member(self.bot.user.id)
            if role.name == '@everyone' or role in bot_member.roles:
                continue
            if role.color == disnake.Colour.default():
                counter += 1
                await role.delete(reason='Удалено при выполнении скрипта')
                # await ctx.send(f'`  |Удалена роль {role.name}`')
        await ctx.send(f'{emojis.white_check_mark}`Удалено {counter} ролей`')
