import json
import disnake
from disnake.ext import commands
import core
import database
from dt import datetime_format
import datetime
from core.lib import pr_properties

default_sys_info = {
    'send_dm_voice': False
}


class ProfileModule(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def top(self, inter: disnake.CommandInteraction):
        """Самые крутые обитают здесь!"""
        users = database.User.select().where(database.User.guild_id == inter.guild.id) \
            .order_by(-database.User.xp) \
            .limit(20)
        emb = disnake.Embed(title='ТОП-20', color=disnake.Colour(0xFF9CFF), description='')
        emb.set_footer(text=f'Центр статистики имени {self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
        counter = 1
        for user in users:
            ds_user = self.bot.get_user(user.user_id)
            if counter == 1:
                emb.description += "🥇"
            elif counter == 2:
                emb.description += "🥈"
            elif counter == 3:
                emb.description += "🥉"
            else:
                emb.description += "🎖"
            emb.description += f'[`{counter}`]:{ds_user.mention} - `{user.xp}`\n'
            counter += 1
        await inter.send(embed=emb)

    @commands.slash_command()
    async def profile(self, inter: disnake.CommandInteraction, user: disnake.Member = None):
        """Информация о тебе, солнце!"""
        if user == self.bot.user:
            await inter.send('🕵️ `Информация находиться под грифом "Перед прочтением съесть!".... Съел!`')
            return
        if user is None:
            user = inter.author
        embed = disnake.Embed(title=' ', colour=user.colour, description=user.mention)
        for pr in pr_properties.get_profile_properties(inter, user):
            embed.add_field(name=pr.name, value=pr.out(), inline=pr.inline)
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)
        await inter.send(embed=embed)

    @classmethod
    def update_xp(cls, user: disnake.Member, xp: int):
        bot = core.Bot.get_bot()
        try:
            if user.id == bot.user.id:
                return
        except AttributeError:
            return
        user_data = database.User.get_or_none(database.User.user_id == user.id,
                                              database.User.guild_id == user.guild.id)
        if user_data is None:
            cls.create_profile(user)
            user_data = database.User.get(database.User.user_id == user.id, database.User.guild_id == user.guild.id)
        current_xp_count = user_data.xp
        new_xp_count = current_xp_count + xp
        user_data.xp = new_xp_count
        user_data.save()

    @classmethod
    def update_messages_count(cls, user: disnake.Member, msg: int):
        bot = core.Bot.get_bot()
        if user.id == bot.user.id:
            return
        try:
            user_data = database.User.get_or_none(database.User.user_id == user.id,
                                                  database.User.guild_id == user.guild.id)
        except AttributeError:
            return
        if user_data is None:
            cls.create_profile(user)
            user_data = database.User.get(database.User.user_id == user.id, database.User.guild_id == user.guild.id)
        current_msg_count = user_data.message_count
        new_msg_count = current_msg_count + msg
        user_data.message_count = new_msg_count
        user_data.save()

    @classmethod
    def create_profile(cls, user: disnake.Member):
        try:
            database.User.insert(user_id=user.id,
                                 guild_id=user.guild.id,
                                 message_count=0,
                                 xp=0,
                                 in_voice_time=0,
                                 discord_name=user.name).execute()
            return 1
        except:
            return 0

    @classmethod
    def create_guild_profile(cls, guild: disnake.Guild):
        try:
            database.Guild.insert(guild_id=guild.id,
                                  name=guild.name,
                                  admins=json.dumps([])).execute()
            return 1
        except:
            return 0


def setup(bot: commands.Bot):
    bot.add_cog(ProfileModule(bot))
