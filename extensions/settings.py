import json
import discord
from discord.ext import commands
import database


class MembersCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def settings_voice_time_notify(self, ctx, mode: str):
        if mode in ['true', 'True']:
            mode = 'true'
        elif mode in ['False', 'false']:
            mode = 'false'
        else:
            raise commands.errors.MissingRequiredArgument('')
        user = database.User.get_or_none(database.User.user_id == ctx.author.id)
        if user is None:
            print('User settings ошибка запроса в БД')
            await ctx.send('Ошибка')
            return
        sys_data = json.loads(user.sys_info)
        sys_data['send_dm_voice'] = mode
        user.sys_info = json.dumps(sys_data)
        user.save()
        await ctx.send(f':white_check_mark: `Настройка settings_voice_time_notify установлена на {mode}`')

    @settings_voice_time_notify.error
    async def settings_voice_time_notify_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':no_entry:`Неправильное использование!`')

        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')


def setup(bot):
    bot.add_cog(MembersCommands(bot))
