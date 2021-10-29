import math
import discord
from discord.ext import commands
from database import cursor, db
from componets import config


class ProfileModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx: commands.Context, user: discord.User or None = None):
        if user is None:
            user = ctx.author
        cursor.execute(
            f'SELECT message_count,xp,in_voice_time,status,warns,last_voice_time FROM server_users WHERE id = {user.id}')
        result = cursor.fetchone()
        if result is None:
            await ctx.send('Это ваше первое сообщение! Ваш профиль создан!')

        else:
            message_count, xp, in_voice_time, status, warns, last_voice_time = result
            embed = discord.Embed(title=f'Профиль пользователя {user.name}', colour=discord.Colour.random())
            embed.add_field(name='Количество сообщений', value=message_count)
            embed.add_field(name='Очки опыта', value=xp)
            embed.add_field(name='Время в голосовом канале', value=f'{math.ceil(in_voice_time / 60)} минут')
            await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(ProfileModule(bot))
