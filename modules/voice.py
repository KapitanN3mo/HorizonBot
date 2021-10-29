import datetime
import json
import math
import discord
from discord.ext import commands
from componets import temp_file, get_msk_datetime, get_str_msk_datetime
from database import cursor, db
from componets import config


class VoiceModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.User, before: discord.VoiceState,
                                    after: discord.VoiceState):
        if before.channel is None and after.channel is not None:
            print('entry')
            try:
                temp_file.remove_section(str(member.id))
            except Exception as ex:
                print(ex)
            temp_file.add_section(str(member.id))
            temp_file.set(str(member.id), 'entry',
                          get_str_msk_datetime())
            temp_file.commit()
        if before.channel is not None and after.channel is None:
            entry_time = temp_file.get(str(member.id), 'entry')
            entry_time = datetime.datetime.strptime(entry_time, '%Y-%m-%d-%H-%M')
            cursor.execute(f'SELECT in_voice_time FROM server_users WHERE id = {member.id}')
            old_time = cursor.fetchone()
            if old_time is None:
                return
            else:
                old_time = float(old_time[0])
            duration = (get_msk_datetime().replace(tzinfo=None) - entry_time).seconds
            cursor.execute(f'UPDATE server_users SET in_voice_time = {old_time + duration} WHERE id = {member.id}')
            db.commit()
            xp_voice_multiplier = float(config.get('Profile', 'xp_voice_multiplier'))
            voice_xp = math.ceil(duration / 60) * xp_voice_multiplier
            cursor.execute(f'SELECT xp FROM server_users WHERE id = {member.id}')
            print(member.id)
            before_xp = cursor.fetchone()[0]
            print(before_xp)
            total_xp = before_xp + voice_xp
            cursor.execute(f'UPDATE server_users SET xp = {total_xp} WHERE id = {member.id}')
            db.commit()
            cursor.execute(f'SELECT sys_info FROM server_users WHERE id = {member.id}')
            res = cursor.fetchone()
            if res is None:
                print('Voice ошибка чтения из БД')
                return
            sys_info = json.loads(res[0])
            if sys_info['send_dm_voice'] == 'true':
                hours = duration // 3600
                minutes = (duration - (hours*3600)) // 60
                await member.send(
                    f'Вы общались {hours} часов {minutes} минут. Начислен опыт: {voice_xp} очков')


def setup(bot):
    bot.add_cog(VoiceModule(bot))
