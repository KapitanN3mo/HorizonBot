import json
import math
import discord
from discord.ext import commands
import database
from modules.datetime import datetime_format
import datetime
from modules import permissions
from core import Bot

default_sys_info = {
    'send_dm_voice': False
}


class ProfileModule(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def top(self, ctx: commands.Context):
        users = database.User.select().where(database.User.guild_id == ctx.guild.id) \
            .order_by(-database.User.xp) \
            .limit(20)
        emb = discord.Embed(title='', color=discord.Colour(0xD1C300), description='')
        emb.set_footer(text=f'Центр статистики имени {self.bot.user.name}', icon_url=self.bot.user.avatar_url)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        counter = 1
        for user in users:
            ds_user = self.bot.get_user(user.user_id)
            emb.description += f'**[{counter}]**:{ds_user.mention} - {user.xp} xp\n'
            counter += 1
        await ctx.send(embed=emb)

    @commands.command()
    async def profile(self, ctx: commands.Context, user: discord.Member or None = None):
        if user == self.bot.user:
            await ctx.send('🕵️ `Информация находиться под грифом "Перед прочтением съесть!".... Съел!`')
            return
        if user is None:
            user = ctx.author
        user_data = database.User.select().where(database.User.user_id == user.id,
                                                 database.User.guild_id == ctx.guild.id).get_or_none()
        if user_data is None:
            await ctx.send('Это ваше первое сообщение! Ваш профиль создан!')
        else:
            warns_count = len(
                database.Warn.select().where(database.Warn.user_id == user.id, database.Warn.guild_id == ctx.guild.id))
            embed = discord.Embed(title=' ', colour=user.colour, description=user.mention)
            embed.add_field(name='Количество сообщений', value=user_data.message_count)
            embed.add_field(name='Очки опыта', value=user_data.xp)
            embed.add_field(name='Время в голосовом канале', value=f'{user_data.in_voice_time // 60} минут')
            join_datetime = user.joined_at
            embed.add_field(name='Появился на сервере',
                            value=f'{join_datetime.strftime(datetime_format)} ({(datetime.datetime.now() - join_datetime).days} дней назад)')
            embed.add_field(name='Предупреждения', value=f'{warns_count}/3')
            embed.set_author(name=user.name, icon_url=user.avatar_url)
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)

    @classmethod
    def update_xp(cls, user: discord.Member, xp: int):
        bot = Bot.get_bot()
        try:
            if user.id == bot.user.id:
                return
        except AttributeError:
            return
        user_data = database.User.get_or_none(database.User.user_id == user.id,
                                              database.User.guild_id == user.guild.id)
        if user_data is None:
            cls.create_profile(user)
            user_data = database.User.get(database.User.user_id == user.id, database.User.guild_id == user.guild.id)
        current_xp_count = user_data.xp
        new_xp_count = current_xp_count + xp
        user_data.xp = new_xp_count
        user_data.save()

    @classmethod
    def update_messages_count(cls, user: discord.Member, msg: int):
        bot = Bot.get_bot()
        if user.id == bot.user.id:
            return
        try:
            user_data = database.User.get_or_none(database.User.user_id == user.id,
                                                  database.User.guild_id == user.guild.id)
        except AttributeError:
            return
        if user_data is None:
            cls.create_profile(user)
            user_data = database.User.get(database.User.user_id == user.id, database.User.guild_id == user.guild.id)
        current_msg_count = user_data.message_count
        new_msg_count = current_msg_count + msg
        user_data.message_count = new_msg_count
        user_data.save()

    @classmethod
    def create_profile(cls, user: discord.Member):
        try:
            database.User.insert(user_id=user.id,
                                 guild_id=user.guild.id,
                                 message_count=0,
                                 xp=0,
                                 in_voice_time=0,
                                 sys_info=json.dumps(default_sys_info),
                                 discord_name=user.name).execute()
            return 1
        except:
            return 0

    @classmethod
    def create_guild_profile(cls, guild: discord.Guild):
        try:
            database.Guild.insert(guild_id=guild.id,
                                  admins=json.dumps([])).execute()
            return 1
        except:
            return 0


def setup(bot: commands.Bot):
    bot.add_cog(ProfileModule(bot))
