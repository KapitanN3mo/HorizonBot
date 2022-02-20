import asyncio
import dt
import random
from assets.fun_assets.gif_url import *
from assets.fun_assets.phrases import *
from assets.fun_assets import fbi
import discord
from discord.ext import commands
from discord_components import *
from assets.fun_assets import feed
from assets import emojis
from assets.fun_assets import marry
from assets.fun_assets import gachi
from assets.fun_assets import sacrifice

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
            guild = ctx.guild
            m_ch = discord.utils.get(guild.channels, id=m_ch_id)
            move_members = []
            for channel in guild.channels:
                if isinstance(channel, discord.VoiceChannel):
                    for member in channel.members:
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
        emb = discord.Embed(description='Вам запретили обниматься', colour=discord.Colour.red())
        emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=emb)
        emb = discord.Embed(title='Обнимааааашкииии!',
                            description=f'{ctx.author.mention} стискивает в объятиях {user.mention}!', colour=0xe1ad0c)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        emb.set_image(url=random.choice(hug_gif))
        emb.set_footer(text=f'Провайдер обнимашек в ваше сердечко -  {self.bot.user.name}',
                       icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=emb)

    @commands.command()
    async def feed(self, ctx, user: discord.User):
        f = feed.Feed.get_feeds()
        labels = []
        for fd in f:
            labels.append(SelectOption(label=fd.name, value=fd.id, emoji=fd.emoji))
        mes = await ctx.send('Выберите угощение:', components=[Select(placeholder='Выбрать...', options=labels)])
        while True:
            try:
                selected = await self.bot.wait_for('select_option', timeout=60 * 60)
                if selected.user.id == ctx.author.id and selected.message.id == mes.id:
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
        await ctx.send(embed=emb)

    @commands.command()
    async def kill(self, ctx: commands.Context, user: discord.User):
        emb = discord.Embed(title=' ', description=f'{ctx.author.mention}{random.choice(kill_phrases)}{user.mention}',
                            colour=0xe1ad0c)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        emb.set_image(url=random.choice(kill_gif))
        emb.set_footer(text=f'Похоронное агенство - {self.bot.user.name}', icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=emb)

    @commands.command()
    async def fbi(self, ctx: commands.Context, user: discord.Member):
        emb = discord.Embed(title='Вызываем FBI', colour=discord.Colour(0xFF9700),
                            description=f'**СПЕЦНАЗ ЗА {user.mention} ПРИБУДЕТ ЧЕРЕЗ 10 СЕКУНД!**')
        emb.set_image(url=random.choice(fbi.urls))
        await ctx.send(embed=emb)
        webhook: discord.Webhook = await ctx.channel.create_webhook(name='fun_webhook',
                                                                    reason='Временный вебхук для спецназа!')
        await asyncio.sleep(10)
        for phase in fbi.phases:
            for i in range(fbi.phases[phase]['count']):
                agent = random.choice(fbi.agents)
                await webhook.send(content=random.choice(fbi.phases[phase]['phrases']),
                                   username=agent['name'],
                                   avatar_url=agent['avatar'])
                await asyncio.sleep(1)
        await webhook.delete()

    @commands.command()
    async def marry(self, ctx: commands.Context, first_partner: discord.Member, second_partner: discord.Member = None):
        if second_partner is None:
            description_head = f'{ctx.author.mention} зовёт под венец {first_partner.mention}\n' \
                               f'Вы согласны?\n Подтвердите согласие нажав на реакцию\n'
            emb = discord.Embed(title=' ',
                                description=description_head + f'{ctx.author.mention} - {emojis.question_unicode}\n'
                                                               f'{first_partner.mention} - {emojis.question_unicode}',
                                colour=discord.Colour(0xFF5DB4))
            emb.set_footer(text=f'Брачное агенство {self.bot.user.name}', icon_url=self.bot.user.avatar_url)
            emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            second_partner = ctx.author

        else:
            description_head = f'{ctx.author.mention} объявляет парой {first_partner.mention} и ' \
                               f'{second_partner.mention}\n' \
                               f'Вы согласны?\n Подтвердите согласие нажав на реакцию\n'
            emb = discord.Embed(title=' ',
                                description=description_head +
                                            f'{first_partner.mention} - {emojis.question_unicode}\n'
                                            f'{second_partner.mention} - {emojis.question_unicode}',
                                colour=discord.Colour(0xFF5DB4))
            emb.set_footer(text=f'Брачное агенство {self.bot.user.name}', icon_url=self.bot.user.avatar_url)
            emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        message = await ctx.send(embed=emb)
        await message.add_reaction(emoji=emojis.white_check_mark_unicode)
        await message.add_reaction(emoji=emojis.no_entry_unicode)
        start_time = datetime.datetime.now()
        confirmations = {first_partner: [None, emojis.question_unicode],
                         second_partner: [None, emojis.question_unicode]}
        while datetime.datetime.now() - start_time < datetime.timedelta(minutes=10):
            try:
                reaction, member = await self.bot.wait_for('reaction_add', timeout=10)
            except asyncio.TimeoutError:
                continue
            if member in confirmations and reaction.message.id == message.id:
                if reaction.emoji == emojis.white_check_mark_unicode:
                    confirmations[member][0] = True
                    confirmations[member][1] = emojis.white_check_mark_unicode
                elif reaction.emoji == emojis.no_entry_unicode:
                    confirmations[member][0] = False
                    confirmations[member][1] = emojis.no_entry_unicode
                    emb.description = description_head + f'{first_partner.mention} - {confirmations[first_partner][1]}\n' \
                                                         f'{second_partner.mention} - {confirmations[second_partner][1]}'
                    emb.title = 'Один из партнёров отказался!'
                    emb.colour = discord.Colour(0xFFA8D7)
                    await message.edit(embed=emb)
                    return
                else:
                    continue
            else:
                continue
            emb.description = description_head + f'{first_partner.mention} - {confirmations[first_partner][1]}\n' \
                                                 f'{second_partner.mention} - {confirmations[second_partner][1]}'
            if all([confirmations[partner][0] for partner in confirmations]):
                emb.title = f'Объявляю {first_partner.display_name} и {second_partner.display_name} парой!'
                emb.colour = discord.Colour(0xFF299B)
                emb.set_image(url=random.choice(marry.gif_urls))
                await message.edit(embed=emb)
                return
            await message.edit(embed=emb)
        emb.title = 'Любовь не вечна! Время ушло!'
        emb.description = ' '
        emb.colour = discord.Colour(0x7A007C)
        await message.edit(embed=emb)
        await message.clear_reactions()

    @commands.command()
    async def gachi(self, ctx: commands.Context):
        participants = [ctx.author]
        emb = discord.Embed(title='🎉 🎉 :male_sign: **ОБЪЯВЛЯЕМ ГАЧИ ВЕЧЕРИНКУ!!!** :male_sign: 🎉 🎉',
                            color=discord.Colour(0x1CFCF9),
                            description='Ну что fucking slave? Тоже хочешь на на нашу GayParty?\n'
                                        'Прожимай :male_sign: и становись на путь DungeonMaster-а!:\n'
                                        f'Участники:\n{ctx.author.mention}\n')
        emb.set_image(url=random.choice(gachi.urls))
        message = await ctx.send(embed=emb)
        await message.add_reaction('♂')
        start_time = datetime.datetime.now()
        while datetime.datetime.now() - start_time < datetime.timedelta(minutes=10):
            try:
                reaction, member = await self.bot.wait_for('reaction_add', timeout=10)
            except asyncio.TimeoutError:
                continue
            if reaction.message.id == message.id and not member in participants and not member.id == self.bot.user.id:
                emb.description += f'{member.mention}\n'
                await message.edit(embed=emb)

    @commands.command(aliases=['satan'])
    async def sacrifice_to_satan(self, ctx: commands.Context, victim: discord.Member):
        emb = discord.Embed(title='⛥**В ПЛАМЕНИ ПЕНТАГРАММЫ!!!**⛥', color=0xEB0037,
                            description=f'{ctx.author.mention} принёс {victim.mention} в жертву Сатане! СЛАВА САТАНЕ!')
        emb.set_image(url=random.choice(sacrifice.satan_url))
        await ctx.send(embed=emb)


def setup(bot: commands.Bot):
    bot.add_cog(FunCommands(bot))
