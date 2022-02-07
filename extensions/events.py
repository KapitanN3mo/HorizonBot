import discord
from discord.ext import commands
from extensions import profile


class Events(commands.Cog):
    hooks = {}
    tasks = []

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @classmethod
    def connect_on_raw_reaction_add(cls, hook):
        try:
            cls.hooks['on_raw_reaction_add']
        except KeyError:
            cls.hooks['on_raw_reaction_add'] = []
        finally:
            cls.hooks['on_raw_reaction_add'].append(hook)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if 'on_raw_reaction_add' in self.hooks:
            for hook in self.hooks['on_raw_reaction_add']:
                self.bot.loop.create_task(hook(payload))

    @classmethod
    def connect_on_raw_reaction_remove(cls, hook):
        try:
            cls.hooks['on_raw_reaction_remove']
        except KeyError:
            cls.hooks['on_raw_reaction_remove'] = []
        finally:
            cls.hooks['on_raw_reaction_remove'].append(hook)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if 'on_raw_reaction_remove' in self.hooks:
            for hook in self.hooks['on_raw_reaction_remove']:
                self.bot.loop.create_task(hook(payload))

    @classmethod
    def connect_on_guild_join(cls, hook):
        try:
            cls.hooks['on_guild_join']
        except KeyError:
            cls.hooks['on_guild_join'] = []
        finally:
            cls.hooks['on_guild_join'].append(hook)

    @classmethod
    def connect_on_member_join(cls, hook):
        try:
            cls.hooks['on_member_join']
        except KeyError:
            cls.hooks['on_member_join'] = []
        finally:
            cls.hooks['on_member_join'].append(hook)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        profile.ProfileModule.create_guild_profile(guild)
        if 'on_guild_join' in self.hooks:
            for hook in self.hooks['on_guild_join']:
                self.bot.loop.create_task(hook(guild))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        profile.ProfileModule.create_profile(member)
        if 'on_member_join' in self.hooks:
            for hook in self.hooks['on_member_join']:
                self.bot.loop.create_task(hook(member))

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
