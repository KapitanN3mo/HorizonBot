import discord
from discord.ext import commands
from modules import permissions
import database
import secrets
import string


class ApiCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @permissions.admin_permission_required
    async def api_create_account(self, ctx: commands.Context):
        user = ctx.author

        res = database.ApiUser.get_or_none(database.ApiUser.user_id == user.id)
        if res is None:
            alphabet = string.ascii_letters + string.digits
            key = ''.join(secrets.choice(alphabet) for i in range(10))
            api_user = database.ApiUser(user_id=user.id, user_name=user.name, user_type='discord_user', user_key=key)
            api_user.save()
            emb = discord.Embed(title='Учётная запись создана', description=f"Имя пользователя: {user.name}\n"
                                                                            f"Пароль: {key}\n"
                                                                            f"**Внимание! Запишите пароль! Это сообщение будт удалено через 5 минут!**",
                                color=discord.Color.green())
        else:
            emb = discord.Embed(title='У вас уже есть учётная запись!',description='Если вы не помните пароль, запросите новый!')


def setup(bot: commands.Bot):
    bot.add_cog(ApiCommands(bot))
