from disnake.ext import commands
import database
from core.events import Events
from functools import wraps


class Restorer(commands.Cog):
    restore_funcs = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        Events.add_task(self.restore)

    async def restore(self):
        messages = database.BotMessage.select()
        for message in messages:
            #print(f'restore -> {message.message_type}')
            for hook in self.restore_funcs[message.message_type]:
                self.bot.loop.create_task(hook(message))


    @classmethod
    def reg_restore(cls, name='none'):
        def wrapper(func):
            try:
                cls.restore_funcs[name].append(func)
            except KeyError:
                cls.restore_funcs[name] = [func]

                @wraps(func)
                def decorator(*args, **kwargs):
                    return func(*args, **kwargs)

                return decorator

        return wrapper


def setup(bot: commands.Bot):
    bot.add_cog(Restorer(bot))
