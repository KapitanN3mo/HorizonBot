from extensions.bin.g_properties.guild_properties import *
from disnake.ext import commands

g_properties = [
    GUserCount,
    GAdmins,
    GAdminAccess,
    GPrivateVoices,
    GNotifyChannel,
    GMinVoiceTime,
    GVoiceMultiplier,
    GTextMultiplier
]


def get_guild_properties(inter, parent_view):
    return [obj(inter, parent_view) for obj in g_properties]
