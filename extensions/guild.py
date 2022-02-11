import json

import discord
from assets import emojis
from discord.ext import commands

import database
from modules.permissions import admin_permission_required


class GuildsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def guild_menu(self, ctx: commands.Context):
        emb = discord.Embed(title='Меню сервера', color=discord.Colour(0xA000CC))
        emb.set_thumbnail(url=ctx.guild.icon_url)
        emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        user_counter = 0
        bot_counter = 0
        for member in ctx.guild.members:
            if member.bot:
                bot_counter += 1
            else:
                user_counter += 1
        emb.add_field(name='Количество пользователей', value=f'```👤:{user_counter} 🤖:{bot_counter}```')

        def check_admin(member):
            return True if member.guild_permissions.administrator and not member.bot else False

        emb.add_field(name='Администраторы',
                      value=' '.join([member.mention for member in ctx.guild.members if check_admin(member)]))
        db_guild: database.Guild = database.Guild.get(database.Guild.guild_id == ctx.guild.id)
        adm_access = []
        for user in json.loads(db_guild.admins):
            ds_user = self.bot.get_user(
                (database.User.get(database.User.user_db_id == user)).user_id)
            adm_access.append(ds_user.mention)
        emb.add_field(name='Доступ к админ. командам',
                      value=''.join(adm_access) if adm_access else f'```{emojis.no_entry_unicode} Нет```')
        emb.add_field(name='Приватные каналы',
                      value=f'```{emojis.white_check_mark_unicode} Включены```{self.bot.get_channel(db_guild.private_voice).mention}' if db_guild.private_voice is not None else f'```{emojis.no_entry_unicode} Выключены```')
        stat_info = ''
        if db_guild.statistics_category is None:
            stat_info = f'```{emojis.no_entry_unicode} Выключена```'
        else:
            stat_info += '```'
            s_info = json.loads(db_guild.statistics_info)
            for stat in s_info:
                if s_info[stat]['mode']:
                    stat_info += f'{emojis.white_check_mark_unicode} {stat}\n'
                else:
                    stat_info += f'{emojis.no_entry_unicode} {stat}\n'
            stat_info += '```'
        emb.add_field(name='Статистика', value=stat_info)
        emb.add_field(name='Канал для уведомлений',
                      value=f'```{emojis.white_check_mark_unicode}Есть```{self.bot.get_channel(db_guild.notify_channel).mention}' if db_guild.notify_channel is not None else f'```{emojis.no_entry_unicode} Нет```')
        emb.add_field(name='Минимальное время в канале для начисления опыта',
                      value='```' + str(db_guild.minimum_voice_time) + ' секунд```')
        emb.add_field(name='Множитель для голосовых каналов', value=f'```{db_guild.xp_voice_multiplier}```')
        emb.add_field(name='Множитель для текстовых каналов', value=f'```{db_guild.xp_message_multiplier}```')
        await ctx.send(embed=emb)


def setup(bot: commands.Bot):
    bot.add_cog(GuildsCommands(bot))
