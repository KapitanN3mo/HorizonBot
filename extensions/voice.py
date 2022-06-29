import datetime
import json
import disnake
from typing import List
from disnake.ext import commands
import core
import database
import dt
from assets import emojis
from permissions import admin_permission_required


class VoiceJournal:
    _journals = set()

    def __init__(self, member: disnake.Member):
        self.member = member
        self.history = []
        self._journals.add(self)

    def __eq__(self, other):
        if isinstance(other, VoiceJournal):
            return self.member.id == other.member.id and self.member.guild.id == other.member.guild.id
        else:
            raise TypeError

    def __hash__(self):
        return hash(f"{self.member.id}{self.member.guild.id}")

    @classmethod
    def _find_journal(cls, member: disnake.Member):
        for j in cls._journals:
            if member.id == j.member.id and member.guild.id == j.member.guild.id:
                return j
        else:
            return None

    @classmethod
    def get_journals_from_db_by_member(cls, member: disnake.Member):
        return [*database.VoiceJournal.select().where(
            database.VoiceJournal.user == database.User.get(database.User.user_id == member.id,
                                                            database.User.guild_id == member.guild.id))]

    @classmethod
    def create_report(cls, member):
        journal = cls._find_journal(member)
        considered_time = 0
        if journal is None:
            return None
        start = 0
        end = 0
        history = journal.history
        for i in range(len(history)):
            row = history[i]
            event = row.get('event')
            timestamp = datetime.datetime.strptime(row.get('timestamp'), dt.enchanted_format)
            if event == 'join':
                start = timestamp
            elif event == 'mute':
                end = timestamp
                considered_time += cls.calc_time(start, end)
                start = 0
            elif event == 'unmute':
                start = timestamp
            elif event == 'leave':
                end = timestamp
                considered_time += cls.calc_time(start, end)
            else:
                continue
        total_time = cls.calc_time(datetime.datetime.strptime(history[0].get('timestamp'), dt.enchanted_format),
                                   datetime.datetime.strptime(history[-1].get('timestamp'), dt.enchanted_format))
        return considered_time, total_time,

    @staticmethod
    def calc_time(start: datetime.datetime, end: datetime.datetime):
        if end == 0 or start == 0:
            return 0
        delta = end - start
        if delta.seconds <= 0:
            return 0
        else:
            # print(delta.seconds)
            return delta.seconds

    @classmethod
    def add_row(cls, event, member: disnake.Member, data: dict = None):
        journal: VoiceJournal = cls._find_journal(member)
        if journal is None:
            return
        journal.history.append(
            {'event': event, 'timestamp': datetime.datetime.now().strftime(dt.enchanted_format), 'data': data})

    @classmethod
    def pretty_print(cls, journals: List[dict]):
        emb = disnake.Embed(title=' ', color=disnake.Colour(0xB0C4DE), description='')
        for journal in journals:
            emb.description += '```--------------BEGIN JOURNAL--------------\n'
            if datetime.datetime.strptime(journal[0].get('timestamp'),
                                          dt.enchanted_format).date() == datetime.datetime.strptime(
                journal[-1].get('timestamp'), dt.enchanted_format).date():
                emb.description += f'            DATE: {datetime.datetime.strptime(journal[0].get("timestamp"), dt.enchanted_format).date()}\n'
            else:
                emb.description += f'            DATE: {datetime.datetime.strptime(journal[0].get("timestamp"), dt.enchanted_format).date()} ' \
                                   f'- {datetime.datetime.strptime(journal[-1].get("timestamp"), dt.enchanted_format).date()}\n'
            for row in journal:
                timestamp = datetime.datetime.strptime(row.get("timestamp"), dt.enchanted_format)
                event = row.get('event')
                if event == 'mute':
                    emoji = '🎙'
                    emb.description += f'{emoji}:{event.upper()} {timestamp.time()}\n'
                elif event == 'leave':
                    emoji = '📤'
                    emb.description += f'{emoji}:{event.upper()} {timestamp.time()} CHANNEL: {row["data"]["channel"]}\n'
                elif event == 'unmute':
                    emoji = '🎙'
                    emb.description += f'{emoji}:{event.upper()} {timestamp.time()}\n'
                elif event == 'change':
                    emoji = '🔁'
                    emb.description += f'{emoji}:{event.upper()} {timestamp.time()} FROM {row["data"]["before"]} TO {row["data"]["after"]}\n'
                elif event == 'join':
                    emoji = '📥'
                    emb.description += f'{emoji}:{event.upper()} {timestamp.time()} CHANNEL: {row["data"]["channel"]}\n'
                else:
                    emoji = '⭕'
            emb.description += "---------------END JOURNAL---------------```\n"
        return emb

    @classmethod
    def release_journal(cls, member: disnake.Member):
        try:
            database.VoiceJournal.insert(
                user=database.User.get(database.User.user_id == member.id, database.User.guild_id == member.guild.id),
                data=json.dumps(cls._find_journal(member).history)
            ).execute()
            cls._journals.remove(cls._find_journal(member))
        except AttributeError:
            pass


class VoiceModule(commands.Cog):
    private_views = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    @admin_permission_required
    async def voice_journal(self, inter: disnake.CommandInteraction, member: disnake.Member):
        """Просмотреть журнал голосового чата"""
        view = VoiceJournalView(member)
        await inter.send(view=view, embed=view.emb)
        view.interaction = inter

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


class VoiceJournalView(disnake.ui.View):
    def __init__(self, member: disnake.Member):
        super(VoiceJournalView, self).__init__()
        self.timeout = 120
        self.bot = core.Bot.get_bot()
        self.member = member
        self.interaction = None
        self.journals = VoiceJournal.get_journals_from_db_by_member(self.member)
        self.index = 0
        self.emb = disnake.Embed()
        self.next_button = disnake.ui.Button(
            style=disnake.ButtonStyle.blurple,
            custom_id='next',
            emoji='▶'
        )
        self.back_button = disnake.ui.Button(
            style=disnake.ButtonStyle.blurple,
            custom_id='back',
            emoji='◀'
        )
        self.end_button = disnake.ui.Button(
            style=disnake.ButtonStyle.blurple,
            custom_id='end',
            emoji='⏭'
        )
        self.begin_button = disnake.ui.Button(
            style=disnake.ButtonStyle.blurple,
            custom_id='begin',
            emoji='⏮'
        )
        self.add_item(self.begin_button)
        self.add_item(self.back_button)
        self.back_button.callback = self.back
        self.next_button.callback = self.next
        self.end_button.callback = self.to_end
        self.begin_button.callback = self.to_begin
        self.add_item(self.next_button)
        self.add_item(self.end_button)
        self.render()

    def update(self):
        self.journals = VoiceJournal.get_journals_from_db_by_member(self.member)

    def render(self):
        # print(self.journals)
        self.emb = VoiceJournal.pretty_print([json.loads(j.data) for j in self.journals[self.index:self.index + 1]])
        self.emb.set_footer(text=f'Запись {self.index + 1} из {len(self.journals)}')
        self.emb.timestamp = datetime.datetime.now()
        self.emb.description = f'Журнал голосового чата для {self.member.mention}\n' + self.emb.description
        if self.index == 0:
            self.back_button.disabled = True
            self.next_button.disabled = False
        elif self.index + 1 == len(self.journals):
            self.next_button.disabled = True
            self.back_button.disabled = False
        else:
            self.back_button.disabled = False
            self.next_button.disabled = False

    async def on_timeout(self) -> None:
        self.back_button.disabled = True
        self.next_button.disabled = True
        await self.interaction.edit_original_message(embed=self.emb, view=self)

    async def next(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.update()
        self.index += 1
        self.render()
        await inter.edit_original_message(embed=self.emb, view=self)
        self.interaction = inter

    async def back(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.update()
        self.index -= 1
        self.render()
        await inter.edit_original_message(embed=self.emb, view=self)
        self.interaction = inter

    async def to_end(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.update()
        self.index = len(self.journals) - 1
        self.render()
        await inter.edit_original_message(embed=self.emb, view=self)

    async def to_begin(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.update()
        self.index = 0
        self.render()
        await inter.edit_original_message(embed=self.emb, view=self)


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
    VoiceJournal.add_row('mute', member)


async def unmute(member, before, after):
    VoiceJournal.add_row('unmute', member)


async def connect_channel(member, before):
    j = VoiceJournal(member)
    j.add_row('join', member, data={'channel': before.channel.name})
    if before.mute or before.self_mute:
        j.add_row('mute', member, data={'channel': before.channel.name})
    await VoiceModule.create_private_voice(member, before.channel)


async def change_channel(member, before, after):
    VoiceJournal.add_row('change', member, data={'before': before.channel.name, 'after': after.channel.name})
    await VoiceModule.create_private_voice(member, after.channel)
    await VoiceModule.check_to_delete_private(before.channel)


async def leave_channel(member, before):
    VoiceJournal.add_row('leave', member, data={'channel': before.channel.name})
    await add_xp_by_voice_time(member)
    await VoiceModule.check_to_delete_private(before.channel)


async def add_xp_by_voice_time(member: disnake.Member):
    db_user: database.User = database.User.get_or_none(database.User.user_id == member.id,
                                                       database.User.guild_id == member.guild.id)
    if db_user is None:
        return
    report = VoiceJournal.create_report(member)
    VoiceJournal.release_journal(member)
    c_time = report[0]
    t_time = report[1]
    if c_time >= db_user.guild_id.minimum_voice_time:
        xp = int(c_time * db_user.guild_id.xp_voice_multiplier / 60)
        db_user.xp += xp
    else:
        xp = 0
    db_user.in_voice_time += t_time
    db_user.save()


def setup(bot):
    bot.add_cog(VoiceModule(bot))
