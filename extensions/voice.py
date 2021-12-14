import json
import discord
from discord.ext import commands
import database
from modules.datetime import get_msk_datetime


class VoiceModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        db_guild = database.Guilds.get_or_none(database.Guilds.guild_id == member.guild.id)
        db_user = database.Users.get_or_none(database.Users.user_id == member.id)
        if db_user is None:
            return
        if before.channel is None and after.channel is not None:
            db_user.voice_entry = get_msk_datetime()
            db_user.save()
            if after.channel.id == db_guild.private_voice:
                print(f'Create private from {member.name}')
                category = after.channel.category
                private_channel = await category.create_voice_channel(name=member.display_name,
                                                                      reason=f'Приватный канал по запросу {member.display_name}')
                overwrite = discord.PermissionOverwrite()
                overwrite.manage_channels = True
                await private_channel.set_permissions(member, overwrite=overwrite)
                db_private_channel = database.PrivateChannels()
                db_private_channel.channel_id = private_channel
                db_private_channel.owner_id = member.id
                db_private_channel.guild_id = member.guild.id
                db_private_channel.save()
                await member.move_to(private_channel)

        if before.channel is not None and after.channel is None:
            entry_time = db_user.voice_entry
            user = database.Users.get_or_none(database.Users.user_id == member.id)
            if user is None:
                return
            duration = (get_msk_datetime() - entry_time).seconds
            if duration > db_guild.minimum_voice_time:
                total_time = user.in_voice_time + duration
                user.in_voice_time = total_time
                voice_xp = (duration // 60) * db_guild.xp_voice_multiplier
            else:
                voice_xp = 0
            total_xp = user.xp + voice_xp
            user.xp = total_xp
            user.save()
            sys_info = json.loads(db_user.sys_info)
            if sys_info['send_dm_voice'] == 'true':
                hours = duration // 3600
                minutes = (duration - (hours * 3600)) // 60
                await member.send(
                    f'Вы общались {hours} часов {minutes} минут. Начислен опыт: {voice_xp} очков')
            db_private_channel = database.PrivateChannels.get_or_none(
                database.PrivateChannels.channel_id == before.channel.id)
            if db_private_channel is not None:
                clients = before.channel.members
                if not clients:
                    owner_name = discord.utils.get(before.channel.guild.members,
                                                   id=db_private_channel.owner_id)
                    print(f'Remove empty private channel. Owner {owner_name}')
                    await before.channel.delete(reason='Автоудаление пустого приватного канала')
                    db_private_channel.delete_instance()
        if before.channel is not None and after.channel is not None:
            if after.channel.id == db_guild.private_voice:
                print(f'Create private from {member.name}')
                category = after.channel.category
                private_channel = await category.create_voice_channel(name=member.display_name,
                                                                      reason=f'Приватный канал по запросу {member.display_name}')
                overwrite = discord.PermissionOverwrite()
                overwrite.manage_channels = True
                await private_channel.set_permissions(member, overwrite=overwrite)
                db_private_channel = database.PrivateChannels()
                db_private_channel.channel_id = private_channel
                db_private_channel.owner_id = member.id
                db_private_channel.guild_id = member.guild.id
                db_private_channel.save()
                await member.move_to(private_channel)
            db_private_channel = database.PrivateChannels.get_or_none(
                database.PrivateChannels.channel_id == before.channel.id)
            if db_private_channel is not None:
                clients = before.channel.members
                if not clients:
                    owner_name = discord.utils.get(before.channel.guild.members,
                                                   id=db_private_channel.owner_id)
                    print(f'Remove empty private channel. Owner {owner_name}')
                    await before.channel.delete(reason='Автоудаление пустого приватного канала')
                    db_private_channel.delete_instance()


def setup(bot):
    bot.add_cog(VoiceModule(bot))
