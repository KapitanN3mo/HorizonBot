import disnake
from disnake.ext import commands
import json
import datetime
import random
import math
import asyncio

from dt import get_msk_datetime
from permissions import admin_permission_required


class PollModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(PollModule(bot))
