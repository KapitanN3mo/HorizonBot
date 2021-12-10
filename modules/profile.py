import math
import discord
from discord.ext import commands
import database
from componets import config, datetime_format
from modules.events import EventsModule
import datetime


class ProfileModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_hook = EventsModule(self.bot)
        print('subscribe')

    @commands.command()
    async def profile(self, ctx: commands.Context, user: discord.User or None = None):
        if user is None:
            user = ctx.author
        user_data = database.Users.select().where(database.Users.user_id == user.id).get_or_none()
        if user_data is None:
            await ctx.send('Это ваше первое сообщение! Ваш профиль создан!')
        else:
            member = discord.utils.get(ctx.guild.members, id=user.id)
            warns_count = len(database.Warns.select().where(database.Warns.user == user.id))
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

    @classmethod
    def update_xp(cls, user: discord.User, xp: int, reason: str = ''):
        user_data = database.Users.get_or_none(database.Users.user_id == user.id)
        if user_data is None:
            return
        else:
            current_xp_count = user_data.xp
        new_xp_count = current_xp_count + xp
        user_data.xp = new_xp_count
        user_data.save()
        print(f'Пользователю {user.name} добавлено {xp} опыта')


def setup(bot: commands.Bot):
    bot.add_cog(ProfileModule(bot))
