import asyncio
import json
from discord.ext import commands
import database
from modules.scripts import *
from modules.permissions import admin_permission_required
import discord
from assets import emojis
from extensions.events import Events


class Statistics(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def statistics(self, ctx: commands.Context, mode):
        mode = to_bool(mode)
        db_guild = database.Guild.get_or_none(database.Guild.guild_id == ctx.guild.id)
        if mode:
            guild = ctx.guild
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False)
            }
            category = await guild.create_category('📊 Статистика', overwrites=overwrites, position=0)
            db_guild.statistics_category = category.id
            db_guild.save()
            await ctx.send(':white_check_mark: `Функция успешно включена!`')
        else:
            guild: discord.Guild = ctx.guild
            db_category = db_guild.statistics_category
            if db_category is None:
                await ctx.send(':no_entry: `Функция уже отключена`')
            else:
                categories = guild.categories
                category = None
                for cg in categories:
                    if cg.id == db_category:
                        category = cg
                if category is None:
                    await ctx.send(':exclamation: `Не удалось найти категорию`')
                    return
                for channel in category.channels:
                    try:
                        await channel.delete()
                    except:
                        pass
                await category.delete()
                db_guild.statistics_category = None
                db_guild.statistics_info = None
                db_guild.save()
                await ctx.send(':white_check_mark: `Функция успешно отключена`')

    @commands.command(aliases=['statistics.messages_count'])
    @admin_permission_required
    async def statistics_messages_count(self, ctx: commands.Context, mode):
        mode = to_bool(mode)
        db_guild = database.Guild.get_or_none(database.Guild.guild_id == ctx.guild.id)
        if db_guild.statistics_category is None:
            await ctx.send(f'{emojis.exclamation} `модуль статистики отключён!`')
            return
        if mode:
            if db_guild.statistics_info is None:
                stat_info = {}
            else:
                stat_info = json.loads(db_guild.statistics_info)
            try:
                current_state = stat_info['messages_count']['mode']
            except KeyError:
                current_state = False
            if current_state:
                await ctx.send(f'{emojis.exclamation} `функция уже включена!`')
                return
            else:
                guild: discord.Guild = ctx.guild
                db_category = db_guild.statistics_category
                categories = guild.categories
                category = None
                for cg in categories:
                    if cg.id == db_category:
                        category = cg
                if category is None:
                    await ctx.send(f'{emojis.exclamation} `не удалось найти категорию!`')
                    return
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True)
                }
                channel = await guild.create_voice_channel('???', overwrites=overwrites, category=category)
                stat_info['messages_count'] = {'mode': True, 'channel': channel.id}
                stat_info = json.dumps(stat_info)
                db_guild.statistics_info = stat_info
                db_guild.save()
                await ctx.send(':white_check_mark: `Функция успешно включена!`')
        else:
            if db_guild.statistics_info is None:
                stat_info = {}
            else:
                stat_info = json.loads(db_guild.statistics_info)
            try:
                current_state = stat_info['messages_count']['mode']
            except KeyError:
                current_state = False
            if current_state:
                guild: discord.Guild = ctx.guild
                channel: discord.VoiceChannel = guild.get_channel(stat_info['messages_count']['channel'])
                if channel is None:
                    await ctx.send(f'{emojis.exclamation} `Не удалось найти канал!`')
                    stat_info['messages_count'] = {'mode': False, 'channel': None}
                    stat_info = json.dumps(stat_info)
                    db_guild.statistics_info = stat_info
                    db_guild.save()
                    await ctx.send(
                        f'{emojis.exclamation} `Данные были удалены из БД, если канал существует, удалите его вручную!`')
                    return
                await channel.delete(reason=f'Счётчик сообщений отключён. Команда от {ctx.author}')
                stat_info['messages_count'] = {'mode': False, 'channel': None}
                stat_info = json.dumps(stat_info)
                db_guild.statistics_info = stat_info
                db_guild.save()
                await ctx.send(':white_check_mark: `Функция успешно отключена`')
            else:
                await ctx.send(f'{emojis.exclamation} `функция уже выключена!`')
                return

    @commands.command(aliases=['statistics.user_count'])
    @admin_permission_required
    async def statistics_user_count(self, ctx: commands.Context, mode):
        mode = to_bool(mode)
        db_guild = database.Guild.get_or_none(database.Guild.guild_id == ctx.guild.id)
        if db_guild.statistics_category is None:
            await ctx.send(f'{emojis.exclamation} `модуль статистики отключён!`')
            return
        if mode:
            if db_guild.statistics_info is None:
                stat_info = {}
            else:
                stat_info = json.loads(db_guild.statistics_info)
            try:
                current_state = stat_info['user_count']['mode']
            except KeyError:
                current_state = False
            if current_state:
                await ctx.send(f'{emojis.exclamation} `функция уже включена!`')
                return
            else:
                guild: discord.Guild = ctx.guild
                db_category = db_guild.statistics_category
                categories = guild.categories
                category = None
                for cg in categories:
                    if cg.id == db_category:
                        category = cg
                if category is None:
                    await ctx.send(f'{emojis.exclamation} `не удалось найти категорию!`')
                    return
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True)
                }
                channel = await guild.create_voice_channel('???', overwrites=overwrites, category=category)
                stat_info['user_count'] = {'mode': True, 'channel': channel.id}
                stat_info = json.dumps(stat_info)
                db_guild.statistics_info = stat_info
                db_guild.save()
                await ctx.send(':white_check_mark: `Функция успешно включена!`')
        else:
            if db_guild.statistics_info is None:
                stat_info = {}
            else:
                stat_info = json.loads(db_guild.statistics_info)
            try:
                current_state = stat_info['user_count']['mode']
            except KeyError:
                current_state = False
            if current_state:
                guild: discord.Guild = ctx.guild
                channel: discord.VoiceChannel = guild.get_channel(stat_info['user_count']['channel'])
                if channel is None:
                    await ctx.send(f'{emojis.exclamation} `Не удалось найти канал!`')
                    stat_info['user_count'] = {'mode': False, 'channel': None}
                    stat_info = json.dumps(stat_info)
                    db_guild.statistics_info = stat_info
                    db_guild.save()
                    await ctx.send(
                        f'{emojis.exclamation} `Данные были удалены из БД, если канал существует, удалите его вручную!`')
                    return
                await channel.delete(reason=f'Счётчик пользователей отключён. Команда от {ctx.author}')
                stat_info['user_count'] = {'mode': False, 'channel': None}
                stat_info = json.dumps(stat_info)
                db_guild.statistics_info = stat_info
                db_guild.save()
                await ctx.send(':white_check_mark: `Функция успешно отключена`')
            else:
                await ctx.send(f'{emojis.exclamation} `функция уже выключена!`')
                return


class Analyzer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.methods = {}
        self.methods['user_count'] = self.count_user_on_guild
        self.methods['messages_count'] = self.day_message_count
        Events.add_task(self.analyze_guilds)
        Events.add_task(self.analyze_guilds)
        Events.connect_on_message(self.message_counter)
        self.cache = {}

    async def message_counter(self, message: discord.Message):
        print('update_messages')
        guild = message.guild
        if guild is None:
            return
        try:
            self.cache[guild.id]
        except KeyError:
            self.cache[guild.id] = {}
        try:
            self.cache[guild.id]['messages_count'] += 1
        except KeyError:
            self.cache[guild.id]['messages_count'] = 1

    async def analyze_guilds(self):
        while True:
            for guild in self.bot.guilds:
                print('check_guild')
                db_guild = database.Guild.get_or_none(database.Guild.guild_id == guild.id)
                if db_guild is None:
                    continue
                stat_info = db_guild.statistics_info
                if stat_info is None:
                    continue
                stat_info = json.loads(stat_info)
                for method in stat_info:
                    if stat_info[method]['mode']:
                        print(stat_info)
                        func = self.methods[method]
                        try:
                            await func(guild, stat_info[method])
                        except Exception as ex:
                            print(ex)
            await asyncio.sleep(60*5)

    async def count_user_on_guild(self, guild: discord.Guild, stat_info):
        users_count = 0
        bots_count = 0
        for member in guild.members:
            if member.bot:
                bots_count += 1
            else:
                users_count += 1
        channels = await guild.fetch_channels()
        channel = None
        for ch in channels:
            if ch.id == stat_info['channel']:
                channel = ch
                break
        if channel is None:
            return
        await channel.edit(name=f'🌚: {users_count} 🤖: {bots_count}')

    async def day_message_count(self, guild: discord.Guild, stat_info):
        print('dd')
        channels = await guild.fetch_channels()
        channel = None
        for ch in channels:
            # print(ch.id,stat_info['channel'])
            if ch.id == stat_info['channel']:
                channel = ch
                break
        if channel is None:
            return
        try:
            print(self.cache)
            await channel.edit(name=f'Сообщений: {self.cache[guild.id]["messages_count"]}')
        except KeyError:
            print('return')
            await channel.edit(name='Сообщений: нет информации')
            print('edit complete')


def setup(bot):
    bot.add_cog(Statistics(bot))
    bot.add_cog(Analyzer(bot))
