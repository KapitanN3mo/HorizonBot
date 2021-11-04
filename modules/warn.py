import asyncio
import datetime
import json
from componets import get_str_msk_datetime, get_msk_datetime, datetime_format
from database import cursor, db
import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle, Select


class WarnModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def auto_warn(self, channel: discord.TextChannel, user: discord.User, expiration: int, reason: str):
        cursor.execute('SELECT MAX(id) FROM warns')
        max_id = cursor.fetchone()
        if max_id[0] is None:
            warn_id = 0
        else:
            warn_id = max_id[0] + 1
        cursor.execute(
            f'INSERT INTO warns (user,owner,reason,datetime,expiration) '
            f'VALUES({user.id},{user.id},"{reason}","{get_str_msk_datetime()}",{expiration})')
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

        if max_id[0] is None:
            warn_id = 0
        else:
            warn_id = max_id[0] + 1
        cursor.execute(
            f'INSERT INTO warns (user,owner,reason,datetime,expiration) '
            f'VALUES({user.id},{ctx.author.id},"{reason}","{get_str_msk_datetime()}",{expiration})')
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
    async def warns(self, ctx: commands.Context, user):
        if user == 'all':
            cursor.execute(f'SELECT id,user,owner,datetime,expiration FROM warns')
        if isinstance(user, discord.User):
            cursor.execute(f'SELECT id,user,owner,datetime,expiration FROM warns WHERE user = {user.id}')
        result = cursor.fetchall()
        if not result:
            await ctx.send(':regional_indicator_n: :regional_indicator_o: `Не найдено предупреждений!`')
            return
        embed = discord.Embed(title=f'Предупрежденеия:', color=discord.Colour.random())
        for warn in result:
            warn_id, user_name, owner, issue_time, expiration = warn
            expiration_time = (datetime.datetime.strptime(issue_time, datetime_format) + datetime.timedelta(
                days=expiration) - get_msk_datetime().replace(tzinfo=None)).days
            owner = self.bot.get_user(owner)
            user_name = self.bot.get_user(user_name)
            if owner is not None:
                owner = owner.name
            if user_name is not None:
                user_name = user_name.name
            embed.add_field(name=f'Warn#{warn_id}',
                            value=f'Выдал {owner} -> {user_name} {issue_time} на {expiration} дней. Истечение через {expiration_time}:',
                            inline=False)
        await ctx.send(embed=embed)

    @warns.error
    async def warns_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':exclamation: `Необходимо указать пользователя.`')
        else:
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def remove_warn(self, ctx: commands.Context, user: discord.User, warn_id: int):
        cursor.execute(f'SELECT user FROM warns WHERE id={warn_id}')
        res = cursor.fetchone()
        if res is None:
            await ctx.send(f':x: `Такого варна не существует`')
            return
        if res[0] == user.id:
            cursor.execute(f'DELETE FROM warns WHERE id = {warn_id}')
            db.commit()
            await ctx.send(f':white_check_mark: `Варн №{warn_id} был удалён! Пользователь {user}`')

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def clear_warns(self, ctx: commands.Context, user: discord.User):
        comp = [[Button(label='Да', style=ButtonStyle.green), Button(label='Нет', style=ButtonStyle.red)]]
        await ctx.send(f':question: Вы действительно хотите очистить варны пользователя {user}', components=comp)
        start_time = get_msk_datetime().replace(tzinfo=None)
        while (get_msk_datetime().replace(tzinfo=None) - start_time).seconds < 120:
            confirm_response = await self.bot.wait_for('button_click')
            if confirm_response.author == ctx.message.author and confirm_response.component.label == 'Да':
                await confirm_response.respond(
                    content=f':ok_hand: Все предупреждения пользователя {user} будут удалены')
                cursor.execute(f'DELETE FROM warns WHERE user = {user.id}')
                db.commit()
                break
            elif confirm_response.author == ctx.message.author and confirm_response.component.label == 'Нет':
                await confirm_response.respond(content=f':x: Действие отменено')
                break


def setup(bot):
    bot.add_cog(WarnModule(bot))
