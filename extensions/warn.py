import asyncio
import datetime
import json
import traceback
import database
from modules.datetime import get_str_msk_datetime, get_msk_datetime, datetime_format
from database import *
import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle, Select


class InExcept(Exception):
    def __init__(self, context):
        self.context = context


class WarnModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def auto_warn(self, channel: discord.TextChannel, user: discord.User, expiration: int, reason: str):
        warn = database.Warn()
        warn.user_id = user.id
        warn.owner_id = self.bot.user.id
        warn.reason = reason
        warn.datetime = get_msk_datetime()
        warn.expiration = expiration
        warn.save()
        warns_count = len(database.Warn.get(database.Warn.user_id == user.id))
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
        try:
            print(f'{type(expiration)} {expiration}')
            print(f'{type(reason)} {reason}')
            db_user = database.User.get_or_none(database.User.user_id == user.id,
                                                database.User.guild_id == ctx.guild.id)
            db_author = database.User.get_or_none(database.User.user_id == ctx.author.id,
                                                  database.User.guild_id == ctx.guild.id)
            if db_user is None:
                print('find error')
                return
            print(db_user.user_db_id, db_author.user_db_id)
            warn = database.Warn()
            warn.guild_id = ctx.guild.id
            warn.user_db_id = db_user.user_db_id
            warn.owner_id = db_author.user_db_id
            warn.reason = reason
            warn.datetime = get_msk_datetime()
            warn.expiration = expiration
            warn.save()
        except Exception as ex:
            print(traceback.print_exc())
        warns_count = len(
            database.Warn.select().where(database.Warn.user_id == user.id and database.Warn.guild_id == ctx.guild.id))
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

    @warn.error
    async def warns_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':exclamation:`Недостаточно аргументов!`')
        elif isinstance(error.original, InExcept):
            await ctx.send(error.original.context)
        else:
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')

    @commands.command()
    async def warns(self, ctx: commands.Context, user: str = ''):
        member = discord.utils.get(ctx.guild.members, id=ctx.author.id)
        permit = member.guild_permissions.kick_members
        if permit and user == 'all':
            print('all')
            warn_list = database.Warn.select().where(database.Warn.guild_id == ctx.guild.id)
        elif user != 'all' and user != '' and permit:
            print('user')
            user = user.replace('<', '').replace('>', '').replace('@', '').replace('!', '')
            try:
                user = int(user)
            except ValueError:
                raise InExcept(':exclamation:`Недопустимый пользователь`')
            user = self.bot.get_user(user)
            if user is None:
                raise InExcept(':exclamation:`Такого пользователя не существует`')
            user_db = database.User.get_or_none(database.User.user_id == user.id)
            warn_list = database.Warn.select().where(
                database.Warn.user_db_id == user_db.user_db_id and database.Warn.guild_id == ctx.guild.id)
        elif user == '':
            print('self')
            warn_list = database.Warn.select().where(
                database.Warn.user_db_id == ctx.author.id and database.Warn.guild_id == ctx.guild.id)
            print(type(warn_list))
        else:
            raise InExcept(
                ':exclamation:`Вы можете посмортеть только свои варны, для этого просто используйте {warns} без аргументов`')
        warn_list = [warn for warn in warn_list]
        if warn_list is None or warn_list == []:
            await ctx.send(':regional_indicator_n: :regional_indicator_o: `Не найдено предупреждений!`')
            return
        embed = discord.Embed(title=f'Предупрежденеия:', color=discord.Colour.random())
        for warn in warn_list:
            warn_id = warn.warn_id
            user_id = warn.user_db_id.user_id
            owner = warn.owner_id.user_id
            issue_time: datetime.datetime = warn.datetime
            expiration = warn.expiration
            expiration_time = issue_time + datetime.timedelta(days=expiration) - datetime.datetime.now()
            reason = warn.reason
            owner = self.bot.get_user(owner)
            user_name = self.bot.get_user(user_id)
            if owner is not None:
                owner = owner.name
            if user_name is not None:
                user_name = user_name.name
            embed.add_field(name=f'Warn#{warn_id}',
                            value=f'Выдал {owner} -> {user_name} {issue_time} на {expiration} дней. Истечение через {expiration_time.days} Причина: {reason}',
                            inline=False)
        await ctx.send(embed=embed)

    @warns.error
    async def warns_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':exclamation:`Необходимо указать пользователя.`')
        elif isinstance(error.original, InExcept):
            await ctx.send(error.original.context)
        else:
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def remove_warn(self, ctx: commands.Context, warn_id: int):
        warn = database.Warn.get_or_none(database.Warn.warn_id == warn_id)
        if warn is None:
            await ctx.send(f':x: `Такого варна не существует`')
        else:
            user = warn.user_id
            warn.delete_instance()
            await ctx.send(
                f':white_check_mark: `Варн №{warn_id} был удалён! Пользователь {self.bot.get_user(user.user_id).name}`')

    @remove_warn.error
    async def remove_warn_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':exclamation:`Использование: remove_warn {user} {warn id}.`')
        elif isinstance(error.original, InExcept):
            await ctx.send(error.original.context)
        else:
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def clear_warns(self, ctx: commands.Context, user: discord.User):
        comp = [[Button(label='Да', style=ButtonStyle.green), Button(label='Нет', style=ButtonStyle.red)]]
        await ctx.send(f':question: Вы действительно хотите очистить варны пользователя {user}', components=comp)
        start_time = get_msk_datetime().replace(tzinfo=None)
        confirm_response = None
        while (get_msk_datetime() - start_time).seconds < 120:
            try:
                confirm_response = await self.bot.wait_for('button_click', timeout=10)
            except TimeoutError:
                continue
            if confirm_response.author == ctx.message.author and confirm_response.component.label == 'Да':
                await confirm_response.respond(
                    content=f':ok_hand: Все предупреждения пользователя {user} будут удалены')
                query = database.Warn.delete().where(database.Warn.user_id == user.id)
                query.execute()
                break
            elif confirm_response.author == ctx.message.author and confirm_response.component.label == 'Нет':
                await confirm_response.respond(content=f':x: Действие отменено')
                break
        else:
            await confirm_response.respond(content=f':x: Истекло время ожидания')


def setup(bot):
    bot.add_cog(WarnModule(bot))
