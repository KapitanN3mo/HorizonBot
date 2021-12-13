import datetime
import json
import math
import discord
from discord.ext import commands
import database
from modules.datetime import get_msk_datetime
from database import *


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
            user = database.Users.get_or_none(database.Users.user_id == member.id)
            if user is None:
                return
            duration = (get_msk_datetime().replace(tzinfo=None) - entry_time).seconds
            if duration > int(config.get('Profile', 'voice_minimum_time')):
                total_time = user.in_voice_time + duration
                user.in_voice_time = total_time
                xp_voice_multiplier = float(config.get('Profile', 'xp_voice_multiplier'))
                voice_xp = (duration // 60) * xp_voice_multiplier
                total_xp = user.xp + voice_xp
                user.xp = total_xp
                user.save()
            else:
                voice_xp = 0
            sys_info = json.loads(user.sys_info)
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
