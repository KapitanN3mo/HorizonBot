import disnake
from disnake.ext import commands
from assets import emojis
import core
import database
import json


class GProperty:
    def __init__(self, inter,
                 parent_view):
        self.parent_view = parent_view
        self.name = 'g_base_property'
        self.editable = False
        self.inter = inter
        self.bot = core.Bot.get_bot()
        self.db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == self.inter.guild.id)
        self.edit_interface = None

    def out(self):
        pass

    def set(self, value) -> bool:
        pass

    def value(self):
        pass

    def __str__(self):
        return self.name


class GUserCount(GProperty):
    def __init__(self, inter, parent_view):
        super(GUserCount, self).__init__(inter, parent_view)
        self.name = 'Количество пользователей'

    def __str__(self):
        return self.out()

    def out(self):
        user_counter = 0
        bot_counter = 0
        for member in self.inter.guild.members:
            if member.bot:
                bot_counter += 1
            else:
                user_counter += 1
        return f'```👤:{user_counter} 🤖:{bot_counter}```'


class GAdmins(GProperty):
    def __init__(self, inter, parent_view):
        super(GAdmins, self).__init__(inter, parent_view)
        self.name = 'Администраторы'

    def out(self):
        return ' '.join([member.mention for member in self.inter.guild.members if self.check_admin(member)])

    @staticmethod
    def check_admin(member):
        return True if member.guild_permissions.administrator and not member.bot else False


class GAdminAccess(GProperty):
    def __init__(self, inter, parent_view):
        super(GAdminAccess, self).__init__(inter, parent_view)
        self.name = 'Доступ к админ. командам'

    def out(self):
        adm_access = []
        for user in json.loads(self.db_guild.admins):
            ds_user = self.bot.get_user(
                (database.User.get(database.User.user_db_id == user)).user_id)
            adm_access.append(ds_user.mention)
        return ''.join(adm_access) if adm_access else f'```{emojis.no_entry_unicode} Нет```'


class GPrivateVoices(GProperty):
    def __init__(self, inter, parent_view):
        super(GPrivateVoices, self).__init__(inter, parent_view)
        self.name = 'Приватные каналы'

    def out(self):
        if self.db_guild.private_voice is None:
            return f'```{emojis.no_entry_unicode} Выключены```'
        else:
            return f'```{emojis.white_check_mark_unicode} Включены```{self.bot.get_channel(self.db_guild.private_voice).mention}'


class GNotifyChannel(GProperty):
    def __init__(self, inter, parent_view):
        super(GNotifyChannel, self).__init__(inter, parent_view)
        self.name = 'Канал для уведомлений'
        self.editable = False

    def out(self):
        if self.db_guild.notify_channel is None:
            return f'```{emojis.no_entry_unicode} Нет```'
        else:
            return f'```{emojis.white_check_mark_unicode}Есть```{self.bot.get_channel(self.db_guild.notify_channel).mention}'


class GMinVoiceTime(GProperty):
    def __init__(self, inter, parent_view):
        super(GMinVoiceTime, self).__init__(inter, parent_view)
        self.editable = True
        self.name = 'Минимальное время в канале для начисления опыта'
        self.edit_data = {'data_type': int, 'limit': '1.2'}

    def set(self, value):
        try:
            self.db_guild.minimum_voice_time = value
            self.db_guild.save()
            return True
        except:
            return False

    def value(self):
        return str(self.db_guild.minimum_voice_time)

    def out(self):
        return '```' + str(self.db_guild.minimum_voice_time) + ' секунд```'


class GVoiceMultiplier(GProperty):
    def __init__(self, inter, parent_view):
        super(GVoiceMultiplier, self).__init__(inter, parent_view)
        self.name = 'Множитель для голосовых каналов'

    def out(self):
        return '```' + str(self.db_guild.xp_voice_multiplier) + '```'


class GTextMultiplier(GProperty):
    def __init__(self, inter, parent_view):
        super(GTextMultiplier, self).__init__(inter, parent_view)
        self.name = 'Множитель для текстовых каналов'

    def out(self):
        return '```' + str(self.db_guild.xp_message_multiplier) + '```'
