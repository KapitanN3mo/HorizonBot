import json

import discord
from discord.ext import commands

import core
import database
from core.bot_messages import Restorer
from core.events import Events
from modules.permissions import admin_permission_required


class RoleSender(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def role_message(self, ctx: commands.Context, channel: discord.TextChannel, *, data):
        author = ctx.author
        try:
            data = json.loads(data)
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
        rm = RoleMessage(self.bot, channel, data, author, ctx.guild)
        await rm.send()


class RoleMessage:
    def __init__(self, bot: commands.Bot, send_channel: discord.TextChannel = None, message_data=None,
                 author: discord.Member = None, guild: discord.Guild = None):

        self.bot = bot
        self.guild = guild
        self.send_channel = send_channel
        self.message_data = message_data
        self.author = author
        if self.message_data is None:
            self.variants = None
            self.color = None
            self.title = None
        else:
            self.variants: list = self.message_data['variants']
            self.color = self.message_data['color']
            self.title = self.message_data['title']
        self.message = None
        self.db_message = None

    async def start(self):
        Events.connect_on_raw_reaction_remove(self.update)
        Events.connect_on_raw_reaction_add(self.update)

    async def send(self):
        text = ''
        for ms in self.variants:
            ds_role = discord.utils.get(self.guild.roles, name=ms['name'])
            if ds_role is None:
                ds_role = await self.guild.create_role(name=ms['name'], reason='Система выдачи ролей')
            self.variants[self.variants.index(ms)]['id'] = ds_role.id
            print(self.variants)
            text += f'{ms["emoji"]} - {ds_role.mention}\n'
        emb = discord.Embed(title=self.title, description=text, colour=discord.Colour(int(self.color, 16)))
        message = await self.send_channel.send(embed=emb)
        self.message = message
        for ms in self.variants:
            await self.message.add_reaction(ms['emoji'])
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

    def clear_db(self):
        self.db_message.delete_instance()

    async def update(self, payload: discord.RawReactionActionEvent):
        if payload.channel_id == self.send_channel.id and payload.user_id != self.bot.user.id:
            if payload.event_type == 'REACTION_ADD':
                member: discord.Member = payload.member
                role = self.message.guild.get_role(self.find(emoji=payload.emoji)['id'])
                await member.add_roles(role, reason='Выдача роли по эмодзи')
            elif payload.event_type == 'REACTION_REMOVE':
                member = discord.utils.get(self.message.guild.members, id=payload.user_id)
                role = self.message.guild.get_role(self.find(emoji=payload.emoji)['id'])
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
    print('restore')
    bot = core.Bot.get_bot()
    db_message = db_message
    message_data = json.loads(db_message.message_data)
    guild = bot.get_guild(db_message.guild_id)
    send_channel = bot.get_channel(db_message.channel_id)
    if send_channel is None:
        return
    message = await send_channel.fetch_message(db_message.message_id)
    if message is None:
        return
    rm = RoleMessage(bot, send_channel, message_data, guild)
    rm.message = message
    bot.loop.create_task(rm.start())


def setup(bot: commands.Bot):
    bot.add_cog(RoleSender(bot))
