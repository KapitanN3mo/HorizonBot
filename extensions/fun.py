import asyncio
import datetime
import random
import core
import database
from assets.fun_assets.gif_url import *
from assets.fun_assets.phrases import *
from assets.fun_assets import fbi
import disnake
from disnake.ext import commands
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
    async def fry(self, ctx: commands.Context, user: disnake.User, piece_count=10):
        if user.id == ctx.author.id:
            await ctx.send('Оооо да вы, месье, ценитель каннибализма! 🧐 ')
        if user == self.bot.user:
            await ctx.send('Не-не-не, я не вкусный! 🤖')
            return
        start_time = datetime.datetime.now()
        current_pieces_count = piece_count
        embed = disnake.Embed(title=f'🔥 Жарим {user.name}',
                              description="**Прогресс отжаривания:**\n" + "<" + "=" + ">",
                              colour=0xFF8F00)
        msg = await ctx.send(embed=embed)
        for i in range(1, 11):
            embed = disnake.Embed(title=f'🔥 Жарим {user.name}',
                                  description="**Прогресс отжаривания:**\n" + "<" + "=" * i + ">" + str(i * 10) + "%",
                                  colour=0xFF8F00)
            await msg.edit(embed=embed)
            await asyncio.sleep(1)
        embed = disnake.Embed(title=f'🔥 Жарим {user.name}',
                              description="**Прогресс отжаривания:**\n" + f"Успешно отжарено! "
                                                                          f"Хотите кусочек? Осталось {current_pieces_count} 🍗",
                              colour=0xFF8F00)
        await msg.edit(embed=embed)
        await msg.add_reaction('🍗')
        mes_id = msg.id
        while True:
            msg = await ctx.fetch_message(mes_id)
            if ((datetime.datetime.now() - start_time).seconds / 60) >= 10:
                await msg.edit(embed=disnake.Embed(title=f'🔥 Жарим {user.name}',
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
                await msg.edit(embed=disnake.Embed(title=f'🔥 Жарим {user.name}',
                                                   description="**Прогресс отжаривания:**\n" +
                                                               f"Всё украли! Расходимся! 😡",
                                                   colour=0xFF8F00))
                return
            current_pieces_count = piece_count + 1 - react_count
            embed = disnake.Embed(title=f'🔥 Жарим {user.name}',
                                  description="**Прогресс отжаривания:**\n" +
                                              f"Хотите кусочек? Осталось {current_pieces_count} 🍗 ?",
                                  colour=0xFF8F00)
            await msg.edit(embed=embed)
            await asyncio.sleep(1)
            if current_pieces_count <= 0:
                break
        msg = await ctx.fetch_message(mes_id)
        await msg.edit(embed=disnake.Embed(title=f'🔥 Жарим {user.name}',
                                           description="**Прогресс отжаривания:**\n" +
                                                       f"Всего сожрали!",
                                           colour=0xFF8F00))

    @commands.command()
    async def lock_voice(self, ctx, user: disnake.User, state, channel: int):
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

    async def _kb(self, ctx: commands.Context, user: disnake.User, m_ch_id):
        while True:
            guild = ctx.guild
            m_ch = disnake.utils.get(guild.channels, id=m_ch_id)
            move_members = []
            for channel in guild.channels:
                if isinstance(channel, disnake.VoiceChannel):
                    for member in channel.members:
                        if member.id == user.id:
                            if channel.id != m_ch_id:
                                move_members.append(member)
            for member in move_members:
                await member.move_to(m_ch)
            move_members.clear()
            await asyncio.sleep(1)

    @commands.command()
    async def cookie(self, ctx: commands.Context, user: disnake.User):
        emb = disnake.Embed(title=' ', description=f'{user.mention} <_> держи печеньку от {ctx.author.mention}!',
                            colour=0xe1ad0c)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        emb.set_image(url=random.choice(cookie_gif))
        emb.set_footer(text=f'Печеньки с любовью от {self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=emb)

    @commands.command()
    async def hug(self, ctx: commands.Context, user: disnake.User):
        emb = disnake.Embed(title='Обнимааааашкииии!',
                            description=f'{ctx.author.mention} стискивает в объятиях {user.mention}!', colour=0xe1ad0c)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        emb.set_image(url=random.choice(hug_gif))
        emb.set_footer(text=f'Провайдер обнимашек в ваше сердечко -  {self.bot.user.name}',
                       icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=emb)

    @commands.command()
    async def feed(self, ctx: commands.Context, user: disnake.Member):
        view = FeedView(ctx.author, user)
        await ctx.send('Выберете угощение!', view=view)

    @commands.command()
    async def ave_maria(self, ctx: commands.Context):
        emb = disnake.Embed(title=' ',
                            description=f'{ctx.author.mention} созывает всех верных Ордену на Великий Крестовый Поход!!',
                            colour=0xe1ad0c)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        emb.set_image(url=random.choice(ave_maria))
        emb.set_footer(text=f'НА ИЕРУСАЛИМ!', icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=emb)

    @commands.command()
    async def kill(self, ctx: commands.Context, user: disnake.User):
        emb = disnake.Embed(title=' ', description=f'{ctx.author.mention}{random.choice(kill_phrases)}{user.mention}',
                            colour=0xe1ad0c)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        emb.set_image(url=random.choice(kill_gif))
        emb.set_footer(text=f'Похоронное агенство - {self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=emb)

    @commands.command()
    async def fbi(self, ctx: commands.Context, user: disnake.Member):
        emb = disnake.Embed(title='Вызываем FBI', colour=disnake.Colour(0xFF9700),
                            description=f'**СПЕЦНАЗ ЗА {user.mention} ПРИБУДЕТ ЧЕРЕЗ 10 СЕКУНД!**')
        emb.set_image(url=random.choice(fbi.urls))
        await ctx.send(embed=emb)
        webhook: disnake.Webhook = await ctx.channel.create_webhook(name='fun_webhook',
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
    async def marry(self, ctx: commands.Context, first_partner: disnake.Member, second_partner: disnake.Member = None):
        if second_partner is None:
            description_head = f'{ctx.author.mention} зовёт под венец {first_partner.mention}\n' \
                               f'Вы согласны?\n Подтвердите согласие нажав на реакцию\n'
            emb = disnake.Embed(title=' ',
                                description=description_head + f'{ctx.author.mention} - {emojis.question_unicode}\n'
                                                               f'{first_partner.mention} - {emojis.question_unicode}',
                                colour=disnake.Colour(0xFF5DB4))
            emb.set_footer(text=f'Брачное агенство {self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
            emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            second_partner = ctx.author

        else:
            description_head = f'{ctx.author.mention} объявляет парой {first_partner.mention} и ' \
                               f'{second_partner.mention}\n' \
                               f'Вы согласны?\n Подтвердите согласие нажав на реакцию\n'
            emb = disnake.Embed(title=' ',
                                description=description_head +
                                            f'{first_partner.mention} - {emojis.question_unicode}\n'
                                            f'{second_partner.mention} - {emojis.question_unicode}',
                                colour=disnake.Colour(0xFF5DB4))
            emb.set_footer(text=f'Брачное агенство {self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
            emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        message = await ctx.send(embed=emb)
        first_partner_db = database.User.get(database.User.user_id == first_partner.id,
                                             database.User.guild_id == first_partner.guild.id)
        second_partner_db = database.User.get(database.User.user_id == second_partner.id,
                                              database.User.guild_id == second_partner.guild.id)
        first_partner_check = database.MarryPartner.get_or_none(
            database.MarryPartner.user1 == first_partner_db) or database.MarryPartner.get_or_none(
            database.MarryPartner.user2 == first_partner_db)
        second_partner_check = database.MarryPartner.get_or_none(
            database.MarryPartner.user1 == second_partner_db) or database.MarryPartner.get_or_none(
            database.MarryPartner.user2 == second_partner_db)
        check_result = [first_partner_check, second_partner_check]
        if any(check_result):
            emb.title = f'У {first_partner.display_name if check_result[0] is not None else second_partner.display_name} уже есть пара!'
            emb.description = 'Невозможно создать пару! Сначала необходимо разорвать старую!'
            await message.edit(embed=emb)
            return
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
                    emb.colour = disnake.Colour(0xFFA8D7)
                    emb.description = ''
                    await message.edit(embed=emb)
                    await message.clear_reactions()
                    return
                else:
                    continue
            else:
                continue
            emb.description = description_head + f'{first_partner.mention} - {confirmations[first_partner][1]}\n' \
                                                 f'{second_partner.mention} - {confirmations[second_partner][1]}'
            if all([confirmations[partner][0] for partner in confirmations]):
                database.MarryPartner.insert(user1=first_partner_db, user2=second_partner_db).execute()
                emb.title = f'Объявляю {first_partner.display_name} и {second_partner.display_name} парой!'
                emb.colour = disnake.Colour(0xFF299B)
                emb.set_image(url=random.choice(marry.gif_urls))
                await message.edit(embed=emb)
            await message.edit(embed=emb)
        emb.title = 'Любовь не вечна! Время ушло!'
        emb.description = ' '
        emb.colour = disnake.Colour(0x7A007C)
        await message.edit(embed=emb)
        await message.clear_reactions()

    @commands.command()
    async def divorce(self, ctx: commands.Context, user: disnake.Member):
        first_partner = ctx.author
        second_partner = user
        first_partner_db = database.User.get(database.User.user_id == first_partner.id,
                                             database.User.guild_id == first_partner.guild.id)
        second_partner_db = database.User.get(database.User.user_id == second_partner.id,
                                              database.User.guild_id == second_partner.guild.id)
        marry_db = database.MarryPartner.get_or_none(database.MarryPartner.user1 == first_partner_db,
                                                     database.MarryPartner.user2 == second_partner_db) or database.MarryPartner.get_or_none(
            database.MarryPartner.user1 == second_partner_db, database.MarryPartner.user2 == first_partner_db)
        emb = disnake.Embed(title='Развод', color=disnake.Colour(0x850028))
        emb.set_footer(text='Агенство бракоразводных процессов', icon_url=self.bot.user.display_avatar.url)
        if marry_db is None:
            emb.description = f'Пара {first_partner.mention} и {second_partner.mention} не найдена!'
        else:
            emb.description = f'Пара {first_partner.mention} и {second_partner.mention} разорвана!'
            marry_db.delete_instance()
        await ctx.send(embed=emb)

    @commands.command()
    async def gachi(self, ctx: commands.Context):
        participants = [ctx.author]
        emb = disnake.Embed(title='🎉 🎉 :male_sign: **ОБЪЯВЛЯЕМ ГАЧИ ВЕЧЕРИНКУ!!!** :male_sign: 🎉 🎉',
                            color=disnake.Colour(0x1CFCF9),
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
    async def sacrifice_to_satan(self, ctx: commands.Context, victim: disnake.Member):
        emb = disnake.Embed(title='⛥**В ПЛАМЕНИ ПЕНТАГРАММЫ!!!**⛥', color=0xEB0037,
                            description=f'{ctx.author.mention} принёс {victim.mention} в жертву Сатане! СЛАВА САТАНЕ!')
        emb.set_image(url=random.choice(sacrifice.satan_url))
        await ctx.send(embed=emb)


class FeedView(disnake.ui.View):
    def __init__(self, author: disnake.Member, recipient: disnake.Member):
        super().__init__()
        self.add_item(FeedSelect(author, recipient))


class FeedSelect(disnake.ui.Select):
    def __init__(self, author: disnake.Member, recipient: disnake.Member):
        self.bot = core.Bot.get_bot()
        self.author = author
        self.recipient = recipient
        f = feed.Feed.get_feeds()
        options = []
        for fd in f:
            options.append(disnake.SelectOption(label=fd.name, value=fd.id, emoji=fd.emoji))
        super(FeedSelect, self).__init__(
            min_values=1,
            max_values=1,
            placeholder='Выбрать...',
            options=options
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        if interaction.user.id == self.author.id:
            emb = disnake.Embed(title='Прятного аппетита!', color=0x7FFFA0,
                                description=f'{self.author.mention} прислал {self.recipient.mention} вкусняшку!')
            emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
            emb.set_footer(text=f'Производитель самой свежей и вкусной еды -  {self.bot.user.name}',
                           icon_url=self.bot.user.display_avatar.url)
            await interaction.response.send_message(embed=emb, ephemeral=False)
            await interaction.send(feed.Feed.get_feed_by_id(self.values[0]).emoji)


def setup(bot: commands.Bot):
    bot.add_cog(FunCommands(bot))
