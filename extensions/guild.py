import json
import discord
from assets import emojis
from discord.ext import commands
import database
from modules.permissions import admin_permission_required
from modules.guild_properties import *


class GuildsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def guild_menu(self, ctx: commands.Context):
        emb = discord.Embed(title='Меню сервера', color=discord.Colour(0xA000CC))
        emb.set_thumbnail(url=ctx.guild.icon_url)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        emb.add_field(name='Количество пользователей', value=GUserCount(ctx).out())
        emb.add_field(name='Администраторы', value=GAdmins(ctx).out())
        emb.add_field(name='Доступ к админ. командам',value=GAdminAccess(ctx).out())
        emb.add_field(name='Приватные каналы',value=GPrivateVoices(ctx).out())
        emb.add_field(name='Статистика', value=GStatInfo(ctx).out())
        emb.add_field(name='Канал для уведомлений',value=GNotifyChannel(ctx).out())
        emb.add_field(name='Минимальное время в канале для начисления опыта',value=)
        emb.add_field(name='Множитель для голосовых каналов', value=f'```{db_guild.xp_voice_multiplier}```')
        emb.add_field(name='Множитель для текстовых каналов', value=f'```{db_guild.xp_message_multiplier}```')
        message = await ctx.send(embed=emb)


def setup(bot: commands.Bot):
    bot.add_cog(GuildsCommands(bot))
