import discord
from discord.ext import commands
from assets import emojis
import core
import database
import json


class GProperty:
    def __init__(self, ctx: commands.Context):
        self.name = 'g_base_property'
        self.editable = False
        self.ctx = ctx
        self.bot = core.Bot.get_bot()
        self.db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == self.ctx.guild.id)

    def out(self):
        pass

    def set(self):
        pass

    def __str__(self):
        return self.name


class GUserCount(GProperty):
    def __init__(self, ctx):
        super(GUserCount, self).__init__(ctx)
        self.name = 'Количество пользователей'

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


class GAdmins(GProperty):
    def __init__(self, ctx):
        super(GAdmins, self).__init__(ctx)
        self.name = 'Администраторы'

    def out(self):
        return ' '.join([member.mention for member in self.ctx.guild.members if self.check_admin(member)])

    @staticmethod
    def check_admin(member):
        return True if member.guild_permissions.administrator and not member.bot else False


class GAdminAccess(GProperty):
    def __init__(self, ctx):
        super(GAdminAccess, self).__init__(ctx)
        self.name = 'Доступ к админ. командам'

    def out(self):
        adm_access = []
        for user in json.loads(self.db_guild.admins):
            ds_user = self.bot.get_user(
                (database.User.get(database.User.user_db_id == user)).user_id)
            adm_access.append(ds_user.mention)
        return ''.join(adm_access) if adm_access else f'```{emojis.no_entry_unicode} Нет```'


class GPrivateVoices(GProperty):
    def __init__(self, ctx):
        super(GPrivateVoices, self).__init__(ctx)
        self.name = 'Приватные каналы'

    def out(self):
        if self.db_guild.private_voice is None:
            return f'```{emojis.no_entry_unicode} Выключены```'
        else:
            return f'```{emojis.white_check_mark_unicode} Включены```{self.bot.get_channel(self.db_guild.private_voice).mention}'


class GStatInfo(GProperty):
    def __init__(self, ctx: commands.Context):
        super(GStatInfo, self).__init__(ctx)
        self.name = 'Статистика'

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


class GNotifyChannel(GProperty):
    def __init__(self, ctx):
        super(GNotifyChannel, self).__init__(ctx)
        self.name = 'Канал для уведомлений'
        self.editable = True

    def out(self):
        if self.db_guild.notify_channel is None:
            return f'```{emojis.no_entry_unicode} Нет```'
        else:
            return f'```{emojis.white_check_mark_unicode}Есть```{self.bot.get_channel(self.db_guild.notify_channel).mention}'

    async def set(self):
        channels = [channel for channel in self.ctx.guild.channels if isinstance(channel, discord.TextChannel)]
        await self.ctx.message.edit('\n'.join([channel.name for channel in channels]))


class GMinVoiceTime(GProperty):
    def __init__(self, ctx: commands.Context):
        super(GMinVoiceTime, self).__init__(ctx)
        self.editable = True
        self.name = 'Минимальное время в канале для начисления опыта'

    def out(self):
        return '```' + str(self.db_guild.minimum_voice_time) + ' секунд```'


class GVoiceMultiplier(GProperty):
    def __init__(self, ctx: commands.Context):
        super(GVoiceMultiplier, self).__init__(ctx)
        self.editable = True
        self.name = 'Множитель для голосовых каналов'

    def out(self):
        return '```' + str(self.db_guild.xp_voice_multiplier) + '```'


class GTextMultiplier(GProperty):
    def __init__(self, ctx):
        super(GTextMultiplier, self).__init__(ctx)
        self.name = 'Множитель для текстовых каналов'

    def out(self):
        return '```' + str(self.db_guild.xp_message_multiplier) + '```'
