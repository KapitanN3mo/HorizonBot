import discord
from discord.ext import commands
from extensions.events import Events
from extensions.profile import ProfileModule


class Messages(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        Events.connect_on_message(self.message_xp)

    async def message_xp(self, message: discord.Message):
        ProfileModule.update_xp(message.author, 1)
        ProfileModule.update_messages_count(message.author, 1)


def setup(bot):
    bot.add_cog(Messages(bot))
