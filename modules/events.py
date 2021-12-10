import discord
from discord.ext import commands
from modules.profile import ProfileModule


class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ProfileModule.update_xp(message.author, 1)


def setup(bot):
    bot.add_cog(Events(bot))
