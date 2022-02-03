from discord.ext import commands
import database
from extensions.events import Events
from core import Bot
from links import restore_funcs


class Restorer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        Events.add_task(self.restore)

    async def restore(self):
        messages = database.BotMessage.select()
        for message in messages:
            print(f'restore -> {message.message_type}')
            c = restore_funcs[message.message_type](self.bot)
            self.bot.loop.create_task(c.restore(message))


def setup(bot: commands.Bot):
    bot.add_cog(Restorer(bot))
