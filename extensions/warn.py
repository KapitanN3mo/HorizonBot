import asyncio
import datetime
import traceback
from core import events
import core
import database
import dt
from dt import get_str_msk_datetime, get_msk_datetime
import disnake
from disnake.ext import commands
from permissions import admin_permission_required
from assets import emojis


class InExcept(Exception):
    def __init__(self, context):
        self.context = context


class WarnModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_task = self.bot.loop.create_task(self.check_warn_expiration())

    async def auto_warn(self, channel: disnake.TextChannel, user: disnake.User, expiration: int, reason: str):
        warn = database.Warn()
        warn.user_id = user.id
        warn.owner_id = self.bot.user.id
        warn.reason = reason
        warn.datetime = get_msk_datetime()
        warn.expiration = expiration
        warn.save()
        warns_count = len(database.Warn.get(database.Warn.user_id == user.id))
        embed = disnake.Embed(title=f'Выдано предупреждение!', colour=disnake.Colour.red())
        embed.add_field(name='Кому:', value=user.mention)
        embed.add_field(name='Причина:', value=reason)
        embed.add_field(name='Выдан:', value=self.bot.user.mention)
        embed.add_field(name='Количество:', value=f'{warns_count}/3')
        embed.add_field(name='Срок истечения:', value=str(expiration))
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=get_str_msk_datetime())
        await channel.send(embed=embed)
        if warns_count >= 3:
            embed = disnake.Embed(title='Автоматический бан',
                                  description=f'Пользователь {user.name} ({user.mention}) был забанен, так как получил 3 варна!',
                                  colour=0x000000)
            member = disnake.utils.get(channel.guild.members, id=user.id)
            await channel.send(embed=embed)
            await asyncio.sleep(5)
            try:
                await member.ban(reason='Автоматический бан за 3 предупреждения')
            except disnake.errors.Forbidden:
                await channel.send(f':sob: `Недостаточно прав! Не могу забанить {user.name}`')

    @commands.slash_command()
    @admin_permission_required
    async def warn(self, inter: disnake.CommandInteraction, user: disnake.User, expiration: int, reason: str):
        try:
            db_user = database.User.get_or_none(database.User.user_id == user.id,
                                                database.User.guild_id == inter.guild.id)
            db_author = database.User.get_or_none(database.User.user_id == inter.author.id,
                                                  database.User.guild_id == inter.guild.id)
            if db_user is None:
                return
            warn = database.Warn()
            warn.guild_id = inter.guild.id
            warn.user_db_id = db_user.user_db_id
            warn.owner_id = db_author.user_db_id
            warn.reason = reason
            warn.datetime = get_msk_datetime()
            warn.expiration = expiration
            warn.save()
        except Exception as ex:
            print(traceback.print_exc())
        user_db = database.User.get_or_none(database.User.user_id == user.id, database.User.guild_id == inter.guild.id)
        warns_count = len(
            database.Warn.select().where(database.Warn.user_db_id == user_db, database.Warn.guild_id == inter.guild.id))
        embed = disnake.Embed(title=f'Выдано предупреждение!', colour=disnake.Colour.red())
        embed.add_field(name='Кому:', value=user.mention)
        embed.add_field(name='Причина:', value=reason)
        embed.add_field(name='Выдан:', value=inter.author.mention)
        embed.add_field(name='Количество:', value=f'{warns_count}/3')
        embed.add_field(name='Срок истечения:', value=str(expiration))
        embed.set_author(name=inter.author.name, icon_url=inter.author.display_avatar.url)
        embed.set_footer(text=get_str_msk_datetime())
        await inter.send(embed=embed)
        if warns_count >= 3:
            embed = disnake.Embed(title='Автоматический бан',
                                  description=f'Пользователь {user.name} ({user.mention}) был забанен, так как получил 3 варна!',
                                  colour=0x000000)
            member = disnake.utils.get(inter.guild.members, id=user.id)
            await inter.send(embed=embed)
            await asyncio.sleep(5)
            try:
                await member.ban(reason='Автоматический бан за 3 предупреждения')
            except disnake.errors.Forbidden:
                await inter.send(f':sob: `Недостаточно прав! Не могу забанить {user.name}`')

    @warn.error
    async def warns_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':exclamation:`Недостаточно аргументов!`')
        elif isinstance(error.original, InExcept):
            await ctx.send(error.original.context)
        else:
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')

    @commands.slash_command()
    async def warns(self, inter: disnake.CommandInteraction,
                    user: disnake.Member = commands.Param(lambda inter: inter.author)):
        """Посмотреть список предупреждений пользователя"""
        warn_list = [*database.Warn.select().where(database.Warn.guild_id == inter.guild_id,
                                                   database.Warn.user_db_id == database.User.get(
                                                       database.User.guild_id == inter.guild_id,
                                                       database.User.user_id == user.id))]
        if warn_list is None or warn_list == []:
            await inter.send(':regional_indicator_n: :regional_indicator_o: `Не найдено предупреждений!`')
            return
        embed = disnake.Embed(title=f'Предупрежденеия:', color=disnake.Colour.random())
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
                owner = owner.mention
            if user_name is not None:
                user_name = user_name.mention
            embed.add_field(name=f'Warn#{warn_id}',
                            value=f'Выдал {owner} -> {user_name} {issue_time}, на {expiration} дней. Истечение через {expiration_time.days}. Причина: {reason}',
                            inline=False)
        await inter.send(embed=embed)

    @commands.slash_command()
    async def all_warns(self, inter: disnake.CommandInteraction):
        """Посмотреть список всех предупреждений"""
        warn_list = [*database.Warn.select().where(database.Warn.guild_id == inter.guild_id)]
        if warn_list is None or warn_list == []:
            await inter.send(':regional_indicator_n: :regional_indicator_o: `Не найдено предупреждений!`')
            return
        embed = disnake.Embed(title=f'Предупрежденеия:', color=disnake.Colour.random())
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
                owner = owner.mention
            if user_name is not None:
                user_name = user_name.mention
            embed.add_field(name=f'Warn#{warn_id}',
                            value=f'Выдал {owner} -> {user_name} {issue_time}, на {expiration} дней. Истечение через {expiration_time.days}. Причина: {reason}',
                            inline=False)
        await inter.send(embed=embed)

    @warns.error
    async def warns_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':exclamation:`Необходимо указать пользователя.`')
        elif isinstance(error.original, InExcept):
            await ctx.send(error.original.context)
        else:
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')

    @commands.command()
    @admin_permission_required
    async def remove_warn(self, ctx: commands.Context, warn_id: int):
        warn = database.Warn.get_or_none(database.Warn.warn_id == warn_id, database.Warn.guild_id == ctx.guild.id)
        if warn is None:
            await ctx.send(f':x: `Такого варна не существует`')
        else:
            user = warn.user_db_id
            # print(warn.user_db_id)
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

    @commands.command()
    @admin_permission_required
    async def clear_warns(self, ctx: commands.Context, user: disnake.Member):
        view = ClearWarnView(ctx.author, user)
        await ctx.send(f':question: Вы действительно хотите очистить варны пользователя {user}', view=view)

    async def check_warn_expiration(self):
        await asyncio.sleep(10)
        while True:
            for guild in self.bot.guilds:
                db_guild: database.Guild = database.Guild.get_or_none(database.Guild.guild_id == guild.id)
                if db_guild is None:
                    database.Warn.delete().where(database.Warn.guild_id == guild.id).execute()
                warns = database.Warn.select().where(database.Warn.guild_id == guild.id)
                for warn in warns:
                    if (warn.datetime + datetime.timedelta(days=warn.expiration)) < dt.get_msk_datetime():
                        db_channel = guild.get_channel(db_guild.notify_channel)
                        channel = db_channel if db_channel is not None else guild.system_channel
                        user = guild.get_member(database.User.get(database.User.user_db_id == warn.user_db_id).user_id)
                        await channel.send(
                            f'{emojis.white_check_mark}`С пользователя `{user.mention}` снято предупреждение {warn.warn_id} за "{warn.reason}"`')
                        database.Warn.delete().where(database.Warn.warn_id == warn.warn_id).execute()
                    else:
                        continue
            await asyncio.sleep(600)


class ClearWarnView(disnake.ui.View):
    def __init__(self, owner: disnake.Member, user: disnake.Member):
        self.user = user
        self.owner = owner
        super().__init__()

    @disnake.ui.button(label='Очистить', style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if interaction.author.id == self.owner.id:
            await interaction.response.send_message(
                content=f':ok_hand: `Все предупреждения пользователя `{self.user.mention}` будут удалены`',
                ephemeral=False)
            user_db = database.User.get_or_none(database.User.user_id == self.user.id,
                                                database.User.guild_id == self.user.guild.id)
            query = database.Warn.delete().where(database.Warn.user_db_id == user_db.user_db_id,
                                                 database.Warn.guild_id == self.user.guild.id)
            query.execute()

            await self.disable_button(interaction)
            self.stop()

    @disnake.ui.button(label='Отмена', style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if interaction.author.id == self.owner.id:
            await interaction.response.send_message(content=f':x: `Действие отменено`')
            await self.disable_button(interaction)
            self.stop()

    async def disable_button(self, interaction: disnake.MessageInteraction):
        for button in self.children:
            if isinstance(button, disnake.ui.Button):
                button.disabled = True
        await interaction.message.edit(view=self)


def setup(bot):
    bot.add_cog(WarnModule(bot))
