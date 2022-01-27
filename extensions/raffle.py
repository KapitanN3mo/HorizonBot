import asyncio
import datetime
import json
import random
from modules.permissions import admin_permission_required
import discord
from discord.ext import commands
from modules.datetime import *
from modules.bot_messages import raffle


class Raffle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def create_raffle(self, ctx: commands.Context, channel: discord.TextChannel, *, data: str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            await ctx.send(":exclamation: `Ошибка в JSON аргументе!`")
            return
        try:
            date = datetime.datetime.strptime(data['date'], datetime_format)
            show_author = True if data['author'] in ['True', 'true'] else False
            text = data['text']
            winner_count = data['win_count']
            emoji = data['emoji']
        except KeyError:
            await ctx.send(":exclamation: `Недостаточно аргументов`")
            return
        except Exception as ex:
            await ctx.send(f":exclamation: `Неверные данные` Info:{ex}")
            return
        if date < get_msk_datetime():
            await ctx.send(":exclamation: `Неверное время`")
            return
        rf = raffle.RaffleMessage(self.bot, show_author, text, winner_count, emoji, date)
        await rf.send()


def setup(bot: commands.Bot):
    bot.add_cog(Raffle(bot))
