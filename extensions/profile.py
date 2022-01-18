import json
import math
import discord
from discord.ext import commands
import database
from modules.datetime import datetime_format
import datetime
from modules import permissions

profile_sys_info = {
    'send_dm_voice_notify': False
}


class ProfileModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx: commands.Context, user: discord.User or None = None):
        if user is None:
            user = ctx.author
        user_data = database.User.select().where(database.User.user_id == user.id).get_or_none()
        if user_data is None:
            await ctx.send('Это ваше первое сообщение! Ваш профиль создан!')
        else:
            member = discord.utils.get(ctx.guild.members, id=user.id)
            warns_count = len(database.Warn.select().where(database.Warn.user_id == user.id))
            embed = discord.Embed(title=' ', colour=member.colour, description=user.mention)
            embed.add_field(name='Количество сообщений', value=user_data.message_count)
            embed.add_field(name='Очки опыта', value=user_data.xp)
            embed.add_field(name='Время в голосовом канале', value=f'{user_data.in_voice_time // 60} минут')
            join_datetime = member.joined_at
            embed.add_field(name='Появился на сервере',
                            value=f'{join_datetime.strftime(datetime_format)} ({(datetime.datetime.now() - join_datetime).days} дней назад)')
            embed.add_field(name='Предупреждения', value=f'{warns_count}/3')
            embed.set_author(name=user.name, icon_url=user.avatar_url)
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)

    @staticmethod
    def update_xp(user: discord.User, xp: int):
        user_data = database.User.get_or_none(database.User.user_id == user.id)
        if user_data is None:
            database.User.create(user_id=user.id,
                                 message_count=0,
                                 xp=0,
                                 in_voice_time=0,
                                 sys_info=json.dumps({'send_dm_voice': False}))
            user_data = database.User.get(database.User.user_id == user.id)
        current_xp_count = user_data.xp
        new_xp_count = current_xp_count + xp
        user_data.xp = new_xp_count
        user_data.save()

    @staticmethod
    def update_messages_count(user: discord.User, msg: int):
        user_data = database.User.get_or_none(database.User.user_id == user.id)
        if user_data is None:
            database.User.create(user_id=user.id,
                                 message_count=0,
                                 xp=0,
                                 in_voice_time=0,
                                 sys_info=json.dumps({'send_dm_voice': False}))
            user_data = database.User.get(database.User.user_id == user.id)
        current_msg_count = user_data.message_count
        new_msg_count = current_msg_count + msg
        user_data.message_count = new_msg_count
        user_data.save()

    @staticmethod
    def create_profile(user):
        try:
            database.User.insert(user_id=user.id,
                                 message_count=0,
                                 xp=0,
                                 in_voice_time=0,
                                 sys_info=json.dumps(profile_sys_info)).execute()
            return 1
        except:
            return 0

    @staticmethod
    def create_guild_profile(guild: discord.Guild):
        try:
            database.Guild.insert(guild_id=guild.id,
                                  admins=json.dumps([])).execute()
            return 1
        except:
            return 0


def setup(bot: commands.Bot):
    bot.add_cog(ProfileModule(bot))
