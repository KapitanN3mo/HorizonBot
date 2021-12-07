import discord
from discord.ext import commands
from componets import admin_role, admin_roles


class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_any_role(admin_roles)
    @commands.command()
    async def send(self, ctx, channel: discord.TextChannel, *, message: str):
        print(message)
        await channel.send(content=message)


def setup(bot: commands.Bot):
    bot.add_cog(BasicCommands(bot))
