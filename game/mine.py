import sqlite3
import discord
from discord.ext import commands


class GameMineModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def work(self, ctx):
        pass
