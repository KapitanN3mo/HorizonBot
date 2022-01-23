import discord
from discord.ext import commands
from modules import permissions


class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @permissions.admin_permission_required
    async def send(self, ctx, channel: discord.TextChannel, *, message: str):
        print(message)
        await channel.send(content=message)


def setup(bot: commands.Bot):
    bot.add_cog(BasicCommands(bot))
