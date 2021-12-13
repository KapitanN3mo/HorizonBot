from functools import wraps
import discord
import database
from discord.ext import commands
from core import Bot


def admin_permission_require(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        bot = Bot.get_bot()
        ctx: commands.Context = args[0]
        user: discord.User = ctx.author
        guild: discord.Guild = ctx.guild
        member: discord.Member = discord.utils.get(guild.members, id=user.id)
        if member.guild_permissions.administrator:
            bot.loop.create_task((args, kwargs))
        else:
            admin_list = database.Guilds.get_or_none(database.Guilds.guild_id == guild.id)
            if user.id in admin_list:
                bot.loop.create_task(func(args, kwargs))
            else:
                raise commands.MissingPermissions(['administrator'])

    return wrapper
