from core.lib.pr_properties.profile_properties import *
from disnake.ext import commands
import disnake

p_properties = [
    MessageCount,
    XPCount,
    VoiceTime,
    JoinDatetime,
    WarnsCount,
    MarryPartner
]


def get_profile_properties(ctx: commands.Context, user: disnake.Member):
    return [obj(ctx, user) for obj in p_properties]
