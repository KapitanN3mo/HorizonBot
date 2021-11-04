import json
import discord
from discord.ext import commands
from database import cursor, db
from componets import config


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
        cursor.execute(f'SELECT sys_info FROM server_users WHERE id = {ctx.author.id}')
        res = cursor.fetchone()
        if res is None:
            print('User settings ошибка запроса в БД')
            await ctx.send('Ошибка')
            return
        sys_data = json.loads(res[0])
        sys_data['send_dm_voice'] = mode
        cursor.execute(f'UPDATE server_users SET sys_info = (?) WHERE id = {ctx.author.id}', (json.dumps(sys_data),))
        db.commit()
        await ctx.send(f':white_check_mark: `Настройка settings_voice_time_notify установлена на {mode}`')

    @settings_voice_time_notify.error
    async def settings_voice_time_notify_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':no_entry:`Неправильное использование!`')

        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')

    admin_role = int(config.get('Global', 'admin_role'))

    @commands.has_role(admin_role)
    @commands.command()
    async def settings_set(self, ctx, section, option, value):
        if config.has_section(section):
            if config.has_option(section, option):
                if option == 'token' and section == 'Global':
                    await ctx.send('`Я не знаю откуда ты об этом узнал, но нет.')
                    return
                config.set(section, option, value)
                config.commit()
                await ctx.send(f':white_check_mark:`Значение {section}.{option} установлено на {value}`')
            else:
                await ctx.send(f':exclamation: `Не найдена опция {option}`')
        else:
            await ctx.send(f':exclamation: `Не найдена секция {section}`')

    @commands.has_role(admin_role)
    @commands.command()
    async def settings_list(self, ctx):
        message = '```'
        for section in config.config.sections():
            message += f'{section}:\n'
            for option in config.config.options(section):
                if option == 'token':
                    continue
                value = config.get(section, option)
                message += f'--> {option} --> {value}\n'
        message += '```'
        await ctx.send(message)


def setup(bot):
    bot.add_cog(MembersCommands(bot))
