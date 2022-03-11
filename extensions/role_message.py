import asyncio
import json
import math
import sys

from assets import emojis
import disnake
from disnake.ext import commands
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
tasks = []
all_messages = []


class RoleSender(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def create_role_message(self, ctx: commands.Context, channel: disnake.TextChannel, *, data):
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
        iteration_count = math.ceil(len(variants) / max_role_in_message)
        step = 0
        for i in range(iteration_count):
            start = step * max_role_in_message
            stop = start + max_role_in_message
            if step + 1 == iteration_count:
                selected_items = variants[start:]
            else:
                selected_items = variants[start:stop]
            temp_data = data
            temp_data['variants'] = selected_items
            # self.bot.loop.create_task(
            await self.create_message_object(channel, temp_data, author, ctx.guild, init_channel=ctx.channel)
            step += 1

    async def create_message_object(self, channel, data, author, guild, init_channel):
        rm = RoleMessage()
        await rm.create(channel, author, guild, data, init_channel)
        await rm.send()


class RoleMessage:

    def __init__(self):
        self.bot = core.Bot.get_bot()
        self.guild = None
        self.send_channel = None
        self.author = None
        self.variants = None
        self.color = None
        self.title = None
        self.message = None
        self.db_message = None
        self.init_channel = None

    async def create(self, send_channel: disnake.TextChannel, author: disnake.Member, guild: disnake.Guild,
                     message_data, init_channel):
        self.send_channel = send_channel
        self.author = author
        self.guild = guild
        self.init_channel = init_channel
        await self.unpack_data(message_data)

    async def unpack_data(self, message_data):
        # ситуация с исключениями возможна только при создании экземпляра.
        try:
            self.color = message_data['color']
        except KeyError:
            self.color = disnake.Colour.default()
        try:
            self.title = message_data['title']
        except KeyError:
            self.title = 'Получение ролей'
        try:
            self.variants = message_data['variants']
            #print(self.variants)
        except KeyError:
            await self.init_channel.send(f'{emojis.no_entry}`Хм, а что выдавать-та?`')
            self.end()

    async def restore(self, send_channel, message_data, guild, db_message, message):
        self.send_channel = send_channel
        self.guild = guild
        self.db_message = db_message
        self.message = message
        await self.unpack_data(message_data)

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
                        return [False, disnake.utils.get(self.guild.roles, name=i)]
        return [True]

    async def check_repeat_emoji(self):
        for i in range(len(self.variants)):
            for j in range(i + 1, len(self.variants)):
                if self.variants[i]['emoji'] == self.variants[j]['emoji']:
                    return [False, self.variants[i]['emoji']]
        return [True]

    async def prepare_data(self, ms, counter):
        if 'color' in ms:
            color = disnake.Colour(ms['color'])
        else:
            color = disnake.Colour.default()
        self.variants[self.variants.index(ms)]['color'] = color.value
        ds_role: disnake.Role = disnake.utils.get(self.guild.roles, name=ms['name'])
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
        emb = disnake.Embed(title=self.title, description='',
                            colour=self.color)
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
        message_data = {
            'color': self.color,
            'title': self.title,
            'variants': self.variants
        }
        self.db_message = database.BotMessage.create(
            message_id=self.message.id,
            guild_id=self.message.guild.id,
            channel_id=self.send_channel.id,
            author_id=author,
            message_type='role',
            message_data=json.dumps(message_data),
        )
        await self.start()

    def end(self):
        self.db_message.delete_instance()
        Events.disconnect_events(self.update)
        # all_messages.pop(all_messages.index(self))

    async def is_real_role(self, role, payload):
        if role is None:
            try:
                guild: disnake.Guild = self.bot.get_guild(payload.guild_id)
                channel: disnake.TextChannel = guild.get_channel(channel_id=payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                emb = disnake.Embed(title=' ',
                                    description='Одна или несколько ролей из этого сообщения не найдены. Сообщение отключено',
                                    color=disnake.Colour.dark_gray())
                emb.set_footer(text=f'Время ошибки: {dt.get_str_msk_datetime()}',
                               icon_url=self.bot.user.avatar_url)
                await message.edit(embed=emb)
                await message.clear_reactions()
                await message.add_reaction(emoji=emojis.no_entry_unicode)
                return False
            except disnake.errors.NotFound:
                return False
            finally:
                self.end()
        else:
            return True

    async def update(self, payload: disnake.RawReactionActionEvent):
        if payload.message_id == self.message.id and payload.user_id != self.bot.user.id:
            if payload.event_type == 'REACTION_ADD':
                member: disnake.Member = payload.member
                try:
                    role = self.message.guild.get_role(self.find(emoji=payload.emoji)['id'])
                except TypeError:
                    return
                if await self.is_real_role(role, payload):
                    await member.add_roles(role, reason='Выдача роли по эмодзи')
            elif payload.event_type == 'REACTION_REMOVE':
                member = disnake.utils.get(self.message.guild.members, id=payload.user_id)
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
    except disnake.errors.NotFound:
        rm.end()
        return
    await rm.restore(send_channel, message_data, guild, db_message, message)
    future = bot.loop.create_task(rm.start())
    tasks.append(future)


def setup(bot: commands.Bot):
    bot.add_cog(RoleSender(bot))
