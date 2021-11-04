import json

import discord
from discord.ext import commands
from log_service import Logging
from database import cursor, db
from componets import get_str_msk_datetime, get_msk_datetime
from discord_components import Button, ButtonStyle

logger = Logging('ban')


class BanModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, user: discord.Member, *, reason: str = ''):
        if user == ctx.author:
            await ctx.send(':face_with_raised_eyebrow: `Ты чё, дурак что ли? Ты сам себя забанить решил? Молодец!`')
            return
        if reason == '':
            reason = 'Причина не указана'
        await user.ban(reason=reason)
        # cursor.execute(
        #     f'INSERT INTO bans(user,user_name,owner,reason,datetime) VALUES({user.id},"{user.display_name}",{ctx.author.id},"{reason}","{get_str_msk_datetime()}")')
        logger.audit(f'{ctx.author} забанил {user} по причине {reason}')
        # db.commit()
        await ctx.send(f':white_check_mark: `Пользователь {user.display_name} забанен!`')

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error.original, discord.errors.Forbidden):
            await ctx.send(f':sob: `Ой,я не могу забанить этого человека! Недостаточно прав!`')
        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('`:no_entry: У вас недостаточно прав для бана пользователя!`')

    # @commands.has_permissions(ban_members=True)
    # @commands.command()
    # async def unban(self, ctx, ban_id: int):
    #     cursor.execute(f'SELECT * FROM bans WHERE id = {ban_id} ')
    #     res = cursor.fetchone()
    #     if res is None:
    #         await ctx.send(f':x:`Бан с ID #{ban_id} не найден в БД`')
    #         return
    #     ban_id, user_id, user_name, owner, reason, timestamp = res
    #     current_name = discord.utils.get(ctx.guild.members, id=user_id)
    #     admin_name = discord.utils.get(ctx.guild.members, id=owner)
    #     comp = [[Button(label='Да', style=ButtonStyle.green),
    #              Button(label='Нет', style=ButtonStyle.green)]]
    #     embed = discord.Embed(title='Вы действительно хотите снять этот бан?', colour=discord.Colour.random(),
    #                           description='Вот немного информации о нём:')
    #     embed.add_field(name='ID:', value=str(ban_id))
    #     embed.add_field(name='ID пользователя:', value=str(user_id))
    #     embed.add_field(name='Имя на момент бана:', value=user_name)
    #     embed.add_field(name='Текущее имя:', value=current_name)
    #     embed.add_field(name='Забанил:', value=admin_name)
    #     embed.add_field(name='Причина', value=reason)
    #     embed.add_field(name='Дата:', value=timestamp)
    #     embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
    #     await ctx.send(embed=embed, components=comp)
    #     start_time = get_msk_datetime()
    #     while (get_msk_datetime().replace(tzinfo=None) - start_time).seconds < 120:
    #         confirm_response = await self.bot.wait_for('button_click')
    #         if confirm_response.author == ctx.message.author and confirm_response.component.label == 'Да':
    #             await confirm_response.respond(
    #                 content=f':ok_hand: Бан ID #{ban_id} будет снят!')
    #             await ctx.guild.unban(user_id)
    #             cursor.execute(f'DELETE FROM bans WHERE id = {ban_id}')
    #             db.commit()
    #         if confirm_response.author == ctx.message.author and confirm_response.component.label == 'Нет':
    #             await confirm_response.respond(content=':x: Действие отменено!')

    # @unban.error
    # async def unban_error(self, ctx, error):
    #     await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def unban(self, ctx, user_id: int):
        banned_users = await ctx.guild.bans()
        for banned_member in banned_users:
            if banned_member.user.id == user_id:
                user = banned_member.user
                await ctx.guild.unban(user)
                await ctx.send(f':ok_hand: Бан пользователя {banned_member.user.name} будет снят!')

    @unban.error
    async def unban_error(self, ctx, error):
        await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')


def setup(bot):
    bot.add_cog(BanModule(bot))
