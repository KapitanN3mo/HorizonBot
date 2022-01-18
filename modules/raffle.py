import datetime
import json

import discord
from discord.ext import commands

import componets
from componets import admin_role, admin_roles, datetime_format


class Raffle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_any_role(*admin_roles)
    @commands.command()
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
        if date < componets.get_msk_datetime():
            await ctx.send(":exclamation: `Неверное время`")
            return
        emb = discord.Embed(title="Внимание розыгрыш!", description=f'Победителей: {winner_count}',
                            colour=discord.Colour.random())
        emb.add_field(name='Информация', value=text)
        if show_author:
            emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        emb.set_footer(text=f'Окончание в: {date}')
        message = await channel.send(embed=emb)
        await message.add_reaction(emoji=emoji)


def setup(bot: commands.Bot):
    bot.add_cog(Raffle(bot))
