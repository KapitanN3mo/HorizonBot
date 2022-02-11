import json
import discord
from discord.ext import commands
import database
from modules.datetime import get_msk_datetime
from assets import emojis
from modules.permissions import admin_permission_required


class VoiceModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def enable_private_voice(self, ctx: commands.Context, *, name):
        db_guild = database.Guild.get_or_none(database.Guild.guild_id == ctx.guild.id)
        if db_guild is None:
            return
        if db_guild.private_voice is None:
            category = await ctx.guild.create_category('[СОЗДАТЬ ПРИВАТ]')
            channel = await ctx.guild.create_voice_channel(name, reason='Канал для создания приваток',
                                                           category=category)
            db_guild.private_voice = channel.id
            db_guild.save()
            await ctx.send(f'{emojis.white_check_mark} `Голосовой канал создан!`')
        else:
            await ctx.send(f'{emojis.exclamation} `Приватные каналы уже включены на вашем сервере`')
            await ctx.send(f'`Вы можете отключить их при помощи команды [disable_private_voice]`')

    @commands.command()
    @admin_permission_required
    async def disable_private_voice(self, ctx: commands.Context):
        db_guild = database.Guild.get_or_none(database.Guild.guild_id == ctx.guild.id)
        if db_guild is None:
            return
        if db_guild.private_voice is not None:
            p_channels = database.PrivateChannel.select().where(database.PrivateChannel.guild_id == ctx.guild.id)
            for p_channel in p_channels:
                channel = ctx.guild.get_channel(p_channel.channel_id)
                try:
                    await channel.delete()
                except Exception as ex:
                    print(ex)
            create_channel = ctx.guild.get_channel(db_guild.private_voice)
            category = create_channel.category
            if category is not None:
                await category.delete()
            try:
                await create_channel.delete()
            except Exception as ex:
                print(ex)
            db_guild.private_voice = None
            db_guild.save()
            await ctx.send(f'{emojis.white_check_mark}`Удаление завершено, приватные каналы отключены!`')
        else:
            await ctx.send(f'{emojis.exclamation}`Приватные каналы уже отключены!`')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        db_guild = database.Guild.get_or_none(database.Guild.guild_id == member.guild.id)
        db_user = database.User.get_or_none(database.User.user_id == member.id)
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
                database.PrivateChannel.insert(channel_id=private_channel.id,
                                               owner_id=database.User.get(database.User.user_id == member.id,
                                                                          database.User.guild_id == member.guild.id),
                                               guild_id=member.guild.id).execute()
                await member.move_to(private_channel)

        if before.channel is not None and after.channel is None:
            entry_time = db_user.voice_entry
            user = database.User.get_or_none(database.User.user_id == member.id,
                                             database.User.guild_id == member.guild.id)
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
                await member.send(embed=discord.Embed(title='Начисление опыта', colour=discord.Color.random(),
                                                      description=f'Вы общались {hours} часов {minutes} минут. '
                                                                  f'Начислен опыт: {voice_xp} очков'))
            db_private_channel = database.PrivateChannel.get_or_none(
                database.PrivateChannel.channel_id == before.channel.id)
            if db_private_channel is not None:
                clients = before.channel.members
                if not clients:
                    owner_name = discord.utils.get(before.channel.guild.members,
                                                   id=db_private_channel.owner_id.user_id)
                    print(f'Remove empty private channel. Owner {owner_name}')
                    try:
                        await before.channel.delete(reason='Автоудаление пустого приватного канала')
                    except:
                        pass
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
                db_private_channel = database.PrivateChannel()
                db_private_channel.channel_id = private_channel
                db_private_channel.owner_id = member.id
                db_private_channel.guild_id = member.guild.id
                db_private_channel.save()
                await member.move_to(private_channel)
            db_private_channel = database.PrivateChannel.get_or_none(
                database.PrivateChannel.channel_id == before.channel.id)
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
