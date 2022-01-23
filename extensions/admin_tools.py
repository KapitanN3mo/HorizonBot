import discord
from discord.ext import commands
from extensions.profile import ProfileModule
from modules.permissions import admin_permission_required
from assets import emojis


class AdminTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def add_xp(self, ctx: commands.Context, member: discord.Member, count: int):
        ProfileModule.update_xp(member, count)
        await ctx.send(f'{emojis.white_check_mark} `добавлено {count} очков опыта {member.display_name}`')

    @commands.command()
    @admin_permission_required
    async def remove_xp(self, ctx: commands.Context, member: discord.Member, count: int):
        ProfileModule.update_xp(member, -count)
        await ctx.send(f'{emojis.white_check_mark} `удалено {count} очков опыта {member.display_name}`')


def setup(bot):
    bot.add_cog(AdminTools(bot))