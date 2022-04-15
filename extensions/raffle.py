import core
from permissions import admin_permission_required
from dt import *
import traceback
import json
import database
import disnake
from disnake.ext import commands
from dt import get_msk_datetime
import asyncio
import random
from core.bot_messages import Restorer


class Raffle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


def setup(bot: commands.Bot):
    bot.add_cog(Raffle(bot))
