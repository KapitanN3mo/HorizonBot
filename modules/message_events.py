import math
import discord
from discord.ext import commands
from database import cursor, db
from componets import config
import re
from modules.warn import WarnModule


class EventsModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return
        member = discord.utils.get(message.guild.members, id=message.author.id)
        admin_role = discord.utils.get(message.guild.roles, id=int(config.get('Global', 'admin_role')))
        # mat_check = mat_search(clear_message)
        # if mat_check:
        #     print(f'Обнаружен мат {mat_check}')
        #     warn_module = WarnModule(self.bot)
        #     self.bot.loop.create_task(warn_module.auto_warn(message.channel, message.author, 10,
        #                                                     f'Автоматическое предупреждение за мат! Сообщение: {message.content}'))
        #     cursor.execute(f'SELECT message_count,xp FROM server_users WHERE id = {message.author.id}')
        #     result = cursor.fetchone()
        #     if result is None:
        #         user_data = [message.author.id, 1, 1, 0, 'normal', '{}', '{"send_dm_voice":"false"}', 'none']
        #         cursor.execute(f'INSERT INTO server_users VALUES(?,?,?,?,?,?,?,?)', user_data)
        #         db.commit()
        #     else:
        #         old_xp = result[1]
        #         if old_xp < 1000:
        #             total_xp = 0
        #         else:
        #             total_xp = old_xp - 1000
        #         cursor.execute(
        #             f'''UPDATE server_users SET xp = {total_xp} WHERE id = {message.author.id}''')
        #         db.commit()
        #     await message.delete()
        # else:
        cursor.execute(f'SELECT message_count,xp FROM server_users WHERE id = {message.author.id}')
        result = cursor.fetchone()
        if result is None:
            user_data = [message.author.id, 1, 1, 0, 'normal', '{}', '{"send_dm_voice":"false"}', 'none']
            cursor.execute(f'INSERT INTO server_users VALUES(?,?,?,?,?,?,?,?)', user_data)
            db.commit()
        else:
            old_count = result[0]
            old_xp = result[1]
            old_count += 1
            xp_multiplier = int(config.get('Profile', 'xp_message_multiplier'))
            total_xp = int(xp_multiplier + old_xp)
            cursor.execute(
                f'''UPDATE server_users SET message_count = {old_count},xp = {total_xp} WHERE id = {message.author.id}''')
            db.commit()


def setup(bot):
    bot.add_cog(EventsModule(bot))
