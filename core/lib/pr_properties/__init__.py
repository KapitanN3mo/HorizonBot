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


def get_profile_properties(inter: disnake.CommandInteraction, user: disnake.Member):
    return [obj(inter, user) for obj in p_properties]
