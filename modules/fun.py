import asyncio
import datetime

import discord
from discord.ext import commands


class FunCommands(commands.Cog):
    _tasks = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def fry(self, ctx: commands.Context, user: discord.User, piece_count=10):
        if user.id == ctx.author.id:
            await ctx.send('Оооо да вы, месье, ценитель канибализма! 🧐 ')
        if user == self.bot.user:
            await ctx.send('Не-не-не, я не вкусный! 🤖')
            return
        start_time = datetime.datetime.now()
        current_pieces_count = piece_count
        embed = discord.Embed(title=f'🔥 Жарим {user.name}',
                              description="**Прогресс отжаривания:**\n" + "<" + "=" + ">",
                              colour=0xFF8F00)
        msg = await ctx.send(embed=embed)
        for i in range(1, 11):
            embed = discord.Embed(title=f'🔥 Жарим {user.name}',
                                  description="**Прогресс отжаривания:**\n" + "<" + "=" * i + ">" + str(i * 10) + "%",
                                  colour=0xFF8F00)
            await msg.edit(embed=embed)
            await asyncio.sleep(1)
        embed = discord.Embed(title=f'🔥 Жарим {user.name}',
                              description="**Прогресс отжаривания:**\n" + f"Успешно отжарено! "
                                                                          f"Хотите кусочек? Осталось {current_pieces_count} 🍗",
                              colour=0xFF8F00)
        await msg.edit(embed=embed)
        await msg.add_reaction('🍗')
        mes_id = msg.id
        while current_pieces_count > 0:
            msg = await ctx.fetch_message(mes_id)
            if ((datetime.datetime.now() - start_time).seconds / 60) >= 10:
                await msg.edit(embed=discord.Embed(title=f'🔥 Жарим {user.name}',
                                                   description="**Прогресс отжаривания:**\n" +
                                                               f"Всё испортилось! 😕",
                                                   colour=0xFF8F00))
                return
            emojis = msg.reactions
            # print(emojis)
            react_count = None
            for emoji in emojis:
                if emoji.emoji == '🍗':
                    react_count = emoji.count
                    break
            if react_count is None:
                await ctx.send('Кто-то украл всю еду! Вот розьбiйник! 🤠')
                await msg.edit(embed=discord.Embed(title=f'🔥 Жарим {user.name}',
                                                   description="**Прогресс отжаривания:**\n" +
                                                               f"Всё украли! Расходимся! 😡",
                                                   colour=0xFF8F00))
                return
            current_pieces_count = piece_count + 1 - react_count
            embed = discord.Embed(title=f'🔥 Жарим {user.name}',
                                  description="**Прогресс отжаривания:**\n" +
                                              f"Хотите кусочек? Осталось {current_pieces_count} 🍗 ?",
                                  colour=0xFF8F00)
            await msg.edit(embed=embed)
            await asyncio.sleep(1)
        await msg.edit(title=f'🔥 Жарим {user.name}',
                       description="**Прогресс отжаривания:**\n" +
                                   f"Всего сожрали!",
                       colour=0xFF8F00)

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
                    del self._tasks[user.id]
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
