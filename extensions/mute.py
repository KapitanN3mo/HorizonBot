import discord
from discord.ext import commands
import asyncio


class MuteModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def mute(self, ctx, user: discord.Member, time: float):
        try:
            mute_role = discord.utils.get(ctx.author.guild.roles, id=878788895570001970)
            await ctx.send(f':zipper_mouth: `Товарищ {user.mention} помолчит {time} минут`')
            await user.add_roles(mute_role)
            self.bot.loop.create_task(await self.automatic_unmute(user, mute_role, time))
        except Exception as ex:
            print(ex)

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def unmute(self, ctx, user: discord.Member):
        mute_role = discord.utils.get(ctx.author.guild.roles, id=878788895570001970)
        await user.remove_role(mute_role)
        await ctx.send(f':kissing_closed_eyes:`Товарищ {user.mention} помилован! Веди себя хорошо!`')

    async def automatic_unmute(self, user: discord.Member, role: discord.Role, time: float):
        mute_role = role
        await asyncio.sleep(time * 60)
        await user.remove_roles(mute_role)


def setup(bot):
    bot.add_cog(MuteModule(bot))
