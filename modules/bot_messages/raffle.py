import json

import database
import discord
from discord.ext import commands
from modules.datetime import get_msk_datetime
import asyncio
import random


class RaffleMessage:
    def __init__(self, bot: commands.Bot, text, winner_count,
                 emoji, date, send_channel, info_channel, author):
        self.bot = bot
        self.string = 'raffle'
        self.show_author = False if author is None else True
        self.text = text
        self.winner_count = winner_count
        self.emoji = emoji
        self.date = date
        self.send_channel = send_channel
        self.info_channel = info_channel
        self.author = author

        self.message = None

    async def send(self):
        emb = discord.Embed(title="Внимание розыгрыш!", description=self.text,
                            colour=discord.Colour.random())
        emb.add_field(name='Количество победителей: ', value=self.winner_count)
        if self.show_author:
            emb.set_author(name=self.author.name, icon_url=self.author.avatar_url)
        emb.set_footer(text=f'Самые честные розыгрыши от HorizonBot!',
                       icon_url=self.bot.user.avatar_url)
        emb.add_field(name='Окончание в: ', value=f'{self.date.strftime("%m-%d-%H-%M")}')

        message = await self.send_channel.send(embed=emb)
        await message.add_reaction(emoji=self.emoji)
        self.message = message
        db_message = database.BotMessage()
        db_message.message_id = message.id
        db_message.guild_id = message.guild.id
        db_message.channel_id = message.channel.id
        db_message.owner_id = message.author.id
        db_message.message_type = self.string
        db_message.message_data = json.dumps({
            'winner_count': self.winner_count,
            'text': self.text,
            'emoji': self.emoji,
            'show_author': self.show_author,
            'info_channel': self.info_channel.id
        })
        db_message.save()
        await self.wait_time()

    async def restore(self, db_message: database.BotMessage):
        data = json.loads(db_message.message_data)
        self.text = data['text']
        self.show_author = data['show_author']
        self.emoji = data['emoji']
        self.winner_count = data['winner_count']

        self.info_channel = self.bot.get_channel(data['info_channel'])
        self.send_channel = self.bot.get_channel(db_message.channel_id)

        self.message = self.send_channel.fetch_message(db_message.message_id)
        if self.show_author:
            guild = self.message.guild
            self.author = discord.utils.get(guild.members, id=db_message.owner_id)

        self.bot.loop.create_task(self.wait_time())

    async def wait_time(self):
        sleep_time = (self.date - get_msk_datetime()).seconds
        if sleep_time < 0:
            await self.select_winners()
        await self.info_channel.send(f'Время ожидания: {sleep_time}')
        await asyncio.sleep(sleep_time)
        await self.select_winners()

    async def select_winners(self):
        message = await self.send_channel.fetch_message(id=self.message.id)
        reactions = message.reactions
        react = [r for r in reactions if r.emoji == self.emoji][0]
        winners = []
        participants = [participant for participant in await react.users().flatten() if
                        participant.id != self.bot.user.id]
        for i in range(self.winner_count):
            try:
                winner = random.choice(participants)
            except IndexError:
                await self.info_channel.send(
                    ":disappointed_relieved: `К сожалению, участников недостаточно! Розыгрыш отменён!`")
                return
            winners.append(winner)
            participants.remove(winner)
        guild_names = []
        for winner in winners:
            name = discord.utils.get(message.guild.members, id=winner.id)
            guild_names.append(name)
        emb = discord.Embed(title="Поздравляем победителя!",
                            colour=discord.Colour.magenta(), description=self.text)
        emb.add_field(name='Количество победителей: ', value=self.winner_count)
        if self.show_author:
            emb.set_author(name=self.author.name, icon_url=self.author.avatar_url)
        emb.set_footer(text=f'Самые честные розыгрыши от HorizonBot!',
                       icon_url=self.bot.user.avatar_url)
        emb.add_field(name='Окончание в: ', value=f'{self.date.strftime("%m-%d-%H-%M")}')
        emb.add_field(name='Победители:' if self.winner_count > 1 else "Победитель:",
                      value="\n".join(name.display_name for name in guild_names if isinstance(name, discord.Member)))
        emb.set_footer(text=f'Самые честные розыгрыши от HorizonBot!',
                       icon_url=self.bot.user.avatar_url)
        await self.info_channel.send(embed=emb)
        await message.edit(embed=emb)


