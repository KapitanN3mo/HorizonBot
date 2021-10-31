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
            try:
                temp_file.remove_section(str(member.id))
            except Exception as ex:
                print(ex)
            temp_file.add_section(str(member.id))
            temp_file.set(str(member.id), 'entry',
                          get_str_msk_datetime())
            temp_file.commit()
            print(after.channel.id)
            if after.channel.id == int(config.get('Global', 'private_voice_channel')):
                print('create private')
                category = after.channel.category
                owner = discord.utils.get(category.guild.members, id=member.id)
                private_channel = await category.create_voice_channel(name=owner.name,
                                                                      reason=f'Приватный канал по запросу {member.name}')
                overwrite = discord.PermissionOverwrite()
                overwrite.manage_channels = True
                await private_channel.set_permissions(owner, overwrite=overwrite)
                if not temp_file.has_section('private'):
                    temp_file.add_section('private')
                temp_file.set('private', str(private_channel.id), str(owner.id))
                temp_file.commit()
                await owner.move_to(private_channel)

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
                minutes = (duration - (hours * 3600)) // 60
                await member.send(
                    f'Вы общались {hours} часов {minutes} минут. Начислен опыт: {voice_xp} очков')
            if temp_file.has_section('private'):
                if temp_file.has_option('private', str(before.channel.id)):
                    clients = before.channel.members
                    if not clients:
                        print('remove_private')
                        await before.channel.delete(reason='Автоудаление пустого приватного канала')
        if before.channel is not None and after.channel is not None:
            if after.channel.id == int(config.get('Global', 'private_voice_channel')):
                print('create private')
                category = after.channel.category
                owner = discord.utils.get(category.guild.members, id=member.id)
                private_channel = await category.create_voice_channel(name=owner.name,
                                                                      reason=f'Приватный канал по запросу {member.name}')
                overwrite = discord.PermissionOverwrite()
                overwrite.manage_channels = True
                await private_channel.set_permissions(owner, overwrite=overwrite)
                if not temp_file.has_section('private'):
                    temp_file.add_section('private')
                temp_file.set('private', str(private_channel.id), str(owner.id))
                temp_file.commit()
                await owner.move_to(private_channel)
            if temp_file.has_section('private'):
                if temp_file.has_option('private', str(before.channel.id)):
                    clients = before.channel.members
                    if not clients:
                        print('remove_private')
                        await before.channel.delete(reason='Автоудаление пустого приватного канала')


def setup(bot):
    bot.add_cog(VoiceModule(bot))
