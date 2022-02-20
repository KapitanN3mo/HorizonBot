import discord
from permissions import admin_permission_required
from extensions.src import g_properties
from discord.ext import commands
import discord_components as dc
import uuid


class GuildsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def guild_menu(self, ctx: commands.Context):
        # session_id = uuid.uuid4()

        # action_buttons = [dc.Button(emoji='📝',
        #                             style=dc.ButtonStyle.blue,
        #                             custom_id=f'edit_{session_id}')]
        message = await ctx.send(embed=await self.gen_emb(ctx))  # components=action_buttons)
        # while True:
        #    interaction: dc.Interaction = await self.bot.wait_for('button_click')
        #    if interaction.user.id == ctx.author.id:
        #        if interaction.custom_id == f'edit_{session_id}':
        #            await message.edit(embed=await self.gen_emb(ctx),
        #                               components=await self.get_properties_selector(ctx))
        #            interaction: dc.Interaction = await self.bot.wait_for('button_click')

    async def gen_emb(self, ctx):
        emb = discord.Embed(title='Меню сервера', color=discord.Colour(0xA000CC))
        emb.set_thumbnail(url=ctx.guild.icon_url)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        for g_property in g_properties.get_guild_properties(ctx):
            emb.add_field(name=g_property.name, value=g_property.out())
        return emb

    async def get_properties_selector(self, ctx):
        pr = [g_property for g_property in g_properties.get_guild_properties(ctx) if g_property.editable]
        selector = dc.Select(placeholder='Настройки:',
                             options=[dc.SelectOption(label=p.name, value=p.out()) for p in pr])
        return [selector]


def setup(bot: commands.Bot):
    bot.add_cog(GuildsCommands(bot))
