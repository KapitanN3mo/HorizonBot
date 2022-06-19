import datetime
import disnake
from disnake.ext import commands

import permissions


class EmbedTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.buffer = {}  # буфер истории
        self.pointers = {}  # указатели на положение в истории
        self.max_history_length = 10
        self.embeds = {}  # хранит ID на выбранный embed

    async def find_message(self, inter):
        try:
            channel = self.bot.get_channel(inter.channel_id)
            msg = await channel.fetch_message(self.embeds[f'{inter.guild.id}{inter.user.id}'])
            return True, msg
        except KeyError:
            await inter.send('Сначала необходимо выбрать сообщение с помощью [select]', ephemeral=True)
            return False, None
        except Exception as ex:
            await inter.send(f'Ошибка: {ex}', ephemeral=True)
            return False, None

    def add_history(self, msg_id, emb: disnake.Embed):
        if msg_id in self.buffer:
            if len(self.buffer[msg_id]) == self.max_history_length:
                self.buffer[msg_id] = self.buffer[msg_id][1:]
            self.buffer[msg_id].append(emb)
            pointer = self.pointers[msg_id]
            if pointer != 0:
                for i in range(len(self.buffer[msg_id] - pointer), len(self.buffer[msg_id])):
                    del self.buffer[msg_id][i]
                self.pointers[msg_id] = 0
        else:
            self.buffer[msg_id] = [emb]
            self.pointers[msg_id] = 0

    @commands.slash_command()
    @permissions.admin_permission_required
    async def create_emb(self, inter: disnake.CommandInteraction, title: str, color: str):
        try:
            color = int(color.replace('#', '0x'), 16)
        except:
            await inter.send('Incorrect color')
            return

        emb = disnake.Embed(title=title, color=disnake.Color(color))
        msg = await inter.channel.send(embed=emb)
        self.embeds[f'{inter.guild.id}{inter.user.id}'] = msg.id
        self.add_history(msg.id, emb)
        await inter.send('ok,это сообщение автоматически было выбрано для редактирования', ephemeral=True)

    @commands.slash_command()
    @permissions.admin_permission_required
    async def set_description(self, inter, text: str):
        res, msg = await self.find_message(inter)
        if res:
            emb = msg.embeds[0]
            emb.description = text
            await msg.edit(embed=emb)
            self.add_history(msg.id, emb)
            await inter.send('ok', ephemeral=True)

    @commands.slash_command()
    @permissions.admin_permission_required
    async def set_footer(self, inter, show_author: bool, show_timestamp: bool, text: str = None):
        res, msg = await self.find_message(inter)
        if res:
            emb = msg.embeds[0]
            emb.set_footer(text=text if text is not None else disnake.Embed.Empty,
                           icon_url=self.bot.user.display_avatar.url if show_author else disnake.Embed.Empty)
            emb.timestamp = datetime.datetime.now() if show_timestamp else disnake.Embed.Empty
            await msg.edit(embed=emb)
            self.add_history(msg.id, emb)
            await inter.send('Ok', ephemeral=True)

    @commands.slash_command()
    @permissions.admin_permission_required
    async def append_desc(self, inter, text: str):
        res, msg = await self.find_message(inter)
        if res:
            emb = msg.embeds[0]
            emb.description += f'\n{text}'
            await msg.edit(embed=emb)
            self.add_history(msg.id, emb)
            await inter.send('ok', ephemeral=True)

    @commands.slash_command()
    @permissions.admin_permission_required
    async def set_color(self, inter, color: str):
        res, msg = await self.find_message(inter)
        if res:
            emb = msg.embeds[0]
            try:
                emb.color = disnake.Color(int(color.replace('#', '0x'), 16))
            except:
                await inter.send('Incorrect color')
            await msg.edit(embed=emb)
            self.add_history(msg.id, emb)
            await inter.send('Ok', ephemeral=True)

    @commands.slash_command()
    @permissions.admin_permission_required
    async def set_title(self, inter, title: str):
        res, msg = await self.find_message(inter)
        if res:
            emb = msg.embeds[0]
            emb.title = title
            await msg.edit(embed=emb)
            self.add_history(msg.id, emb)
            await inter.send('ok', ephemeral=True)

    @commands.slash_command()
    @permissions.admin_permission_required
    async def get_color(self, inter, msg_id: commands.LargeInt):
        try:
            channel = self.bot.get_channel(inter.channel_id)
            msg = await channel.fetch_message(msg_id)
        except Exception as ex:
            await inter.send(f'Ошибка {ex}')
            return
        try:
            await inter.send(msg.embeds[0].color)
        except Exception as ex:
            await inter.send(ex)

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def select(self, inter, msg_id: commands.LargeInt):
        self.embeds[f'{inter.guild.id}{inter.user.id}'] = msg_id
        res, msg = await self.find_message(inter)
        if res:
            await inter.send('Ok', ephemeral=True)
        else:
            del self.embeds[f'{inter.guild.id}{inter.user.id}']

    @commands.slash_command()
    @permissions.admin_permission_required
    async def set_description(self, inter, text: str):
        res, msg = await self.find_message(inter)
        if res:
            emb = msg.embeds[0]
            emb.description = text
            await msg.edit(embed=emb)
            self.add_history(msg.id, emb)
            await inter.send('ok', ephemeral=True)


def setup(bot):
    bot.add_cog(EmbedTools(bot))
