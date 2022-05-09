import asyncio
import datetime

import disnake
from disnake.ext import commands, tasks
import core
from permissions import admin_permission_required
from assets import emojis
import database
from typing import List, Tuple


class RMS(commands.Cog):
    bot = core.Bot.get_bot()
    task = None
    tsk: List[asyncio.Task] = []

    @classmethod
    def add_role(cls, role: disnake.Role, emoji: str):
        try:
            database.Role.insert(
                role_id=role.id,
                guild=role.guild.id,
                name=role.name,
                emoji=emoji,
                color=role.color,
                having_users='[]'
            ).execute()
            return True, None
        except Exception as ex:
            return False, str(ex)

    @classmethod
    def connect_role(cls, guild: disnake.Guild, role: disnake.Role, block_id: int, emoji: str):
        db_role = database.Role.get_or_none(database.Role.role_id == role.id)
        if db_role is None:
            result, info = cls.add_role(role, emoji)
            if result is False:
                return False, f'Ошибка БД: {info}'
            db_role = database.Role.get_or_none(database.Role.role_id == role.id)
        else:
            return False, 'Эта роль управляется другим блоком!'
        db_block = database.RoleBlock.get_or_none(database.RoleBlock.block_id == block_id,
                                                  database.RoleBlock.guild == guild.id)
        if db_block is None:
            return False, 'Блок не найден'
        if cls.check_emoji(db_block, emoji):
            return False, 'Этот эмодзи уже используется в этом блоке'
        db_role.linked_block = db_block
        db_role.save()
        cls.bot.loop.create_task(cls.update_block(db_role.linked_block))
        return True, None

    @classmethod
    def disconnect_role(cls, role: disnake.Role):
        role = database.Role.get_or_none(database.Role.role_id == role.id)
        if role is None:
            return False, 'Эта роль и так не подключена'
        cls.bot.loop.create_task(cls.update_block(role.linked_block))
        role.delete_instance()
        return True, None

    @classmethod
    def change_emoji(cls, role: disnake.Role, emoji: str):
        db_role = database.Role.get_or_none(database.Role.role_id == role.id)
        if db_role is None:
            return False, 'Такой роли нет в RMS'
        db_role.custom_emojis = emoji
        db_role.save()
        return True, None

    @classmethod
    def check_emoji(cls, block: database.RoleBlock, emoji: str):
        block_emojis = [role.emoji for role in database.Role.select().where(database.Role.linked_block == block)]
        return emoji in block_emojis

    @classmethod
    def new_block(cls, guild: disnake.Guild, name: str, color: str):
        color = color.replace('#', '')
        color = int(color, 16)
        try:
            database.RoleBlock.insert(
                name=name,
                color=color,
                style='numeric',
                guild=guild.id,
            ).execute()
            return True, None
        except Exception as ex:
            return False, str(ex)

    @classmethod
    async def remove_block(cls, guild: disnake.Guild, block_id: int):
        block: database.RoleBlock = database.RoleBlock.get_or_none(database.RoleBlock.block_id == block_id,
                                                                   database.RoleBlock.guild == guild.id)
        if block is None:
            return False, 'Такой блок не существует'
        try:
            roles = database.Role.select().where(database.Role.linked_block == block)
            for role in roles:
                role.delete_instance()
            channel = cls.bot.get_channel(block.block_channel_id)
            message = await channel.fetch_message(block.block_message_id)
            await message.delete()
        except Exception as ex:
            print(ex)
        block.delete_instance()
        return True, None

    @classmethod
    def get_blocks_embed(cls, guild: disnake.Guild):
        emb = disnake.Embed(title=f'Список блоков для {guild.name}', description='', color=disnake.Colour(0x4F9100))
        blocks = cls.get_blocks_data(guild)
        for block in blocks:
            print(block)
            connected_role_count = database.Role.select().where(database.Role.linked_block == block).count()
            if block.block_channel_id is not None:
                channel = cls.bot.get_channel(block.block_channel_id)
            else:
                channel = None
            row = f'ID:{block.block_id};' \
                  f' Канал: {channel.mention if channel is not None else "Скрытый"};' \
                  f' Кол-во ролей: {connected_role_count}\n'
            emb.description += row
        if len(blocks) == 0:
            emb.description = 'Ни одного блока не найдено '
            emb.set_image(
                url='https://cdn.discordapp.com/attachments/940641488122044476/973146397371150366/7c1ca448be31c489fb66214ea3ae6deb.jpg')
        emb.set_footer(icon_url=cls.bot.user.display_avatar)
        emb.timestamp = datetime.datetime.now()
        return emb

    @classmethod
    def hide_block(cls, guild: disnake.Guild, block_id: int):
        block = database.RoleBlock.get_or_none(database.RoleBlock.block_id == block_id,
                                               database.RoleBlock.guild == guild.id)
        if block is None:
            return False, 'Блок не найден'
        block.block_channel_id = None
        block.block_message_id = None
        block.save()
        return True, ''

    @classmethod
    async def send_block_message(cls, block: database.RoleBlock, channel: disnake.TextChannel):
        res, data, react_list = cls.gen_block_embed(block)
        if res:
            mes = await channel.send(embed=data)
            for react in react_list:
                await mes.add_reaction(react)
            block.block_message_id = mes.id
            block.block_channel_id = mes.channel.id
            block.save()
            return True, None
        else:
            return False, data

    @classmethod
    def gen_block_embed(cls, block: database.RoleBlock):
        guild = cls.bot.get_guild(block.guild.guild_id)
        emb = disnake.Embed(title=block.name, description='', colour=block.color)
        react_list = []
        for role in database.Role.select().where(database.Role.linked_block == block):
            ds_role = guild.get_role(role.role_id)
            if ds_role is None:
                return False, f'Роль {role.name} не найдена!', None
            emb.description += f'{role.emoji}:{ds_role.mention}\n'
            react_list.append(role.emoji)
        return True, emb, react_list

    @classmethod
    def get_blocks_data(cls, guild: disnake.Guild):
        return [*database.RoleBlock.select().where(database.RoleBlock.guild == guild.id)]

    @classmethod
    def get_roles_data(cls, block: database.RoleBlock) -> List[database.Role]:
        return [*database.Role.select().where(database.Role.linked_block == block)]

    @classmethod
    async def fix_block(cls, block: database.RoleBlock, db_role: database.Role, message: disnake.Message):
        message_reactions = [react.emoji for react in message.reactions]
        if db_role.emoji in message_reactions:
            await message.clear_reaction(db_role.emoji)
        if f'<@&{db_role.role_id}>' in message.embeds[0].description:
            res, data, reacts = cls.gen_block_embed(block)
            if res:
                message = await message.edit(embed=data)
                message_reactions = [react.emoji for react in message.reactions]
                for tr_react in reversed(reacts):
                    if tr_react not in message_reactions:
                        await message.add_reaction(tr_react)
                    reacts.remove(tr_react)
                for react in reacts:
                    await message.clear_reaction(react)

    @classmethod
    async def update_block(cls, role_block: database.RoleBlock):
        guild = cls.bot.get_guild(role_block.guild.guild_id)
        roles = cls.get_roles_data(role_block)
        if role_block.block_message_id:
            block_channel = guild.get_channel(role_block.block_channel_id)
            if block_channel is None:
                await guild.system_channel.send(
                    f'{emojis.exclamation}`[RMS_ERROR] Канал блока {role_block.name}#{role_block.block_id} не найден! '
                    f'Блок переведён в скрытый режим`')
                cls.hide_block(guild, role_block.block_id)
                return
            try:
                block_message: disnake.Message = await block_channel.fetch_message(role_block.block_message_id)
            except disnake.errors.NotFound:
                await guild.system_channel.send(
                    f'{emojis.exclamation}`[RMS_ERROR] Сообщение блока {role_block.name}#{role_block.block_id} не найдено! '
                    f'Блок переведён в скрытый режим`')
                cls.hide_block(guild, role_block.block_id)
                return
            if len(roles) == 0:
                cls.hide_block(guild, role_block)
                await guild.system_channel.send(
                    f'{emojis.exclamation}`[RMS_ERROR] Ни одна из ролей не ссылается на блок {role_block.name}#{role_block.block_id}. '
                    f'Блок переведён в скрытый режим`')
                await block_message.delete()
            message_reactions = [react.emoji for react in block_message.reactions]
            for db_role in roles:
                ds_role = guild.get_role(db_role.role_id)
                if ds_role is None:
                    await guild.system_channel.send(
                        f'{emojis.exclamation}`[RMS_ERROR] Роль {db_role.name} не найдена! '
                        f'Роль удалена из RMS`')
                    db_role.delete_instance()
                    await cls.fix_block(role_block, db_role, block_message)
                    continue
            res, data, reacts = cls.gen_block_embed(role_block)
            if res:
                emb: disnake.Embed = data
                if emb.description.strip() != block_message.embeds[0].description.strip():
                    block_message = await block_message.edit(embed=emb)
                if reacts != message_reactions:
                    for react in reacts:
                        if react in message_reactions:
                            message_reactions.remove(react)
                            continue
                        else:
                            await block_message.add_reaction(react)
                    for r in message_reactions:
                        await block_message.clear_reaction(r)


class RoleCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.indexing.start()

    @commands.slash_command()
    async def disconnect_role(self, inter: disnake.CommandInteraction, role: disnake.Role):
        """Отключить роль от RMS"""
        res, data = RMS.disconnect_role(role)
        if res:
            await inter.send(f'{emojis.white_check_mark} `Роль удалена`')
        else:
            await inter.send(f'{emojis.exclamation}`{data}`')

    @commands.slash_command()
    @admin_permission_required
    async def remove_block(self, inter: disnake.CommandInteraction, block_id: int):
        """Удаление блока"""
        result, com = await RMS.remove_block(inter.guild, block_id)
        if result:
            await inter.send(f'{emojis.white_check_mark}`Блок #{block_id} успешно удалён`')
        else:
            await inter.send(f'При удалении блока произошла ошибка: {com}')

    @commands.slash_command()
    @admin_permission_required
    async def create_block(self, inter: disnake.CommandInteraction):
        """Создать блок ролей. ФОРМА ВВОДА"""
        await inter.response.send_modal(modal=BlockCreteModal())

    @commands.slash_command()
    @admin_permission_required
    async def connect_role(self, inter: disnake.CommandInteraction, role: disnake.Role, emoji: str, role_block_id: int):
        """Подключить роль к RMS"""
        result, info = RMS.connect_role(inter.guild, role, role_block_id, emoji)
        if result:
            await inter.send(f'{emojis.white_check_mark} `Роль добавлена!`')
        else:
            await inter.send(f'{emojis.exclamation}`При подключении произошла ошибка: {info}`')

    @commands.slash_command()
    @admin_permission_required
    async def blocks_list(self, inter: disnake.CommandInteraction):
        """Список блоков ролей в RMS"""
        await inter.send(embed=RMS.get_blocks_embed(inter.guild))

    @commands.slash_command()
    @admin_permission_required
    async def hide_block(self, inter: disnake.CommandInteraction, block_id: int):
        """Выключить блок"""
        role_block = database.RoleBlock.get_or_none(database.RoleBlock.block_id == block_id)
        if role_block is None:
            await inter.send(f"{emojis.exclamation}`Такого блока не существует`")
            return
        if role_block.block_message_id is None:
            await inter.send(f'{emojis.no_entry}`Блок уже скрыт!`')
            return
        RMS.hide_block(inter.guild, block_id)
        channel = self.bot.get_channel(role_block.block_channel_id)
        if channel is None:
            await inter.send(f"{emojis.exclamation}`Канал не найден`")
            return
        try:
            mes = await channel.fetch_message(role_block.block_message_id)
        except disnake.errors.NotFound:
            await inter.send(f"{emojis.exclamation}`Сообщение не найдено не найден`")
            return
        await mes.delete()
        await inter.send(f'{emojis.white_check_mark}`Блок {role_block.name}#{role_block.block_id} скрыт!`')

    @commands.slash_command()
    @admin_permission_required
    async def show_block(self, inter: disnake.CommandInteraction, block_id: int, channel: disnake.TextChannel):
        """Включить блок"""
        guild = inter.guild
        block = database.RoleBlock.get_or_none(database.RoleBlock.block_id == block_id,
                                               database.RoleBlock.guild == guild.id)
        if block is None:
            await inter.send(f'{emojis.exclamation} `Блок не найден`')
            return
        if block.block_message_id is not None:
            await inter.send(f'{emojis.exclamation}` Этот блок уже отображается!`')
            return
        connected_roles = [*database.Role.select().where(database.Role.linked_block == block)]
        if len(connected_roles) == 0:
            await inter.send(f'{emojis.exclamation} `К этому блоку не привязано ни одной роли`')
            return
        res, data = await RMS.send_block_message(block, channel)
        if res:
            await inter.send(f'{emojis.white_check_mark}`Выполнено!`')
        else:
            await inter.send(f'{emojis.exclamation}`Произошла ошибка:`{data}')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: disnake.RawReactionActionEvent):
        guild = self.bot.get_guild(event.guild_id)
        channel = self.bot.get_channel(event.channel_id)
        message = await channel.fetch_message(event.message_id)
        role_block = database.RoleBlock.get_or_none(database.RoleBlock.block_message_id == message.id)
        if role_block is None:
            return
        roles = {role.emoji: role.role_id for role in
                 database.Role.select().where(database.Role.linked_block == role_block)}
        try:
            role_id = roles[event.emoji.name]
        except KeyError:
            return
        ds_role = guild.get_role(role_id)
        if ds_role is None:
            return
        try:
            await event.member.add_roles(ds_role, reason='Выдана по реакции')
        except disnake.errors.Forbidden:
            await guild.system_channel.send(
                f'{emojis.exclamation}`[RMS_ERROR] Недостаточно прав для управления ролью`{ds_role.mention}` '
                f'Роль удалена из RMS`')
            res, data = RMS.disconnect_role(ds_role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, event: disnake.RawReactionActionEvent):
        guild = self.bot.get_guild(event.guild_id)
        channel = self.bot.get_channel(event.channel_id)
        message = await channel.fetch_message(event.message_id)
        role_block = database.RoleBlock.get_or_none(database.RoleBlock.block_message_id == message.id)
        if role_block is None:
            return
        roles = {role.emoji: role.role_id for role in
                 database.Role.select().where(database.Role.linked_block == role_block)}
        try:
            role_id = roles[event.emoji.name]
        except KeyError:
            return
        ds_role = guild.get_role(role_id)
        if ds_role is None:
            return
        member = guild.get_member(event.user_id)
        try:
            await member.remove_roles(ds_role, reason='Выдана по реакции')
        except disnake.errors.Forbidden:
            await guild.system_channel.send(
                f'{emojis.exclamation}`[RMS_ERROR] Недостаточно прав для управления ролью`{ds_role.mention}`. '
                f'Роль удалена из RMS`')
            RMS.disconnect_role(ds_role)

    @tasks.loop(seconds=10.0)
    async def indexing(self):
        for guild in self.bot.guilds:
            role_blocks = RMS.get_blocks_data(guild)
            if not role_blocks:
                continue
            for role_block in role_blocks:
                core.Bot.add_task(self.bot.loop.create_task(RMS.update_block(role_block)))


class BlockCreteModal(disnake.ui.Modal):
    def __init__(self):
        title = 'Создать новый блок ролей'
        self.title_input = disnake.ui.TextInput(
            label='Название',
            custom_id='name',
            style=disnake.TextInputStyle.short,
            required=True,
            min_length=3,
            max_length=15
        )
        self.color_input = disnake.ui.TextInput(
            label='Цвет в HEX',
            custom_id='color',
            style=disnake.TextInputStyle.short,
            required=True,
            min_length=6,
            max_length=7,
            placeholder='example: #ffffff'
        )
        components = [
            self.title_input,
            self.color_input
        ]

        super(BlockCreteModal, self).__init__(title=title, components=components)

    async def callback(self, interaction: disnake.ModalInteraction, /) -> None:
        name = interaction.text_values['name']
        color = interaction.text_values['color']
        RMS.new_block(interaction.guild, name=name, color=color)
        await interaction.send(f'{emojis.white_check_mark}`Блок {name} создан!`')


def setup(bot):
    bot.add_cog(RoleCommands(bot))
