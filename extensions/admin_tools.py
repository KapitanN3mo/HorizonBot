import disnake
from disnake.ext import commands
from core.profile import ProfileModule
from permissions import admin_permission_required
from assets import emojis


class AdminTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    @admin_permission_required
    async def add_xp(self, inter: disnake.CommandInteraction, member: disnake.Member, count: int):
        """Добавить опыт"""
        ProfileModule.update_xp(member, count)
        await inter.send(f'{emojis.white_check_mark} `добавлено {count} очков опыта {member.display_name}`')

    @commands.slash_command()
    @admin_permission_required
    async def remove_xp(self, inter: disnake.CommandInteraction, member: disnake.Member, count: int):
        """Удалить опыт"""
        ProfileModule.update_xp(member, -count)
        await inter.send(f'{emojis.white_check_mark} `удалено {count} очков опыта {member.display_name}`')

    @commands.slash_command()
    @admin_permission_required
    async def clear_chat(self, inter: disnake.CommandInteraction, count: int):
        channel = inter.guild.get_channel(inter.channel_id)
        await inter.response.defer()
        original_msg = await inter.original_message()
        await channel.purge(limit=count, check=lambda msg: msg.id != original_msg.id)
        await inter.send(f'{emojis.white_check_mark} `Удалено {count} сообщений`')
        await inter.delete_original_message(delay=5)


def setup(bot):
    bot.add_cog(AdminTools(bot))
