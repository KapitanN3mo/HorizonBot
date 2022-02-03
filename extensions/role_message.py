import discord
from discord.ext import commands
from modules.permissions import admin_permission_required
import database


class RoleSender(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def role_message(self):
        pass


class RoleMessage:
    def __init__(self, bot: commands.Bot, send_channel: discord.TextChannel = None, message_data=None,
                 author: discord.Member = None):
        self.bot = bot
        self.send_channel = send_channel
        self.message_data = message_data
        self.author = author

        self.variants = {}
        self.color = None
        self.title = None
        self.message = None
        self.db_message = None

    async def send(self):
        self.variants = self.message_data['variants']
        self.color = self.message_data['color']
        self.title = self.message_data['title']
        text = '\n'.join([f'{role} {info}' for role, info in self.variants.items()])
        emb = discord.Embed(title=self.title, description=text, colour=self.color)
        message = await self.send_channel.send(embed=emb)
        self.message = message
        self.db_message = database.BotMessage.create(
            message_id=self.message.id,
            guild_id=self.message.guild.id,
            channel_id=self.send_channel.id,
            author_id=self.author.id,
            message_type='role',
            message_data=self.message_data,

        )

    def update(self):
        pass


def setup(bot: commands.Bot):
    bot.add_cog()
