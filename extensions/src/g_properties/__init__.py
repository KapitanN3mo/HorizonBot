from extensions.src.g_properties.guild_properties import *
from discord.ext import commands

g_properties = [
    GUserCount,
    GAdmins,
    GAdminAccess,
    GPrivateVoices,
    GStatInfo,
    GNotifyChannel,
    GMinVoiceTime,
    GVoiceMultiplier,
    GTextMultiplier
]


def get_guild_properties(ctx: commands.Context):
    return [obj(ctx) for obj in g_properties]
