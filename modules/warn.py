import asyncio
import datetime
import json
from componets import get_str_msk_datetime, get_msk_datetime, datetime_format
from database import cursor, db
import discord
from discord.ext import commands


class WarnModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def auto_warn(self, channel: discord.TextChannel, user: discord.User, expiration: int, reason: str):
        cursor.execute('SELECT MAX(id) FROM warns')
        max_id = cursor.fetchone()
        print(max_id)
        if max_id[0] is None:
            warn_id = 0
        else:
            warn_id = max_id[0] + 1
        warn_info = [warn_id, user.id, user.id, reason, get_str_msk_datetime(), expiration]
        cursor.execute('INSERT INTO warns VALUES(?,?,?,?,?,?)', warn_info)
        db.commit()
        cursor.execute(f'SELECT Count(*) FROM warns WHERE user = {user.id}')
        warns_count = cursor.fetchone()[0]
        embed = discord.Embed(title=f'Выдано предупреждение!', colour=discord.Colour.red())
        embed.add_field(name='Кому:', value=user.mention)
        embed.add_field(name='Причина:', value=reason)
        embed.add_field(name='Выдан:', value=self.bot.user.mention)
        embed.add_field(name='Количество:', value=f'{warns_count}/3')
        embed.add_field(name='Срок истечения:', value=str(expiration))
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=get_str_msk_datetime())
        await channel.send(embed=embed)
        if warns_count >= 3:
            embed = discord.Embed(title='Автоматический бан',
                                  description=f'Пользователь {user.name} ({user.mention}) был забанен, так как получил 3 варна!',
                                  colour=0x000000)
            member = discord.utils.get(channel.guild.members, id=user.id)
            await channel.send(embed=embed)
            await asyncio.sleep(5)
            try:
                await member.ban(reason='Автоматический бан за 3 предупреждения')
            except discord.errors.Forbidden:
                await channel.send(f':sob: `Недостаточно прав! Не могу забанить {user.name}`')

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def warn(self, ctx: commands.Context, user: discord.User, expiration: int, *, reason: str):
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
        embed.add_field(name='Срок истечения:', value=str(expiration))
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
            try:
                await member.ban(reason='Автоматический бан за 3 предупреждения')
            except discord.errors.Forbidden:
                await ctx.send(f':sob: `Недостаточно прав! Не могу забанить {user.name}`')

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def get_warns(self, ctx: commands.Context, user: discord.User):
        cursor.execute(f'SELECT id,owner,datetime,expiration FROM warns WHERE user = {user.id}')
        result = cursor.fetchall()
        if not result:
            await ctx.send(':regional_indicator_n: :regional_indicator_o: `У пользователя не найдено предупреждений!`')
            return
        embed = discord.Embed(title=f'Предупрежденеия пользователя {user}', color=discord.Colour.random())
        for warn in result:
            warn_id, owner, issue_time, expiration = warn
            expiration_time = (datetime.datetime.strptime(issue_time, datetime_format) + datetime.timedelta(
                days=expiration) - get_msk_datetime().replace(tzinfo=None)).days
            owner = self.bot.get_user(owner)
            embed.add_field(name=f'Warn#{warn_id}',
                            value=f'Выдан {owner.name} {issue_time} на {expiration} дней. Истечение через {expiration_time}:',
                            inline=False)
        await ctx.send(embed=embed)

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def remove_warn(self, ctx: commands.Context, warn_id: int):
        try:
            cursor.execute(f'DELETE FROM warns WHERE id = {warn_id}')
            db.commit()
        except Exception as ex:
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {ex}`')
            return
        await ctx.send(':white_check_mark: `Если такой варн существовал, то он удалён!`')


def setup(bot):
    bot.add_cog(WarnModule(bot))
