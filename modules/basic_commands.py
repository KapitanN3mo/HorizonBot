import discord
from discord.ext import commands
from componets import admin_role


class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_role(admin_role)
    @commands.command()
    async def send(self, channel: discord.TextChannel, message: str):
        await channel.send(content=message)


def setup(bot: commands.Bot):
    bot.add_cog(BasicCommands(bot))
