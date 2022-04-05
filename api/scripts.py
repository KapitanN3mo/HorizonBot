import disnake
import core
import database


def get_user_admin_guilds(user_id: int):
    bot = core.Bot.get_bot()
    user = bot.get_user(user_id)
    if user is None:
        return None
    guilds = [bot.get_guild(guild_id) for guild_id in
              database.Guild.select().where(database.Guild.admins.contains(str(user_id)))]
    guilds = set(guilds)
    for guild in user.mutual_guilds:
        member = guild.get_member(user_id)
        if member.guild_permissions.administrator:
            guilds.add(guild)
    return guilds
