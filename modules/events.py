import discord
from discord.ext import commands


class EventsModule(commands.Cog):
    _subscribers = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @classmethod
    def subscribe(cls, method, hook):
        try:
            cls._subscribers[method].append(hook)
        except KeyError:
            cls._subscribers[method] = [hook]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return
        for hook in self._subscribers['on_message']:
            await hook(message)


def setup(bot):
    bot.add_cog(EventsModule(bot))
