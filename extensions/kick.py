import disnake
from disnake.ext import commands


class KickModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, user: disnake.Member, *reason):
        if user == ctx.author:
            await ctx.send(':face_with_raised_eyebrow: `Ты чё, дурак что ли? Ты сам себя выгнать решил? Молодец!`')
            return
        if reason == ():
            reas = 'Причина не указана'
        else:
            reas = ''
            for word in reason:
                reas += (word + ' ')
        await user.kick(reason=reas)
        await ctx.send(f'`:white_check_mark: Пользователь {user.mention} выгнан!`')

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send(f':sob: `Ой,я не могу выгнать этого человека!`')
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('`:no_entry: У вас недостаточно прав что-бы выгнать пользователя!`')


def setup(bot):
    bot.add_cog(KickModule(bot))
