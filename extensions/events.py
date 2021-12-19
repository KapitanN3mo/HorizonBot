import discord
from discord.ext import commands
from extensions import profile


class Events(commands.Cog):
    hooks = {}
    tasks = []

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        profile.ProfileModule.create_guild_profile(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        profile.ProfileModule.create_profile(member)

    @classmethod
    def connect_on_message(cls, hook):
        try:
            cls.hooks['on_message']
        except KeyError:
            cls.hooks['on_message'] = []
        finally:
            cls.hooks['on_message'].append(hook)

    @classmethod
    def connect_on_ready(cls, hook):
        try:
            cls.hooks['on_ready']
        except KeyError:
            cls.hooks['on_ready'] = []
        finally:
            cls.hooks['on_ready'].append(hook)

    @classmethod
    def add_task(cls, task):
        cls.tasks.append(task)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if 'on_message' in self.hooks:
            for hook in self.hooks['on_message']:
                self.bot.loop.create_task(hook(message))

    @commands.Cog.listener()
    async def on_ready(self):
        print('Бот готов, бан-хаммер блестит!')
        for task in self.tasks:
            self.bot.loop.create_task(task())
        if 'on_ready' in self.hooks:
            for hook in self.hooks['on_ready']:
                self.bot.loop.create_task(hook())


def setup(bot):
    bot.add_cog(Events(bot))