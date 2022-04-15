import asyncio
import json
import disnake
from disnake.ext import commands

import core
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
    private_views = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    @admin_permission_required
    async def private_voice(self, inter: disnake.CommandInteraction):
        """Настройки приватных каналов"""
        db_guild = database.Guild.get_or_none(database.Guild.guild_id == inter.guild.id)
        if db_guild is None:
            return
        v = PrivateVoiceView(inter.guild)
        await inter.send(view=v, embed=v.embed)
        v.last_interaction = inter

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


class PrivateVoiceView(disnake.ui.View):
    _views = {}

    def __init__(self, guild: disnake.Guild):
        super(PrivateVoiceView, self).__init__()
        self.bot = core.Bot.get_bot()
        self.guild = guild
        self.db_guild: database.Guild = None
        self.update_db_data()
        self.timeout = 30
        self.state = 'main'
        self._last_interaction = None
        self.embed: disnake.Embed = None
        try:
            inter = self._views[self.guild.id]
            ts = self.bot.loop.create_task(inter.delete_original_message())
            ts.add_done_callback(self.check)
        except KeyError:
            pass
        self.render()

    def check(self, data):
        pass

    @property
    def last_interaction(self):
        return self._last_interaction

    @last_interaction.setter
    def last_interaction(self, li):
        self._views[self.guild.id] = li
        self._last_interaction = li

    def update_db_data(self):
        self.db_guild = database.Guild.get(database.Guild.guild_id == self.guild.id)

    def gen_embed(self, mode=None):
        if self.state == 'main':
            emb = disnake.Embed(title='Настройки приватных каналов', colour=disnake.Colour.magenta())
            emb.add_field(name='Состояние',
                          value=f'```{emojis.white_check_mark_unicode} Включено```' if mode
                          else f'```{emojis.no_entry_unicode} Выключено```')
            if mode:
                try:
                    channel = self.guild.get_channel(self.db_guild.private_voice)
                    emb.add_field(name='Категория для приваток', value=f'```{channel.category.name}```', inline=False)
                    emb.add_field(name='Канал для создания', value=f'{channel.mention}', inline=False)
                except AttributeError:
                    emb.add_field(
                        name='Ошибка!',
                        value='```Категория не найдена! Во избежание ошибок, для удаления приваток используйте это '
                              'меню```',
                        inline=False)
            self.embed = emb
        elif self.state == 'disable':
            emb = disnake.Embed(title=' ', description='Вы действительно хотите отключить приватные каналы?',
                                colour=disnake.Colour.red())
            self.embed = emb

    async def on_timeout(self) -> None:
        self.render()
        self.embed.set_footer(text='Истекло время ожидания')
        for item in self.children:
            item.disabled = True
        try:
            await self.last_interaction.edit_original_message(view=self, embed=self.embed)
        except disnake.errors.NotFound:
            pass

    def render(self):
        self.update_db_data()
        self.children.clear()
        if self.state == 'main':
            mode = self.db_guild.private_voice is not None
            if mode:
                self.add_item(VoiceDisableButton(self))
            else:
                self.add_item(VoiceEnableButton(self))
            self.gen_embed(mode)
        elif self.state == 'disable':
            self.add_item(ConfirmDisableButton(self))
            self.add_item(CancelDisableButton(self))
            self.gen_embed()


class VoiceDisableButton(disnake.ui.Button):
    def __init__(self, view: PrivateVoiceView):
        super(VoiceDisableButton, self).__init__()
        self.style = disnake.ButtonStyle.red
        self.label = 'Отключить'
        self.parent_view = view

    async def callback(self, inter: disnake.MessageInteraction):
        self.parent_view.last_interaction = inter
        await inter.response.defer()
        self.parent_view.state = 'disable'
        self.parent_view.render()
        await inter.edit_original_message(view=self.parent_view, embed=self.parent_view.embed)


class ConfirmDisableButton(disnake.ui.Button):
    def __init__(self, view: PrivateVoiceView):
        super(ConfirmDisableButton, self).__init__()
        self.style = disnake.ButtonStyle.green
        self.label = 'Отключить'
        self.custom_id = 'del'
        self.parent_view = view

    async def callback(self, inter: disnake.MessageInteraction):
        self.parent_view.last_interaction = inter
        await inter.response.defer()
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == inter.guild_id)
        channel_id = db_guild.private_voice
        db_guild.private_voice = None
        db_guild.save()
        channel = inter.guild.get_channel(channel_id)
        if channel is None:
            self.parent_view.state = 'main'
            self.parent_view.render()
            await inter.edit_original_message(view=self.parent_view, embed=self.parent_view.embed)
            return
        try:
            for chl in channel.category.channels:
                await chl.delete()
            await channel.category.delete()
        except AttributeError:
            pass
        self.parent_view.state = 'main'
        self.parent_view.render()
        await inter.edit_original_message(view=self.parent_view, embed=self.parent_view.embed)


class CancelDisableButton(disnake.ui.Button):
    def __init__(self, view: PrivateVoiceView):
        super(CancelDisableButton, self).__init__()
        self.style = disnake.ButtonStyle.red
        self.label = 'Отмена'
        self.custom_id = 'cancel'
        self.parent_view = view

    async def callback(self, interaction: disnake.MessageInteraction):
        self.parent_view.last_interaction = interaction
        self.parent_view.state = 'main'
        self.parent_view.render()
        await interaction.response.defer()
        await interaction.edit_original_message(view=self.parent_view, embed=self.parent_view.embed)


class VoiceEnableButton(disnake.ui.Button):
    def __init__(self, view: PrivateVoiceView):
        super(VoiceEnableButton, self).__init__()
        self.style = disnake.ButtonStyle.green
        self.label = 'Включить'
        self.parent_view = view

    async def callback(self, inter: disnake.MessageInteraction):
        self.parent_view.last_interaction = inter
        v = EnableVoiceModalWindow(self.parent_view, inter)
        await inter.response.send_modal(modal=v)


class EnableVoiceModalWindow(disnake.ui.Modal):
    def __init__(self, view: PrivateVoiceView, inter: disnake.MessageInteraction):
        self.orig_inter = inter
        self.parent_view = view
        components = [
            disnake.ui.TextInput(
                label='Имя категории',
                custom_id='category_name',
                min_length=1,
                max_length=35,
                value='Приватные каналы',
                required=True
            ),
            disnake.ui.TextInput(
                label='Имя канала',
                custom_id='channel_name',
                min_length=1,
                max_length=35,
                required=True,
                value='[PRESS] Создать приват'
            )
        ]
        super(EnableVoiceModalWindow, self).__init__(title='Включение приватных каналов', components=components)

    async def callback(self, interaction: disnake.ModalInteraction, /) -> None:
        await interaction.response.defer(with_message=False)
        print('callback')
        category_name = interaction.text_values['category_name']
        channel_name = interaction.text_values['channel_name']
        category = await interaction.guild.create_category(name=category_name, reason='Создана для приватных каналов')
        channel = await category.create_voice_channel(name=channel_name)
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == interaction.guild_id)
        db_guild.private_voice = channel.id
        db_guild.save()
        self.parent_view.render()
        await self.orig_inter.edit_original_message(view=self.parent_view, embed=self.parent_view.embed)
        await interaction.delete_original_message()

    async def on_error(self, error: Exception, interaction: disnake.ModalInteraction) -> None:
        print('error')
        print(error)


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
    if voice_time.seconds >= db_user.guild_id.minimum_voice_time:
        xp = int(voice_time.seconds * db_user.guild_id.xp_voice_multiplier)
        db_user.xp += xp
    db_user.in_voice_time += voice_time.seconds
    db_user.save()


def setup(bot):
    bot.add_cog(VoiceModule(bot))
