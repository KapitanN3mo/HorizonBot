import discord
from discord.ext import commands


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
        await ctx.send(f':white_check_mark: `Пользователь {user.display_name} забанен!`')
        ban_emb = discord.Embed(title=f'Вы забанены на сервере {ctx.guild.name}',
                                description=f'Администратор: {ctx.author.name}', colour=discord.Colour.red)

        await user.send(embed=ban_emb)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error.original, discord.errors.Forbidden):
            await ctx.send(f':sob: `Ой,я не могу забанить этого человека! Недостаточно прав!`')
        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('`:no_entry: У вас недостаточно прав для бана пользователя!`')

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def unban(self, ctx, user_id: int):
        banned_users = await ctx.guild.bans()
        for banned_member in banned_users:
            if banned_member.user.id == user_id:
                user = banned_member.user
                await ctx.guild.unban(user)
                await ctx.send(f':ok_hand: Бан пользователя {user.name} будет снят!')
                ban_emb = discord.Embed(title=f' Блокировка на сервере {ctx.guild.name} снята!',
                                        description=f'Администратор: {ctx.author.name}', colour=discord.Colour.red)

                await user.send(embed=ban_emb)

    @unban.error
    async def unban_error(self, ctx, error):
        await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')


def setup(bot):
    bot.add_cog(BanModule(bot))
