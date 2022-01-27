from discord.ext import commands
import database
from extensions.events import Events
from core import Bot


class Restorer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        Events.add_task(self.restore)

    async def restore(self):
        print('restore')
        messages = database.BotMessage.select()
        for message in messages:
            print(message.type)


def setup(bot: commands.Bot):
    bot.add_cog(Restorer(bot))
