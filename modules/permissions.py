from functools import wraps
import discord
import database
from discord.ext import commands
from core import Bot
import json


def admin_permission_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        bot = Bot.get_bot()
        # print(args)
        ctx: commands.Context = args[1]
        user: discord.User = ctx.author
        guild: discord.Guild = ctx.guild
        member: discord.Member = discord.utils.get(guild.members, id=user.id)
        if member.guild_permissions.administrator:
            bot.loop.create_task(func(*args, *kwargs))
        else:
            db_guild = database.Guild.get_or_none(database.Guild.guild_id == guild.id)
            if user.id in json.loads(db_guild.admins):
                bot.loop.create_task(func(args, kwargs))
            else:
                await ctx.send(':no_entry: `у вас недостаточно прав для использования этой команды`')

    return wrapper
