import asyncio
import datetime

import discord.utils
from discord.ext import commands
import database
from modules.datetime import get_msk_datetime
from extensions.events import Events


class StartTask(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        Events.add_task(self.check_warns)

    async def check_warns(self):
        while True:
            warns = database.Warn.select()
            for warn in warns:
                expiration_time = warn.datetime + datetime.timedelta(days=warn.expiration)
                if expiration_time <= get_msk_datetime().replace(tzinfo=None):
                    user = warn.user_id
                    warn_id = warn.warn_id
                    guild_id = warn.guild_id
                    channel_id = database.Guild.get_or_none(database.Guild.guild_id == guild_id)
                    user = self.bot.get_user(user)
                    channel = self.bot.fetch_channel(channel_id)
                    database.Warn.delete().where(database.Warn.warn_id == warn.id)
                    if user is not None:
                        user = user.name
                    if channel is None:
                        return
                    await channel.send(f':grin: `С пользователя {user} снят варн №{warn_id} по истечении срока`')
            await asyncio.sleep(300)


def setup(bot):
    bot.add_cog(StartTask(bot))
