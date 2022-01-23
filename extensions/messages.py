import discord
from discord.ext import commands
from extensions.events import Events
from extensions.profile import ProfileModule


class Messages(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        Events.connect_on_message(self.message_xp)

    async def message_xp(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel) or isinstance(message.channel, discord.GroupChannel):
            return
        member = discord.utils.get(message.guild.members, id=message.author.id)
        if member is None:
            print(f'None member {message.author}')
        ProfileModule.update_xp(member, 1)
        ProfileModule.update_messages_count(message.author, 1)


def setup(bot):
    bot.add_cog(Messages(bot))
