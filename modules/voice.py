import datetime
import json
import math
import discord
from discord.ext import commands
from componets import temp_file, get_msk_datetime, get_str_msk_datetime
from database import *
from componets import config


class VoiceModule(commands.Cog):
    voice_entry = {}
    private_channels = {}

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.User, before: discord.VoiceState,
                                    after: discord.VoiceState):
        if before.channel is None and after.channel is not None:
            self.voice_entry[member.id] = get_msk_datetime()
            if after.channel.id == int(config.get('Global', 'private_voice_channel')):
                print(f'Create private from {member.name}')
                category = after.channel.category
                owner = discord.utils.get(category.guild.members, id=member.id)
                private_channel = await category.create_voice_channel(name=owner.name,
                                                                      reason=f'Приватный канал по запросу {member.name}')
                overwrite = discord.PermissionOverwrite()
                overwrite.manage_channels = True
                await private_channel.set_permissions(owner, overwrite=overwrite)
                self.private_channels[private_channel.id] = owner.id
                await owner.move_to(private_channel)

        if before.channel is not None and after.channel is None:
            entry_time = self.voice_entry[member.id]
            cursor.execute(sql.SQL('SELECT in_voice_time FROM server_users WHERE id = {member_id}').format(
                member_id=sql.Literal(member.id)
            ))
            old_time = cursor.fetchone()
            if old_time is None:
                return
            else:
                old_time = float(old_time[0])
            duration = (get_msk_datetime().replace(tzinfo=None) - entry_time).seconds
            if duration > int(config.get('Profile', 'voice_minimum_time')):
                total_time = old_time + duration
                cursor.execute(
                    sql.SQL('UPDATE server_users SET in_voice_time = {total_time} WHERE id = {member_id}').format(
                        member_id=sql.Literal(member.id),
                        total_time=sql.Literal(total_time)
                    ))
                db.commit()
                xp_voice_multiplier = float(config.get('Profile', 'xp_voice_multiplier'))
                voice_xp = math.ceil(duration / 60) * xp_voice_multiplier
                cursor.execute(sql.SQL('SELECT xp FROM server_users WHERE id = {member_id}').format(
                    member_id=sql.Literal(member.id)
                ))
                before_xp = cursor.fetchone()[0]
                total_xp = before_xp + voice_xp
                cursor.execute(sql.SQL('UPDATE server_users SET xp = {total_xp} WHERE id = {member_id}').format(
                    total_xp=sql.Literal(total_xp),
                    member_id=sql.Literal(member.id)
                ))
                db.commit()
            else:
                voice_xp = 0
            cursor.execute(sql.SQL('SELECT sys_info FROM server_users WHERE id = {member_id}').format(
                member_id=sql.Literal(member.id)
            ))
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
            if before.channel.id in self.private_channels:
                clients = before.channel.members
                if not clients:
                    owner_name = discord.utils.get(before.channel.guild.members,
                                                   id=self.private_channels[before.channel.id])
                    print(f'Remove empty private channel. Owner {owner_name}')
                    await before.channel.delete(reason='Автоудаление пустого приватного канала')
        if before.channel is not None and after.channel is not None:
            if after.channel.id == int(config.get('Global', 'private_voice_channel')):
                print(f'Create private from {member.name}')
                category = after.channel.category
                owner = discord.utils.get(category.guild.members, id=member.id)
                private_channel = await category.create_voice_channel(name=owner.name,
                                                                      reason=f'Приватный канал по запросу {member.name}')
                overwrite = discord.PermissionOverwrite()
                overwrite.manage_channels = True
                await private_channel.set_permissions(owner, overwrite=overwrite)
                self.private_channels[private_channel.id] = owner.id
                await owner.move_to(private_channel)
            if before.channel.id in self.private_channels:
                clients = before.channel.members
                if not clients:
                    print(f'Remove empty private channel. Owner {self.private_channels[before.channel.id]}')
                    await before.channel.delete(reason='Автоудаление пустого приватного канала')


def setup(bot):
    bot.add_cog(VoiceModule(bot))
