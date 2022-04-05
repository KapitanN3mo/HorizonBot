from disnake.ext import commands
import disnake

import database
from permissions import admin_permission_required
from assets import emojis


class EditableMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def send(self, ctx: commands.Context, channel: disnake.TextChannel, *, text):
        content = ctx.message.attachments
        content = [await c.to_file() for c in content]
        mes = await channel.send(text, files=content)
        database.TextBotMessage.insert(
            message_id=mes.id,
            guild_id=ctx.guild.id,
            channel_id=channel.id,
            author_id=database.User.get(database.User.guild_id == ctx.guild.id, database.User.user_id == ctx.author.id)
        ).execute()

    @commands.command()
    @admin_permission_required
    async def edit(self, ctx: commands.Context, channel: disnake.TextChannel, mes_id: int, *, text):
        try:
            message = await channel.fetch_message(mes_id)
        except disnake.errors.NotFound:
            await ctx.send(f'{emojis.exclamation}`Сообщение не найдено! Проверьте канал и ID сообщения`')
            return
        content = ctx.message.attachments
        content = [await c.to_file() for c in content]
        try:
            await message.edit(content=text, files=content, attachments=[])
        except disnake.errors.Forbidden:
            await ctx.send(f'{emojis.exclamation}`Отредактировать можно только сообщения отправленные ботом!`')


def setup(bot: commands.Bot):
    bot.add_cog(EditableMessage(bot))
