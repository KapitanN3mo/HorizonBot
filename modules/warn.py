import asyncio
import datetime
import json
from componets import get_str_msk_datetime, get_msk_datetime
from database import cursor, db
import discord
from discord.ext import commands


class WarnModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def warn(self, ctx: commands.Context, user: discord.User, reason: str, expiration: int):
        cursor.execute('SELECT MAX(id) FROM warns')
        max_id = cursor.fetchone()
        print(max_id)
        if max_id[0] is None:
            warn_id = 0
        else:
            warn_id = max_id[0] + 1
        warn_info = [warn_id, user.id, ctx.author.id, reason, get_str_msk_datetime(), expiration]
        cursor.execute('INSERT INTO warns VALUES(?,?,?,?,?,?)', warn_info)
        db.commit()
        cursor.execute(f'SELECT Count(*) FROM warns WHERE user = {user.id}')
        warns_count = cursor.fetchone()[0]
        embed = discord.Embed(title=f'Выдано предупреждение!', colour=discord.Colour.red())
        embed.add_field(name='Кому:', value=user.mention)
        embed.add_field(name='Причина:', value=reason)
        embed.add_field(name='Выдан:', value=ctx.author.mention)
        embed.add_field(name='Количество:', value=f'{warns_count}/3')
        expiration_time = (get_msk_datetime().replace(tzinfo=None) + datetime.timedelta(days=expiration)).strftime(
            '%Y-%m-%d-%H-%M')
        embed.add_field(name='Срок истечения:', value=expiration_time)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=get_str_msk_datetime())
        await ctx.send(embed=embed)
        if warns_count >= 3:
            embed = discord.Embed(title='Автоматический бан',
                                  description=f'Пользователь {user.name} ({user.mention}) был забанен, так как получил 3 варна!',
                                  colour=0x000000)
            member = discord.utils.get(ctx.guild.members, id=user.id)
            await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await member.ban(reason='Автоматический бан за 3 предупреждения')


def setup(bot):
    bot.add_cog(WarnModule(bot))
