import datetime
from disnake.ext import commands
import core
import database
import disnake

import dt


class ProfileProperty:
    def __init__(self, inter: disnake.CommandInteraction, user: disnake.Member):
        self.name = 'profile_base_property'
        self.editable = False
        self.inter = inter
        self.bot = core.Bot.get_bot()
        self.user: disnake.Member = user
        self.db_user: database.User = database.User.get(database.User.guild_id == self.inter.guild.id,
                                                        database.User.user_id == self.user.id)
        self.inline = True

    def out(self):
        pass

    def set(self):
        pass

    def __str__(self):
        return self.name


class MessageCount(ProfileProperty):
    def __init__(self, inter: disnake.CommandInteraction, user: disnake.Member):
        super(MessageCount, self).__init__(inter, user)
        self.name = 'Количество сообщений'

    def out(self):
        return f'```📨 {self.db_user.message_count}```'


class XPCount(ProfileProperty):
    def __init__(self, inter: disnake.CommandInteraction, user: disnake.Member):
        super(XPCount, self).__init__(inter, user)
        self.name = 'Очки опыта'

    def out(self):
        return f'```🏆 {self.db_user.xp}```'


class VoiceTime(ProfileProperty):
    def __init__(self, inter: disnake.CommandInteraction, user: disnake.Member):
        super(VoiceTime, self).__init__(inter, user)
        self.name = 'Время в голосовом канале'

    def out(self):
        return f'```🎧 {datetime.timedelta(seconds=self.db_user.in_voice_time)}```'


class JoinDatetime(ProfileProperty):
    def __init__(self, inter: disnake.CommandInteraction, user: disnake.Member):
        super(JoinDatetime, self).__init__(inter, user)
        self.name = 'Появился на сервере'

    def out(self):
        return f'```📅 {self.user.joined_at.strftime(dt.datetime_format)} ({(dt.get_msk_datetime() - self.user.joined_at.replace(tzinfo=None)).days} дней назад)```'


class WarnsCount(ProfileProperty):
    def __init__(self, inter: disnake.CommandInteraction, user: disnake.Member):
        super(WarnsCount, self).__init__(inter, user)
        self.name = 'Предупреждения'

    def out(self):
        warns = database.Warn.select().where(database.Warn.user_db_id == self.db_user.user_db_id,
                                             database.Warn.guild_id == self.inter.guild.id)
        return f'```🥊 {len(warns)}```'


class MarryPartner(ProfileProperty):
    def __init__(self, inter: disnake.CommandInteraction, user: disnake.Member):
        super(MarryPartner, self).__init__(inter, user)
        self.name = 'Пара'
        self.inline = False

    def out(self):
        partner = [database.MarryPartner.get_or_none(database.MarryPartner.user1 == self.db_user),
                   database.MarryPartner.get_or_none(database.MarryPartner.user2 == self.db_user)]
        if partner[0] is not None:
            partner = database.User.get(database.User.user_db_id == partner[0].user2)
            ds_partner: disnake.Member = self.inter.guild.get_member(partner.user_id)
            return f'❤ {ds_partner.mention}'
        elif partner[1] is not None:
            partner = database.User.get(database.User.user_db_id == partner[1].user1)
            ds_partner: disnake.Member = self.inter.guild.get_member(partner.user_id)
            return f'❤ {ds_partner.mention}'
        else:
            return f'🖤` Нет пары`'
