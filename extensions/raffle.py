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

    @commands.command()
    @admin_permission_required
    async def create_raffle(self, ctx: commands.Context, channel: disnake.TextChannel, *, data: str):
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
            print(traceback.print_exc())
            await ctx.send(":exclamation: `Недостаточно аргументов`")
            return
        except Exception as ex:
            await ctx.send(f":exclamation: `Неверные данные` Info:{ex}")
            return
        if date < get_msk_datetime():
            await ctx.send(":exclamation: `Неверное время`")
            return
        rf = RaffleMessage(self.bot, text, winner_count, emoji, date, channel, ctx.channel,
                           ctx.author if show_author else None)
        await rf.send()


class RaffleMessage:
    string = 'raffle'

    def __init__(self, bot: commands.Bot, text=None, winner_count=None,
                 emoji=None, date=None, send_channel=None, info_channel=None, author=None):
        self.bot = bot
        #print(author)
        self.show_author = False if author is None else True
        self.text = text
        self.winner_count = winner_count
        self.emoji = emoji
        self.date = date
        self.send_channel = send_channel
        self.info_channel = info_channel
        self.author = author
        self.message = None
        self.db_message = None

    async def send(self):
        emb = disnake.Embed(title="Внимание розыгрыш!", description=self.text,
                            colour=disnake.Colour.random())
        emb.add_field(name='Количество победителей: ', value=self.winner_count)
        if self.show_author:
            emb.set_author(name=self.author.name, icon_url=self.author.avatar_url)
        else:
            self.author = self.bot.user
        emb.set_footer(text=f'Самые честные розыгрыши от HorizonBot!',
                       icon_url=self.bot.user.avatar_url)
        emb.add_field(name='Окончание в: ', value=f'{self.date.strftime("%m-%d-%H-%M")}')

        message = await self.send_channel.send(embed=emb)
        await message.add_reaction(emoji=self.emoji)
        self.message = message
        db_user = database.User.get_or_none(database.User.user_id == self.author.id,
                                            database.User.guild_id == self.message.guild.id)
        db_message = database.BotMessage.create(
            message_id=message.id,
            guild_id=message.guild.id,
            channel_id=message.channel.id,
            author_id=db_user.user_db_id,
            message_type=self.string,
            message_data=json.dumps({
                'winner_count': self.winner_count,
                'text': self.text,
                'emoji': self.emoji,
                'show_author': self.show_author,
                'info_channel': self.info_channel.id,
                'end_date': self.date.strftime(datetime.datetime_format),
            })
        )
        self.db_message = db_message
        await self.wait_time()

    async def wait_time(self):
        sleep_time = (self.date - get_msk_datetime()).seconds
        if self.date < get_msk_datetime():
            await self.select_winners()
        else:
            await self.info_channel.send(f'Время ожидания: {sleep_time}')
            await asyncio.sleep(sleep_time)
            await self.select_winners()
        self.clear_db()

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
                emb = disnake.Embed(title='Розыгрыш отменён!', colour=disnake.Colour.dark_gold(),
                                    description='К сожалению, участников недостаточно!')
                emb.set_footer(text=f'Самые честные розыгрыши от HorizonBot!',
                               icon_url=self.bot.user.avatar_url)
                await message.edit(embed=emb)
                return
            winners.append(winner)
            participants.remove(winner)
        guild_names = []
        for winner in winners:
            name = disnake.utils.get(message.guild.members, id=winner.id)
            guild_names.append(name)
        emb = disnake.Embed(title="Поздравляем победителя!",
                            colour=disnake.Colour.magenta(), description=self.text)
        emb.add_field(name='Количество победителей: ', value=self.winner_count)
        if self.show_author:
            emb.set_author(name=self.author.name, icon_url=self.author.avatar_url)
        emb.set_footer(text=f'Самые честные розыгрыши от HorizonBot!',
                       icon_url=self.bot.user.avatar_url)
        emb.add_field(name='Окончание в: ', value=f'{self.date.strftime("%m-%d-%H-%M")}', inline=False)
        emb.add_field(name='Победители:' if self.winner_count > 1 else "Победитель:", inline=False,
                      value="\n".join(name.display_name for name in guild_names if isinstance(name, disnake.Member)))
        await self.info_channel.send(embed=emb)
        await message.edit(embed=emb)

    def clear_db(self):
        self.db_message.delete_instance()


@Restorer.reg_restore(name='raffle')
async def restore(db_message: database.BotMessage):
    bot = core.Bot.get_bot()
    data = json.loads(db_message.message_data)
    text = data['text']
    show_author = data['show_author']
    emoji = data['emoji']
    winner_count = data['winner_count']
    date = datetime.datetime.strptime(data['end_date'], datetime.datetime_format)
    info_channel = bot.get_channel(data['info_channel'])
    send_channel = bot.get_channel(db_message.channel_id)
    message = await send_channel.fetch_message(db_message.message_id)
    if show_author:
        guild = message.guild
        author = disnake.utils.get(guild.members, id=db_message.owner_id)
    else:
        author = None
    rf = RaffleMessage(bot, text, winner_count, emoji, date, send_channel, info_channel, author)
    rf.message = message
    rf.db_message = db_message
    bot.loop.create_task(rf.wait_time())


def setup(bot: commands.Bot):
    bot.add_cog(Raffle(bot))
