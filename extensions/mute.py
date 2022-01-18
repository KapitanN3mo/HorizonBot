import discord
from discord.ext import commands
import asyncio

import database


class MuteModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def mute(self, ctx, user: discord.Member, time: float):
        try:
            target_guild = database.Guild.get_or_none(database.Guild.guild_id == ctx.guild.id)
            if target_guild.mute_role is None:
                await ctx.send('`Для сервера не настроена роль для мута`')
                return
            mute_role = discord.utils.get(ctx.guild.roles, id=target_guild.mute_role)
            if mute_role is None:
                await ctx.send('`Роль для мута настроена, однако найти её на сервере не удалось!`')
                return
            await user.add_roles(mute_role)
            self.bot.loop.create_task(await self.automatic_unmute(user, mute_role, time, ctx))
            await ctx.send(f':zipper_mouth: `Товарищ `{user.mention}` помолчит {time} минут`')
        except Exception as ex:
            print(ex)

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def unmute(self, ctx, user: discord.Member):
        target_guild = database.Guild.get_or_none(database.Guild.guild_id == ctx.guild.id)
        if target_guild is None:
            await ctx.send('`Для сервера не настроена роль для мута`')
            return
        mute_role = discord.utils.get(ctx.guild.roles, id=target_guild.mute_role)
        if mute_role is None:
            await ctx.send('`Роль для мута настроена, однако найти её на сервере не удалось!`')
            return
        await user.remove_role(mute_role)
        await ctx.send(f':kissing_closed_eyes:`Товарищ {user.mention} помилован! Веди себя хорошо!`')

    async def automatic_unmute(self, user: discord.Member, mute_role: discord.Role, time: float, ctx):
        await asyncio.sleep(time * 60)
        await user.remove_roles(mute_role)
        await ctx.send(f':kissing_closed_eyes:`Товарищ {user.mention} помилован! Веди себя хорошо!`')


def setup(bot):
    bot.add_cog(MuteModule(bot))
