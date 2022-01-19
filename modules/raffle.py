import asyncio
import datetime
import json
import random

import discord
from discord.ext import commands

import componets
from componets import admin_role, admin_roles, datetime_format


class Raffle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # @commands.has_any_role(*admin_roles)
    @commands.command()
    async def create_raffle(self, ctx: commands.Context, channel: discord.TextChannel, *, data: str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            await ctx.send(":exclamation: `Ошибка в JSON аргументе!`")
            return
        try:
            date = datetime.datetime.strptime(data['date'], datetime_format)
            show_author = data['show_author']  # True if data['show_author'] in ['True', 'true'] else False
            text = data['text']
            winner_count = data['win_count']
            emoji = data['emoji']
        except KeyError as ex:
            await ctx.send(f":exclamation: `Недостаточно аргументов` {ex}")
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
        emb.set_footer(text=f'Самые честные розыгрыши от HorizonBot!',
                       icon_url=self.bot.user.avatar_url)
        emb.add_field(name='Окончание в: ', value=f'{date.strftime("%m-%d-%H-%M")}')
        message = await channel.send(embed=emb)
        await message.add_reaction(emoji=emoji)
        sleep_time = (date - datetime.datetime.now()).seconds
        await ctx.send(f'Время ожидания: {sleep_time}')
        await asyncio.sleep(sleep_time)
        message = await message.channel.fetch_message(id=message.id)
        reactions = message.reactions
        react = [r for r in reactions if r.emoji == emoji][0]
        winners = []
        participants = [participant for participant in await react.users().flatten() if
                        participant.id != self.bot.user.id]
        for i in range(winner_count):
            winner = random.choice(participants)
            winners.append(winner)
            participants.remove(winner)
        guild_names = []
        for winner in winners:
            name = discord.utils.get(ctx.guild.members, id=winner.id)
            guild_names.append(name)
        emb = discord.Embed(title="Поздравляем победителя!",
                            colour=discord.Colour.magenta())
        emb.add_field(name='Победители:' if winner_count > 1 else "Победитель:",
                      value="\n".join(name.display_name for name in guild_names if isinstance(name, discord.Member)))
        emb.set_footer(text=f'Самые честные розыгрыши от HorizonBot!',
                       icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=emb)


def setup(bot: commands.Bot):
    bot.add_cog(Raffle(bot))
