import asyncio

import discord
from discord.ext import commands


class FunCommands(commands.Cog):
    _tasks = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def kill(self, ctx, user: discord.User, state, channel: int):
        if state in ['true', 'True']:
            state = True
        else:
            state = False
        if ctx.author.id != 357283670047850497:
            await ctx.send('Иди своей дорогой сталкер')
            return
        else:
            if state:
                if user.id in self._tasks:
                    await ctx.send('Уже')
                else:
                    task = self.bot.loop.create_task(self._kb(ctx, user, channel))
                    self._tasks[user.id] = task
            else:
                if user.id in self._tasks:
                    self._tasks[user.id].cancel()
                    await ctx.send('Пусть живёт')

    async def _kb(self, ctx: commands.Context, user: discord.User, m_ch_id):
        while True:
            print('check')
            guild = ctx.guild
            m_ch = discord.utils.get(guild.channels, id=m_ch_id)
            move_members = []
            for channel in guild.channels:
                print('channel')
                if isinstance(channel, discord.VoiceChannel):
                    for member in channel.members:
                        print('member')
                        if member.id == user.id:
                            if channel.id != m_ch_id:
                                move_members.append(member)
            for member in move_members:
                await member.move_to(m_ch)
            move_members.clear()

            await asyncio.sleep(1)


def setup(bot: commands.Bot):
    bot.add_cog(FunCommands(bot))
