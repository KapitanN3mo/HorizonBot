from discord.ext import commands
from assets import emojis
import core
import database
import json


class GUserCount:
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx

    def __str__(self):
        return self.out()

    def out(self):
        user_counter = 0
        bot_counter = 0
        for member in self.ctx.guild.members:
            if member.bot:
                bot_counter += 1
            else:
                user_counter += 1
        return f'```👤:{user_counter} 🤖:{bot_counter}```'


class GAdmins:
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx

    def out(self):
        return ' '.join([member.mention for member in self.ctx.guild.members if self.check_admin(member)])

    @staticmethod
    def check_admin(member):
        return True if member.guild_permissions.administrator and not member.bot else False


class GAdminAccess:
    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = core.Bot.get_bot()
        self.db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == self.ctx.guild.id)

    def out(self):
        adm_access = []
        for user in json.loads(self.db_guild.admins):
            ds_user = self.bot.get_user(
                (database.User.get(database.User.user_db_id == user)).user_id)
            adm_access.append(ds_user.mention)
        return ''.join(adm_access) if adm_access else f'```{emojis.no_entry_unicode} Нет```'


class GPrivateVoices:
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == self.ctx.guild.id)
        self.bot = core.Bot.get_bot()

    def out(self):
        if self.db_guild.private_voice is None:
            return f'```{emojis.no_entry_unicode} Выключены```'
        else:
            return f'```{emojis.white_check_mark_unicode} Включены```{self.bot.get_channel(self.db_guild.private_voice).mention}'


class GStatInfo:
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == self.ctx.guild.id)

    def out(self):
        stat_info = ''
        if self.db_guild.statistics_category is None:
            stat_info = f'```{emojis.no_entry_unicode} Выключена```'
        else:
            stat_info += '```'
            s_info = json.loads(self.db_guild.statistics_info)
            for stat in s_info:
                if s_info[stat]['mode']:
                    stat_info += f'{emojis.white_check_mark_unicode} {stat}\n'
                else:
                    stat_info += f'{emojis.no_entry_unicode} {stat}\n'
            stat_info += '```'
        return stat_info


class GNotifyChannel:
    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = core.Bot.get_bot()
        self.db_guild = database.Guild = database.Guild.get(database.Guild.guild_id == self.ctx.guild.id)

    def out(self):
        if self.db_guild.notify_channel is None:
            return f'```{emojis.no_entry_unicode} Нет```'
        else:
            return f'```{emojis.white_check_mark_unicode}Есть```{self.bot.get_channel(self.db_guild.notify_channel).mention}'

class GMinVoiceTime:
    def __init__(self,ctx:commands.Context):