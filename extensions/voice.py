import json
import disnake
from disnake.ext import commands
import database
import dt
from dt import get_msk_datetime
from assets import emojis
from permissions import admin_permission_required


class VoiceJournal:
    _journals = []

    def __init__(self, member: disnake.Member):
        self.member = member
        self.history = []
        self._journals.append(self)

    @classmethod
    def _find_journal(cls, member: disnake.Member):
        for j in cls._journals:
            if member.id == j.member.id and member.guild.id == j.member.guild.id:
                return j
        else:
            return None

    @classmethod
    def add_row(cls, event, member: disnake.Member, xp: int):
        journal: VoiceJournal = cls._find_journal(member)
        if journal is None:
            return
        journal.history.append({'event': event, 'timestamp': dt.get_msk_datetime(), 'xp': xp})

    def pretty_print(self):
        emb = disnake.Embed(title='Журнал голосового канала', color=disnake.Colour(0xB0C4DE))
        for row in self.history:
            event = row.get('event')
            xp = row.get('event')
            if event == 'mute':
                emoji = '🔕'
            elif event == 'leave':
                emoji = '🔌'
            else:
                emoji = '♦'
            emb.description += f'{emoji} {xp}'
        return emb


class VoiceModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def enable_private_voice(self, ctx: commands.Context, *, name=''):
        db_guild = database.Guild.get_or_none(database.Guild.guild_id == ctx.guild.id)
        if name == '':
            await ctx.send(f'{emojis.exclamation}`Укажите имя канала`')
            return
        if db_guild is None:
            return
        if db_guild.private_voice is None:
            category = await ctx.guild.create_category('[СОЗДАТЬ ПРИВАТ]')
            channel = await ctx.guild.create_voice_channel(name, reason='Канал для создания приваток',
                                                           category=category)
            db_guild.private_voice = channel.id
            db_guild.save()
            await ctx.send(f'{emojis.white_check_mark} `Голосовой канал создан!`')
        else:
            await ctx.send(f'{emojis.exclamation} `Приватные каналы уже включены на вашем сервере`')
            await ctx.send(f'`Вы можете отключить их при помощи команды [disable_private_voice]`')

    @commands.command()
    @admin_permission_required
    async def disable_private_voice(self, ctx: commands.Context):
        db_guild = database.Guild.get_or_none(database.Guild.guild_id == ctx.guild.id)
        if db_guild is None:
            return
        if db_guild.private_voice is not None:
            create_channel: disnake.VoiceChannel = ctx.guild.get_channel(db_guild.private_voice)
            if create_channel is None:
                await ctx.send(
                    f'{emojis.exclamation}` Не удалось найти канал. Возможно он был удалён вручную. Данные очищены.`')
                db_guild.private_voice = None
                db_guild.save()
                return
            for channel in create_channel.category.channels:
                try:
                    await channel.delete()
                except Exception as ex:
                    pass
            category = create_channel.category
            if category is not None:
                await category.delete()
            try:
                await create_channel.delete()
            except Exception as ex:
                print(ex)
            db_guild.private_voice = None
            db_guild.save()
            await ctx.send(f'{emojis.white_check_mark}`Удаление завершено, приватные каналы отключены!`')
        else:
            await ctx.send(f'{emojis.exclamation}`Приватные каналы уже отключены!`')

    @classmethod
    async def check_to_delete_private(cls, channel: disnake.VoiceChannel):
        db_guild: database.Guild = database.Guild.get_or_none(database.Guild.guild_id == channel.guild.id)
        if db_guild.private_voice is None:
            return
        if channel.id == db_guild.private_voice:
            return
        ds_create_channel: disnake.VoiceChannel = channel.guild.get_channel(db_guild.private_voice)
        if channel.category.id == ds_create_channel.category.id:
            if len(channel.members) == 0:
                try:
                    await channel.delete()
                except:
                    pass

    @classmethod
    async def create_private_voice(cls, member: disnake.Member, channel: disnake.VoiceChannel):
        db_guild: database.Guild = database.Guild.get_or_none(database.Guild.guild_id == member.guild.id)
        if channel is None:
            return
        if db_guild.private_voice is None:
            return
        if channel.id == db_guild.private_voice:
            overwrite = disnake.PermissionOverwrite()
            overwrite.manage_channels = True
            pr = {
                member: overwrite
            }
            ch = await channel.category.create_voice_channel(member.display_name, overwrites=pr)
            await member.move_to(ch)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState,
                                    after: disnake.VoiceState):
        if before.channel is None and after.channel is not None:
            await connect_channel(member, after)
        elif before.channel is not None and after.channel is None:
            await leave_channel(member, before)
        elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            await change_channel(member, before, after)
        elif before.channel.id == after.channel.id:
            if not (before.self_mute and before.mute) and (after.self_mute or after.mute):
                await mute(member, before, after)
            elif (before.self_mute or before.mute) and not (after.self_mute and after.mute):
                await unmute(member, before, after)


async def mute(member, before, after):
    await add_xp_by_voice_time(member)


async def unmute(member, before, after):
    await set_entry_voice_time(member)


async def connect_channel(member, after):
    if after.mute or after.self_mute:
        return
    await set_entry_voice_time(member)
    await VoiceModule.create_private_voice(member, after.channel)


async def change_channel(member, before, after):
    await VoiceModule.create_private_voice(member, after.channel)
    await VoiceModule.check_to_delete_private(before.channel)


async def leave_channel(member, before):
    await add_xp_by_voice_time(member)
    await VoiceModule.check_to_delete_private(before.channel)


async def set_entry_voice_time(member: disnake.Member):
    db_user: database.User = database.User.get_or_none(database.User.user_id == member.id,
                                                       database.User.guild_id == member.guild.id)
    if db_user is None:
        return
    db_user.voice_entry = dt.get_msk_datetime()
    db_user.save()


async def add_xp_by_voice_time(member: disnake.Member):
    db_user: database.User = database.User.get_or_none(database.User.user_id == member.id,
                                                       database.User.guild_id == member.guild.id)
    if db_user is None:
        return
    if db_user.voice_entry is None:
        return
    voice_time = (dt.get_msk_datetime() - db_user.voice_entry)
    if voice_time.seconds <= db_user.guild_id.minimum_voice_time:
        return
    xp = int(voice_time.seconds * db_user.guild_id.xp_voice_multiplier)
    db_user.in_voice_time += voice_time.seconds
    db_user.xp += xp
    db_user.save()


def setup(bot):
    bot.add_cog(VoiceModule(bot))
