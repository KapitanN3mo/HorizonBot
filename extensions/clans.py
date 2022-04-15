import datetime

import disnake
from disnake.ext import commands
import core
import database
from assets import clan_raid


class Clans(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.world = clan_raid.World
        #self.change_weather_task = self.bot.loop.create_task()

    # async def change_weather(self):
    #     while True:
    #         res = self.world.update_weather()
    #         if res is not None:
    #             for guild in self.bot.guilds:
    #                 db_guild: database.Guild = database.Guild.get_or_none(database.Guild.guild_id == guild.id)
    #                 if db_guild is None:
    #                     continue
    #                 clan_channel_id = db_guild.clan_channel
    #                 if db_guild is None:
    #                     continue
    #                 channel = guild.get_channel(clan_channel_id)
    #                 if channel is None:
    #                     continue
    #                 await channel.send()
    @commands.slash_command()
    async def create_clan(self, inter: disnake.CommandInteraction):
        await inter.response.send_modal(modal=CreateClanModal())


class CreateClanModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label='Название клана',
                custom_id='name',
                required=True,
                min_length=2,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label='Тэг клана',
                custom_id='tag',
                required=True,
                min_length=2,
                max_length=5,
            ),
            disnake.ui.TextInput(
                label='Цвет клана',
                custom_id='color',
                required=True,
                placeholder='В формате #ffffff',
                min_length=7,
                max_length=7,
            ),
            disnake.ui.TextInput(
                label='Ссылка на эмблему клана',
                custom_id='emblem_url',
                placeholder='Ссылка на картинку в ДИСКОРДЕ (начинается с https://cdn.discordapp.com/)',
                required=True,
                min_length=2,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label='Описание клана',
                custom_id='description',
                required=True,
                style=disnake.TextInputStyle.long
            )
        ]
        super(CreateClanModal, self).__init__(title='Создать клан', components=components)

    async def callback(self, interaction: disnake.ModalInteraction, /) -> None:
        clan_name = interaction.text_values['name_input']
        clan_tag = interaction.text_values['tag']
        clan_color = interaction.text_values['color']
        clan_emblem = interaction.text_values['emblem_url']
        clan_description = interaction.text_values['description']
        database.Clan.insert(
            guild=interaction.guild.id,
            owner=database.User.get(database.User.guild_id == interaction.guild_id,
                                    database.User.user_id == interaction.author.id),
            name=clan_name,
            tag=clan_tag,
            color=clan_color,
            description=clan_description,
            emblem=clan_emblem
        ).execute()
        emb = disnake.Embed(title=' ', description='Ваша заявка принята, ожидайте подтверждения администрации',
                            colour=disnake.Colour.green())
        emb.set_footer(text=f'Запрос на создание гильдии', icon_url=core.Bot.get_bot().user.display_avatar)
        emb.timestamp = datetime.datetime.now()
        await interaction.send(embed=emb)


def setup(bot):
    bot.add_cog(Clans(bot))
