import asyncio
import datetime
import random
from extensions.events import Events
from assets.fun_assets.gif_url import *
from assets.fun_assets.phrases import *
import discord
from discord.ext import commands
from discord_components import *
from assets.fun_assets import feed
from assets.crussader import crusader

ave_maria_objects = []


class FunCommands(commands.Cog):
    _tasks = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def fry(self, ctx: commands.Context, user: discord.User, piece_count=10):
        if user.id == ctx.author.id:
            await ctx.send('Оооо да вы, месье, ценитель каннибализма! 🧐 ')
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
        while True:
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
            if current_pieces_count <= 0:
                break
        msg = await ctx.fetch_message(mes_id)
        await msg.edit(embed=discord.Embed(title=f'🔥 Жарим {user.name}',
                                           description="**Прогресс отжаривания:**\n" +
                                                       f"Всего сожрали!",
                                           colour=0xFF8F00))

    @commands.command()
    async def lock_voice(self, ctx, user: discord.User, state, channel: int):
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

    @commands.command()
    async def cookie(self, ctx: commands.Context, user: discord.User):
        emb = discord.Embed(title=' ', description=f'{user.mention} <_> держи печеньку от {ctx.author.mention}!',
                            colour=0xe1ad0c)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        emb.set_image(url=random.choice(cookie_gif))
        emb.set_footer(text=f'Печеньки с любовью от {self.bot.user.name}', icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=emb)

    @commands.command()
    async def hug(self, ctx: commands.Context, user: discord.User):
        if ctx.author.id in [0]:
            emb = discord.Embed(description='Вам запретили обниматься', colour=discord.Colour.red())
            emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=emb)
            return
        emb = discord.Embed(title='Обнимааааашкииии!',
                            description=f'{ctx.author.mention} стискивает в объятиях {user.mention}!', colour=0xe1ad0c)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        emb.set_image(url=random.choice(hug_gif))
        emb.set_footer(text=f'Провайдер обнимашек в ваше сердечко -  {self.bot.user.name}',
                       icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=emb)

    @commands.command()
    async def feed(self, ctx, user: discord.User):
        start_time = datetime.datetime.now()
        f = feed.Feed.get_feeds()
        labels = []
        for fd in f:
            labels.append(SelectOption(label=fd.name, value=fd.id, emoji=fd.emoji))
        mes = await ctx.send('Выберите угощение:', components=[Select(placeholder='Выбрать...', options=labels)])
        while True:
            try:
                selected = await self.bot.wait_for('select_option', timeout=60 * 60)
                if selected.user_id.id == ctx.author.id and selected.message.id == mes.id:
                    emb = discord.Embed(title='Прятного аппетита!', color=0x7FFFA0,
                                        description=f'{ctx.author.mention} прислал {user.mention} вкусняшку!')
                    emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                    emb.set_footer(text=f'Производитель самой свежей и вкусной еды -  {self.bot.user.name}',
                                   icon_url=self.bot.user.avatar_url)
                    await selected.respond(embed=emb, ephemeral=False)
                    await ctx.send(feed.Feed.get_feed_by_id(selected.values[0]).emoji)
                    break
                else:
                    continue
            except Exception as ex:
                print(ex)
                break

    @commands.command()
    async def ave_maria(self, ctx: commands.Context):
        emb = discord.Embed(title=' ',
                            description=f'{ctx.author.mention} созывает всех верных Ордену на Великий Крестовый Поход!!',
                            colour=0xe1ad0c)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        emb.set_image(url=random.choice(ave_maria))
        emb.set_footer(text=f'НА ИЕРУСАЛИМ!', icon_url=self.bot.user.avatar_url)
        crusader_team = crusader.CrusaderTeam()
        emb.add_field(name='Отряд:', value=crusader_team.get_string())
        crusader_message = await ctx.send(embed=emb)
        for emoji in [wr.emoji for wr in crusader_team.get_warriors_list()]:
            await crusader_message.add_reaction(emoji)
        crusader_message = await ctx.fetch_message(crusader_message.id)


    @commands.command()
    async def kill(self, ctx: commands.Context, user: discord.User):
        emb = discord.Embed(title=' ', description=f'{ctx.author.mention}{random.choice(kill_phrases)}{user.mention}',
                            colour=0xe1ad0c)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        emb.set_image(url=random.choice(kill_gif))
        emb.set_footer(text=f'Похоронное агенство - {self.bot.user.name}', icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=emb)


def setup(bot: commands.Bot):
    bot.add_cog(FunCommands(bot))