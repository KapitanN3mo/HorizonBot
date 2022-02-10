import discord
from discord.ext import commands
from core.events import Events
from core.profile import ProfileModule
import database


class Messages(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        Events.connect_on_message(self.message_xp)

    async def message_xp(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel) or isinstance(message.channel, discord.GroupChannel):
            return
        member = discord.utils.get(message.guild.members, id=message.author.id)
        if member is None:
            return
        guild = message.guild
        db_guild = database.Guild.get_or_none(database.Guild.guild_id == guild.id)
        xp_multiplier = db_guild.xp_message_multiplier
        ProfileModule.update_xp(member, int(1 * xp_multiplier))
        ProfileModule.update_messages_count(message.author, 1)


def setup(bot):
    bot.add_cog(Messages(bot))
