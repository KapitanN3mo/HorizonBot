import disnake
from permissions import admin_permission_required
from extensions.bin import g_properties
from disnake.ext import commands
import uuid


class GuildsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def guild_menu(self, ctx: commands.Context):
        message = await ctx.send(embed=await self.gen_emb(ctx))

    async def gen_emb(self, ctx):
        emb = disnake.Embed(title='Меню сервера', color=disnake.Colour(0xA000CC))
        emb.set_thumbnail(url=ctx.guild.icon.url)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        for g_property in g_properties.get_guild_properties(ctx):
            emb.add_field(name=g_property.name, value=g_property.out())
        return emb


def setup(bot: commands.Bot):
    bot.add_cog(GuildsCommands(bot))
