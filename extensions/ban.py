import disnake
from disnake.ext import commands


class BanModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_permissions(ban_members=True)
    @commands.slash_command()
    async def ban(self, inter: disnake.CommandInteraction, user: disnake.Member, reason: str = ''):
        if user == inter.author:
            await inter.send(':face_with_raised_eyebrow: `Ты чё, дурак что ли? Ты сам себя забанить решил? Молодец!`')
            return
        if reason == '':
            reason = 'Причина не указана'
        await user.ban(reason=reason)
        await inter.send(f':white_check_mark: `Пользователь {user.display_name} забанен!`')
        ban_emb = disnake.Embed(title=f'Вы забанены на сервере {inter.guild.name}',
                                description=f'Администратор: {inter.author.name}', colour=disnake.Colour.red())

        await user.send(embed=ban_emb)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error.original, disnake.errors.Forbidden):
            await ctx.send(f':sob: `Ой,я не могу забанить этого человека! Недостаточно прав!`')
        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send('`:no_entry: У вас недостаточно прав для бана пользователя!`')


def setup(bot):
    bot.add_cog(BanModule(bot))
