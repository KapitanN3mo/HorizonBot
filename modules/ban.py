import discord
from discord.ext import commands


class BanModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, user: discord.Member, *reason):
        if user == ctx.author:
            await ctx.send(':face_with_raised_eyebrow: `Ты чё, дурак что ли? Ты сам себя забанить решил? Молодец!`')
            return
        if reason == ():
            reas = 'Причина не указана'
        else:
            reas = ''
            for word in reason:
                print(word)
                reas += (word + ' ')
        await user.ban(reason=reas)
        await ctx.send(f'`:white_check_mark: Пользователь {user.mention} забанен!`')

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send(f':sob: `Ой,я не могу забанить этого человека!`')
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('`:no_entry: У вас недостаточно прав для бана пользователя!`')


def setup(bot):
    bot.add_cog(BanModule(bot))
