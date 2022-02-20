import asyncio
import json
import sys

from assets import emojis
import discord
from discord.ext import commands
from assets.fun_assets.number_converter import convert_number_to_emoji
import core
import database
from core.bot_messages import Restorer
from core.events import Events
from permissions import admin_permission_required
import dt

# структура JSON аргумента
#
#
#
#
#

max_role_in_message = 9


class RoleSender(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def create_role_message(self, ctx: commands.Context, channel: discord.TextChannel, *, data):
        author = ctx.author
        try:
            data: dict = json.loads(data)
        except json.JSONDecodeError:
            await ctx.send(':exclamation: `Ошибка в JSON аргументе`')
            return
        try:
            variants = data['variants']
            color = data['color']
            title = data['title']
        except KeyError:
            await ctx.send(':exclamation: `Недостаточно данных в JSON аргументе`')
            return
        selected_items = []
        counter = 0
        for ms in variants:
            selected_items.append(ms)
            counter += 1
            if counter == max_role_in_message:
                temp_data = data
                temp_data['variants'] = selected_items
                self.create_message_object(channel, temp_data, author, ctx.guild, init_channel=ctx.channel)
                counter = 0
                selected_items.clear()
        if counter != 0:
            temp_data = data
            temp_data['variants'] = selected_items

            self.create_message_object(channel, temp_data, author, ctx.guild, init_channel=ctx.channel)

    def create_message_object(self, channel, data, author, guild, init_channel):
        rm = RoleMessage()
        rm.create(channel, data, author, guild, init_channel)
        self.bot.loop.create_task(rm.send())


class RoleMessage:
    all_messages = []

    def __init__(self):
        self.all_messages.append(self)
        self.bot = core.Bot.get_bot()
        self.guild = None
        self.send_channel = None
        self.message_data = None
        self.author = None
        self.variants = None
        self.color = None
        self.title = None
        self.message = None
        self.db_message = None
        self.init_channel = None
        print(f'init id {id(self)}')

    async def create(self, send_channel: discord.TextChannel, author: discord.Member, guild: discord.Guild,
                     message_data, init_channel):
        self.send_channel = send_channel
        self.author = author
        self.guild = guild
        self.message_data = message_data
        self.init_channel = init_channel

    async def unpack_data(self, message_data):
        # ситуация с исключениями возможна только при создании экземпляра.
        try:
            self.color = message_data['color']
        except KeyError:
            self.color = discord.Colour.default()
        try:
            self.title = message_data['title']
        except KeyError:
            self.title = 'Получение ролей'
        try:
            self.variants = message_data['variants']
        except KeyError:
            await self.init_channel.send('')

    def restore(self, send_channel, message_data, guild, db_message, message):
        self.send_channel = send_channel
        self.message_data = message_data
        self.guild = guild
        self.db_message = db_message
        self.message = message
        self.variants = self.message_data['variants']
        self.color = self.message['color']
        self.title = self.message['title']

    async def start(self):
        Events.connect_on_raw_reaction_remove(self.update)
        Events.connect_on_raw_reaction_add(self.update)

    async def check_repeat_roles(self):
        messages = database.BotMessage.select().where(database.BotMessage.guild_id == self.guild.id)
        for mes in messages:
            db_data = json.loads(mes.message_data)
            db_roles = [d['name'] for d in db_data['variants']]
            c_roles = [d['name'] for d in self.variants]
            for i in db_roles:
                for j in c_roles:
                    if i == j:
                        return [False, discord.utils.get(self.guild.roles, name=i)]
        return [True]

    async def check_repeat_emoji(self):
        for i in range(len(self.variants)):
            for j in range(i + 1, len(self.variants)):
                if self.variants[i]['emoji'] == self.variants[j]['emoji']:
                    return [False, self.variants[i]['emoji']]
        return [True]

    async def prepare_data(self, ms, counter):
        if 'color' in ms:
            color = discord.Colour(ms['color'])
        else:
            color = discord.Colour.default()
        self.variants[self.variants.index(ms)]['color'] = color.value
        ds_role: discord.Role = discord.utils.get(self.guild.roles, name=ms['name'])
        if ds_role is None:
            ds_role = await self.guild.create_role(name=ms['name'], reason='Система выдачи ролей',
                                                   color=color)
        else:
            if ds_role.color != color:
                ds_role = await ds_role.edit(color=color)
        self.variants[self.variants.index(ms)]['id'] = ds_role.id
        if 'emoji' in ms:
            emoji = ms['emoji']
        else:
            emoji = convert_number_to_emoji(counter)
            self.variants[self.variants.index(ms)]['emoji'] = emoji
        return color, ds_role, emoji

    async def send(self):
        check_roles = await self.check_repeat_roles()
        if not check_roles[0]:
            await self.init_channel.send(
                f'{emojis.no_entry}`ВНИМАНИЕ! Ролью `{check_roles[1]} `уже управляет другое сообщение. Отправка отменена!`')
            return
        emb = discord.Embed(title=self.title, description='',
                            colour=discord.Colour(self.color))
        counter = 0
        for ms in self.variants:
            counter += 1
            color, ds_role, emoji = await self.prepare_data(ms, counter)
            emb.description += f'{emoji}-{ds_role.mention}\n'
        check_emoji = await self.check_repeat_emoji()
        if not check_emoji[0]:
            await self.init_channel.send(
                f'{emojis.no_entry}`Эмодзи {check_emoji[1]} используется несколько раз. Отправка отменена`'
            )
            return
        self.message = await self.send_channel.send(embed=emb)
        for ms in self.variants:
            await self.message.add_reaction(self.variants[self.variants.index(ms)]['emoji'])
        author = database.User.get(database.User.user_id == self.author.id, database.User.guild_id == self.guild.id)
        self.message_data['variants'] = self.variants
        self.db_message = database.BotMessage.create(
            message_id=self.message.id,
            guild_id=self.message.guild.id,
            channel_id=self.send_channel.id,
            author_id=author,
            message_type='role',
            message_data=json.dumps(self.message_data),
        )
        await self.start()

    def end(self):
        self.db_message.delete_instance()
        Events.disconnect_events(self.update)
        self.all_messages.pop(self.all_messages.index(self))
        self.alive = False

    async def is_real_role(self, role, payload):
        if role is None:
            try:
                guild: discord.Guild = self.bot.get_guild(payload.guild_id)
                channel: discord.TextChannel = guild.get_channel(channel_id=payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                emb = discord.Embed(title=' ',
                                    description='Одна или несколько ролей из этого сообщения не найдены. Сообщение отключено',
                                    color=discord.Colour.dark_gray())
                emb.set_footer(text=f'Время ошибки: {dt.get_str_msk_datetime()}',
                               icon_url=self.bot.user.avatar_url)
                await message.edit(embed=emb)
                await message.clear_reactions()
                await message.add_reaction(emoji=emojis.no_entry_unicode)
                return False
            except discord.errors.NotFound:
                return False
            finally:
                self.end()
        else:
            return True

    async def update(self, payload: discord.RawReactionActionEvent):
        if payload.message_id == self.message.id and payload.user_id != self.bot.user.id:
            if payload.event_type == 'REACTION_ADD':
                member: discord.Member = payload.member
                try:
                    role = self.message.guild.get_role(self.find(emoji=payload.emoji)['id'])
                except TypeError:
                    return
                if await self.is_real_role(role, payload):
                    await member.add_roles(role, reason='Выдача роли по эмодзи')
            elif payload.event_type == 'REACTION_REMOVE':
                member = discord.utils.get(self.message.guild.members, id=payload.user_id)
                try:
                    role = self.message.guild.get_role(self.find(emoji=payload.emoji)['id'])
                except TypeError:
                    return
                if await self.is_real_role(role, payload):
                    await member.remove_roles(role, reason='Удаление роли по эмодзи')

    def find(self, emoji=None, name=None):
        for ms in self.variants:
            if emoji:
                if ms['emoji'] == emoji.name:
                    return ms
            elif name:
                if ms['name'] == name:
                    return ms


@Restorer.reg_restore('role')
async def restore(db_message: database.BotMessage):
    bot = core.Bot.get_bot()
    db_message = db_message
    message_data = json.loads(db_message.message_data)
    guild = bot.get_guild(db_message.guild_id)
    send_channel = bot.get_channel(db_message.channel_id)
    rm = RoleMessage()
    if send_channel is None:
        rm.end()
        return
    try:
        message = await send_channel.fetch_message(db_message.message_id)
    except discord.errors.NotFound:
        rm.end()
        return
    rm.restore(send_channel, message_data, guild, db_message, message)
    bot.loop.create_task(rm.start())


def setup(bot: commands.Bot):
    bot.add_cog(RoleSender(bot))
