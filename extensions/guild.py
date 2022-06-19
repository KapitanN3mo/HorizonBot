from assets import emojis
import disnake
from permissions import admin_permission_required
from extensions.src import g_properties
from disnake.ext import commands
from typing import List


class GuildsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    @admin_permission_required
    async def guild_menu(self, inter: disnake.CommandInteraction):
        v = GuildMenuView(inter)
        await inter.send(view=v, embed=v.emb)


class GuildMenuView(disnake.ui.View):
    def __init__(self, inter: disnake.CommandInteraction):
        super(GuildMenuView, self).__init__()
        self.inter = inter
        self.original_inter = inter
        self.prp: List[g_properties.GProperty] = []
        self.emb = disnake.Embed()
        self.mode = 'main'
        self.update_properties()
        self.render()
        self.gen_emb()
        self.author = self.inter.author

    def update_properties(self):
        self.prp = [g_property for g_property in g_properties.get_guild_properties(self.inter, self)]

    async def update_message(self):
        self.render()
        await self.inter.edit_original_message(view=self, embed=self.emb)

    def render(self):
        self.children.clear()
        self.update_properties()
        self.gen_emb()
        if self.mode == 'main':
            self.add_item(EditButton(self))
        elif self.mode == 'edit':
            for bt in self.gen_edit_buttons():
                self.add_item(bt)
            self.add_item(BackButton(self))

    def gen_emb(self):
        emb = disnake.Embed(title='Меню сервера', color=disnake.Colour(0xA000CC))
        emb.set_thumbnail(url=self.inter.guild.icon.url)
        emb.set_author(name=self.inter.author.display_name, icon_url=self.inter.author.display_avatar.url)
        for g_property in self.prp:
            emb.add_field(name=g_property.name, value=g_property.out())
        self.emb = emb

    def gen_edit_buttons(self):
        buttons = []
        for g_prop in self.prp:
            if g_prop.editable:
                buttons.append(ModalCallButton(g_prop, self))
        return buttons


class BackButton(disnake.ui.Button):
    def __init__(self, parent_view: GuildMenuView):
        super(BackButton, self).__init__()
        self.style = disnake.ButtonStyle.red
        self.emoji = '🔙'
        self.parent_view = parent_view

    async def callback(self, interaction: disnake.MessageInteraction):
        if interaction.author == self.parent_view.author:
            await interaction.response.defer(with_message=False)
            self.parent_view.mode = 'main'
            self.parent_view.render()
            await interaction.edit_original_message(view=self.parent_view, embed=self.parent_view.emb)


class EditButton(disnake.ui.Button):
    def __init__(self, view: GuildMenuView):
        super(EditButton, self).__init__()
        self.style = disnake.ButtonStyle.gray
        self.emoji = '📝'
        self.parent_view = view

    async def callback(self, interaction: disnake.MessageInteraction):
        if interaction.author == self.parent_view.author:
            await interaction.response.defer(with_message=False)
            self.parent_view.mode = 'edit'
            self.parent_view.render()
            await interaction.edit_original_message(view=self.parent_view, embed=self.parent_view.emb)


class ModalCallButton(disnake.ui.Button):
    def __init__(self, prop: g_properties.GProperty, parent_view: GuildMenuView):
        super(ModalCallButton, self).__init__()
        self.parent_view = parent_view
        self.prop = prop
        self.label = prop.name
        self.style = disnake.ButtonStyle.gray

    async def callback(self, interaction: disnake.MessageInteraction):
        if interaction.author == self.parent_view.author:
            await interaction.response.send_modal(NewValueModal(self.prop, self.parent_view))


class NewValueModal(disnake.ui.Modal):
    def __init__(self, prop: g_properties.GProperty, parent_view: GuildMenuView):
        self.prop = prop
        self.parent_view = parent_view
        components = [disnake.ui.TextInput(
            label='Введите новое значение',
            custom_id='new_value',
            value=prop.value(),
            required=True
        )]
        super(NewValueModal, self).__init__(title='Новое значение', components=components)

    async def callback(self, interaction: disnake.ModalInteraction, /) -> None:
        res = self.prop.set(interaction.text_values['new_value'])
        if res:
            await interaction.response.defer(with_message=False)
            await interaction.delete_original_message()
            await self.parent_view.update_message()
        else:
            await interaction.send(f'{emojis.exclamation} `Ошибка при обновлении значения`')


def setup(bot: commands.Bot):
    bot.add_cog(GuildsCommands(bot))
