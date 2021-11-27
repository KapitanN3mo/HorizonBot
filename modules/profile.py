import math
import discord
from discord.ext import commands
from database import *
from componets import config,datetime_format
import json
from modules.events import EventsModule
import datetime


class ProfileModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_hook = EventsModule(self.bot)
        self.event_hook.subscribe('on_message', self.update_on_message)

    @commands.command()
    async def profile(self, ctx: commands.Context, user: discord.User or None = None):
        if user is None:
            user = ctx.author
        cursor.execute(sql.SQL(
            'SELECT message_count,xp,in_voice_time,status,warns,last_voice_time FROM server_users WHERE id = {user_id}').format(
            user_id=sql.Literal(user.id)
        ))
        result = cursor.fetchone()
        if result is None:
            await ctx.send('Это ваше первое сообщение! Ваш профиль создан!')

        else:
            member = discord.utils.get(ctx.guild.members, id=user.id)
            cursor.execute(
                sql.SQL('SELECT COUNT(*) FROM warns WHERE "user" = {user}').format(user=sql.Literal(user.id)))
            warn_result = cursor.fetchone()
            print(warn_result)
            warn_result = warn_result[0]
            message_count, xp, in_voice_time, status, warns, last_voice_time = result
            embed = discord.Embed(title=' ', colour=member.colour, description=user.mention)
            embed.add_field(name='Количество сообщений', value=message_count)
            embed.add_field(name='Очки опыта', value=xp)
            embed.add_field(name='Время в голосовом канале', value=f'{in_voice_time // 60} минут')
            join_datetime = member.joined_at
            embed.add_field(name='Появился на сервере', value=f'{join_datetime.strftime(datetime_format)} ({(datetime.datetime.now() - join_datetime).days} дней назад)')
            embed.add_field(name='Предупреждения', value=f'{warn_result}/3')
            embed.set_author(name=user.name, icon_url=user.avatar_url)
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)

    async def update_on_message(self, message: discord.Message):
        cursor.execute(sql.SQL('SELECT message_count,xp FROM server_users WHERE "id" = {us_id}').format(
            us_id=sql.Literal(message.author.id)))
        result = cursor.fetchone()
        if result is None:
            cursor.execute(
                sql.SQL(
                    'INSERT INTO server_users(id,message_count,xp,in_voice_time,status,warns,sys_info,last_voice_time)'
                    ' VALUES({id},{msg_count},{xp},{in_voice_time},{status},{warns},{sys_info},{last_voice_time})').format(
                    id=sql.Literal(message.author.id),
                    msg_count=sql.Literal(1),
                    xp=sql.Literal(1),
                    in_voice_time=sql.Literal(0),
                    status=sql.Literal('normal'),
                    warns=sql.Literal('{}'),
                    sys_info=sql.Literal(json.dumps({"send_dm_voice": "false"})),
                    last_voice_time=sql.Literal('none')
                ))
            db.commit()
        else:
            old_count = result[0]
            old_xp = result[1]
            old_count += 1
            xp_multiplier = int(config.get('Profile', 'xp_message_multiplier'))
            total_xp = int(xp_multiplier + old_xp)
            cursor.execute(sql.SQL(
                '''UPDATE server_users SET message_count = {old_count},xp = {total_xp} WHERE id = {author_id}''').format(
                old_count=sql.Literal(old_count),
                total_xp=sql.Literal(total_xp),
                author_id=sql.Literal(message.author.id)
            ))
            db.commit()


def setup(bot: commands.Bot):
    bot.add_cog(ProfileModule(bot))
