import datetime
import random

import pytz

from assets import economy
import disnake
from disnake.ext import commands
from functools import wraps
from permissions import admin_permission_required
import database


def transaction(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        Economy.increase_transaction_counter()
        return await func(*args, **kwargs)

    return wrapper


class Economy(commands.Cog):
    _transaction_counter = 0

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @classmethod
    def increase_transaction_counter(cls):
        cls._transaction_counter += 1

    @commands.slash_command()
    @transaction
    async def work(self, inter: disnake.CommandInteraction):
        """БЕЗОПАСНЫЙ способ получить деньги"""
        emb = disnake.Embed(colour=disnake.Colour(0x66BB6A))
        emb.set_author(name=inter.author.display_name, icon_url=inter.author.display_avatar.url)
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == inter.guild_id)
        db_user: database.User = database.User.get(database.User.user_id == inter.author.id,
                                                   database.User.guild_id == inter.guild_id)
        delta: datetime.timedelta = datetime.datetime.now(tz=pytz.UTC) - db_user.last_work_use
        if delta.seconds < (db_guild.work_delay * 60):
            seconds1 = db_guild.work_delay * 60 - delta.seconds
            minutes = seconds1 // 60
            seconds = seconds1 % 60
            emb.colour = disnake.Colour(0x03A8F4)
            emb.description = f'Вы не можете работать ещё {f"{minutes} минут" if minutes > 0 else ""}' \
                              f'{f"{seconds} секунд" if minutes == 0 else ""}'
            await inter.send(embed=emb)
            return
        cash = random.randint(db_guild.min_work_cash, db_guild.max_work_cash)
        db_user.money += cash
        phrase = random.choice(economy.work)
        emb.set_footer(text=f'Запрос №{self._transaction_counter}')
        emb.description = phrase['text'].replace('MONEY', str(cash)).replace('COIN', db_guild.coin_name)
        db_user.last_work_use = datetime.datetime.now()
        db_user.save()
        await inter.send(embed=emb)

    @commands.slash_command()
    @transaction
    async def gachi_work(self, inter: disnake.CommandInteraction):
        """Рискни своим очком"""
        emb = disnake.Embed()
        emb.set_author(name=inter.author.display_name, icon_url=inter.author.display_avatar.url)
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == inter.guild_id)
        db_user: database.User = database.User.get(database.User.user_id == inter.author.id,
                                                   database.User.guild_id == inter.guild_id)
        delta: datetime.timedelta = datetime.datetime.now(tz=pytz.UTC) - db_user.last_gachi_use.astimezone(tz=pytz.UTC)
        if db_user.is_ass_breaking:
            delay = db_guild.gachi_delay_after_fail
        else:
            delay = db_guild.gachi_delay
        if delta.total_seconds() < (delay * 60):
            seconds1 = delay * 60 - delta.seconds
            minutes = seconds1 // 60
            seconds = seconds1 % 60
            emb.colour = disnake.Colour(0x03A8F4)
            hours = minutes // 60
            minutes = minutes - hours * 60
            if db_user.is_ass_breaking:
                emb.description = f'До окончания лечения вашего очка осталось {f"{hours} часов " if hours > 0 else ""}{f"{minutes} минут" if minutes > 0 else ""}' \
                                  f'{f"{seconds} секунд" if minutes < 0 else ""}'
            else:
                emb.description = f'До открытия гачи-клуба осталось ещё {f"{minutes} минут" if minutes > 0 else ""}' \
                                  f'{f"{seconds} секунд" if minutes < 0 else ""}'

            await inter.send(embed=emb)
        else:
            number = random.randint(1, 100)
            if number <= db_guild.ass_breaking_chance:
                db_user.is_ass_breaking = True
                emb.colour = disnake.Colour(0xFF1836)
                emb.description = 'Упс... В порыве страсти вам порвали очко. Все заработанные деньги ' \
                                  'вы потратите на лечение. Лечение длится сутки.'

                await inter.send(embed=emb)
            else:
                db_user.is_ass_breaking = False
                emb.colour = disnake.Colour(0x66BB6A)
                money = random.randint(db_guild.min_gachi_cash, db_guild.max_gachi_cash)
                db_user.money += money
                emb.set_footer(text=f'Запрос №{self._transaction_counter}')
                emb.description = f'Вы успешно прошли все испытания Dungeon Master-а и заработали {money} {db_guild.coin_name}'
                await inter.send(embed=emb)
            db_user.last_gachi_use = datetime.datetime.now()
            db_user.save()

    @commands.slash_command()
    @transaction
    async def crime(self, inter: disnake.CommandInteraction):
        """КримимналОчка"""
        emb = disnake.Embed(colour=disnake.Colour(0x66BB6A))
        emb.set_author(name=inter.author.display_name, icon_url=inter.author.display_avatar.url)
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == inter.guild_id)
        db_user: database.User = database.User.get(database.User.user_id == inter.author.id,
                                                   database.User.guild_id == inter.guild_id)
        delta: datetime.timedelta = datetime.datetime.now() - db_user.last_crime_use
        if delta.seconds < (db_guild.crime_delay * 60):
            seconds1 = db_guild.crime_delay * 60 - delta.seconds
            minutes = seconds1 // 60
            seconds = seconds1 % 60
            emb.colour = disnake.Colour(0x03A8F4)
            emb.description = f'Вы должны скрываться ещё {f"{minutes} минут" if minutes > 0 else ""}' \
                              f'{f"{seconds} секунд" if minutes < 0 else ""}'
            await inter.send(embed=emb)
            return
        cash = random.randint(db_guild.min_crime_cash, db_guild.max_crime_cash)
        number = random.randint(1, 100)
        if number <= db_guild.crime_fail_chance:
            db_user.money -= cash
            phrase = random.choice(economy.crime_negative)
            emb.colour = disnake.Colour(0xFF1836)
        else:
            phrase = random.choice(economy.crime_positive)
            db_user.money += cash
        emb.description = phrase['text'].replace('MONEY', str(cash)).replace('COIN', db_guild.coin_name)
        emb.set_footer(text=f'Запрос №{self._transaction_counter}')
        db_user.last_crime_use = datetime.datetime.now()
        db_user.save()
        await inter.send(embed=emb)

    @commands.slash_command()
    @transaction
    async def balance(self, inter: disnake.CommandInteraction, user: disnake.Member = None):
        """Посмотреть баланс"""
        if user is None:
            user = inter.author
        db_user: database.User = database.User.get(database.User.user_id == user.id,
                                                   database.User.guild_id == inter.guild_id)
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == inter.guild_id)
        emb = disnake.Embed(colour=disnake.Colour(0xDA18DE))
        emb.set_footer(text=f'Запрос №{self._transaction_counter}')
        emb.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        emb.add_field(name='Наличка:', value=f'{db_user.money} {db_guild.coin_name}', inline=True)
        emb.add_field(name='В банке:', value=f'{db_user.bank} {db_guild.coin_name}', inline=True)
        emb.add_field(name='Итого:', value=f'{db_user.money + db_user.bank} {db_guild.coin_name}', inline=True)
        await inter.send(embed=emb)

    @commands.slash_command()
    @transaction
    async def deposit(self, inter: disnake.CommandInteraction, value: str):
        """Положить деньги в банк"""
        db_user: database.User = database.User.get(database.User.user_id == inter.author.id,
                                                   database.User.guild_id == inter.guild_id)
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == inter.guild_id)
        emb = disnake.Embed()
        emb.set_author(name=inter.author.display_name, icon_url=inter.author.display_avatar.url)
        emb.set_footer(text=f'Запрос №{self._transaction_counter}')
        if value == 'all':
            value = db_user.money
        else:
            try:
                value = int(value)
            except ValueError:
                emb.colour = disnake.Colour(0xFF1836)
                emb.description = f'Некорректная сумма. Укажите число или `all`'
                await inter.send(embed=emb)
                return
        if db_user.money >= value:
            db_user.money -= value
            db_user.bank += value
            db_user.save()
            emb.colour = disnake.Colour(0x66BB6A)
            emb.description = f'Вы перевели {value} {db_guild.coin_name} в банк'

        else:
            emb.colour = disnake.Colour(0xFF1836)
            emb.description = f'Недостаточно средств'

        await inter.send(embed=emb)

    @commands.slash_command()
    @transaction
    async def withdraw(self, inter: disnake.CommandInteraction, value: str):
        """Взять деньги из банка"""
        db_user: database.User = database.User.get(database.User.user_id == inter.author.id,
                                                   database.User.guild_id == inter.guild_id)
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == inter.guild_id)
        emb = disnake.Embed()
        emb.set_author(name=inter.author.display_name, icon_url=inter.author.display_avatar.url)
        emb.set_footer(text=f'Запрос №{self._transaction_counter}')
        if value == 'all':
            value = db_user.bank
        else:
            try:
                value = int(value)
            except ValueError:
                emb.colour = disnake.Colour(0xFF1836)
                emb.description = f'Некорректная сумма. Укажите число или `all`'
                await inter.send(embed=emb)
                return
        if value <= db_user.bank:
            db_user.bank -= value
            db_user.money += value
            emb.colour = disnake.Colour(0x66BB6A)
            emb.description = f'Вы сняли  {value} {db_guild.coin_name} из банка'
            db_user.save()
        else:
            emb.colour = disnake.Colour(0xFF1836)
            emb.description = f'Недостаточно средств'
        await inter.send(embed=emb)

    @commands.slash_command()
    @transaction
    async def steal(self, inter: disnake.CommandInteraction, user: disnake.Member):
        """Украсть деньги"""
        db_user: database.User = database.User.get(database.User.user_id == inter.author.id,
                                                   database.User.guild_id == inter.guild_id)
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == inter.guild_id)
        db_user2: database.User = database.User.get(database.User.user_id == user.id,
                                                    database.User.guild_id == inter.guild_id)
        chance = random.randint(1, 100)
        emb = disnake.Embed()
        emb.set_author(name=inter.author.display_name, icon_url=inter.author.display_avatar.url)
        emb.set_footer(text=f'Запрос №{self._transaction_counter}')
        if chance >= db_guild.steal_fail_chance:
            loss = int(
                db_user2.money * random.randint(db_guild.min_steal_lucky_loss, db_guild.max_steal_lucky_loss) / 100)
            db_user2.money -= loss
            db_user.money += loss
            db_user2.save()
            db_user.save()
            emb.colour = disnake.Colour(0x66BB6A)
            emb.description = f'Вы украли {loss} {db_guild.coin_name} у {user.mention}'
        else:
            loss = int((db_user.money + db_user.bank) * random.randint(db_guild.min_steal_fail_loss,
                                                                       db_guild.max_steal_fail_loss) / 100)
            db_user.money -= loss
            db_user.save()
            emb.colour = disnake.Colour(0xFF1836)
            emb.description = f'Вас поймали при попытке кражи. Штраф: {loss}'
        await inter.send(embed=emb)

    @commands.slash_command()
    @transaction
    async def give(self, inter: disnake.CommandInteraction, user: disnake.Member, value: str):
        """Передать деньги"""
        db_user: database.User = database.User.get(database.User.user_id == inter.author.id,
                                                   database.User.guild_id == inter.guild_id)
        db_user2: database.User = database.User.get(database.User.user_id == user.id,
                                                    database.User.guild_id == inter.guild_id)
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == inter.guild_id)
        emb = disnake.Embed()
        emb.set_author(name=inter.author.display_name, icon_url=inter.author.display_avatar.url)
        emb.set_footer(text=f'Запрос №{self._transaction_counter}')
        if value == 'all':
            value = db_user.money
        else:
            try:
                value = int(value)
            except ValueError:
                emb.colour = disnake.Colour(0xFF1836)
                emb.description = f'Некорректная сумма. Укажите число или `all`'
                await inter.send(embed=emb)
                return
        if value > db_user.money:
            emb.colour = disnake.Colour(0xFF1836)
            emb.description = 'Недостаточно средств'
        else:
            db_user.money -= value
            db_user2.money += value
            db_user.save()
            db_user2.save()
            emb.colour = disnake.Colour(0x66BB6A)
            emb.description = f'Вы перевели {value} {db_guild.coin_name} {user.mention}'
        await inter.send(embed=emb)

    @commands.slash_command()
    @admin_permission_required
    @transaction
    async def add_money(self, inter: disnake.CommandInteraction, user: disnake.Member, value: int):
        """Добавить деньги"""
        db_user: database.User = database.User.get(database.User.user_id == user.id,
                                                   database.User.guild_id == inter.guild_id)
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == inter.guild_id)
        db_user.bank += value
        db_user.save()
        emb = disnake.Embed(description=f'Выдано {value} {db_guild.coin_name} для {user.mention}',
                            colour=disnake.Colour(0xFFFF56))
        emb.set_author(name=inter.author.display_name, icon_url=inter.author.display_avatar.url)
        await inter.send(embed=emb)

    @commands.slash_command()
    @admin_permission_required
    @transaction
    async def remove_money(self, inter: disnake.CommandInteraction, user: disnake.Member, value: int):
        """Добавить деньги"""
        db_user: database.User = database.User.get(database.User.user_id == user.id,
                                                   database.User.guild_id == inter.guild_id)
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == inter.guild_id)
        db_user.bank -= value
        db_user.save()
        emb = disnake.Embed(description=f'Удалено {value} {db_guild.coin_name} у {user.mention}',
                            colour=disnake.Colour(0xFFFF56))
        emb.set_author(name=inter.author.display_name, icon_url=inter.author.display_avatar.url)
        await inter.send(embed=emb)


def setup(bot):
    bot.add_cog(Economy(bot))
