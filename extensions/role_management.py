import disnake
from disnake.ext import commands
from permissions import admin_permission_required
from assets import emojis
import database
import extensions.bin.role_block_styles


class RMS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @classmethod
    def add_role(cls, role: disnake.Role):
        try:
            database.Role.insert(
                role_id=role.id,
                guild=role.guild.id,
                name=role.name,
                color=role.color,
                having_users='[]'
            ).execute()
            return True, None
        except Exception as ex:
            return False, str(ex)

    @classmethod
    def connect_role(cls, role: disnake.Role, block_id: int):
        db_role = database.Role.get_or_none(database.Role.role_id == role.id)
        if db_role is None:
            result, info = cls.add_role(role)
            if result is False:
                return False, f'Ошибка БД: {info}'
        db_block = database.RoleBlock.get_or_none(database.RoleBlock.block_id == block_id)
        if db_block is None:
            return False, 'Блок не найден'
        db_role.linked_block = db_block
        db_role.save()
        return True, None

    @classmethod
    def set_custom_emoji(cls, role: disnake.Role, emoji: str):
        db_role = database.Role.get_or_none(database.Role.role_id == role.id)
        if db_role is None:
            return False, 'Такой роли нет в RMS'
        db_role.custom_emojis = emoji
        db_role.save()
        return True, None

    @classmethod
    def reset_custom_emoji(cls, role: disnake.Role):
        db_role = database.Role.get_or_none(database.Role.role_id == role.id)
        if db_role is None:
            return False, 'Такой роли нет в RMS'
        db_role.custom_emojis = None
        db_role.save()
        return True

    @classmethod
    def new_block(cls, guild: disnake.Guild, name: str, color: str):
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
    def get_blocks(cls, guild: disnake.Guild):
        emb = disnake.Embed(title=f'Список блоков для {guild.name}')
        for block in database.RoleBlock.select().where(database.RoleBlock.guild == guild.id):
            connected_role_count = database.Role.get()
            row = ''

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: disnake.RawReactionActionEvent):
        pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, event: disnake.RawReactionActionEvent):
        pass

    def indexing(self):
        pass


class RoleCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    @admin_permission_required
    async def mark_as_roles_chat(self, inter: disnake.CommandInteraction):
        guild = inter.guild
        db_guild = database.Guild.get(database.Guild.guild_id == guild.id)
        db_guild.role_channel = inter.channel_id
        db_guild.save()
        await inter.send(f'{emojis.white_check_mark}`Теперь выдача ролей будет производится в этом чате`')

    @commands.slash_command()
    @admin_permission_required
    async def create_block(self, inter: disnake.CommandInteraction):
        """Создать блок ролей. ФОРМА ВВОДА"""
        await inter.response.send_modal(modal=BlockCreteModal())

    @commands.slash_command()
    @admin_permission_required
    async def connect_role(self, inter: disnake.CommandInteraction, role: disnake.Role, role_block_id: int):
        """Подключить роль к RMS"""
        result, info = RMS.connect_role(role, role_block_id)
        if result:
            await inter.send(f'{emojis.white_check_mark} `Роль добавлена!`')
        else:
            await inter.send(f'{emojis.exclamation}`При подключении произошла ошибка: {info}`')


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
        database.RoleBlock.insert(
            name=name,
            color=color,
            style='numeric',
            guild=interaction.guild_id
        ).execute()
        await interaction.send(f'{emojis.white_check_mark}`Блок {name} создан!`')


def setup(bot):
    bot.add_cog(RoleCommands(bot))
