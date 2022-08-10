import json
import disnake
from disnake.ext import commands

import core.log
from core.events import Events
from core.profile import ProfileModule


class Indexing(commands.Cog):
    log = core.log.Logger('INDEXING')

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        Events.connect_on_ready(self.start_indexing)

    async def start_indexing(self):
        new_user_count = 0
        new_guild_count = 0
        guilds = self.bot.guilds
        for guild_counter in range(len(guilds)):
            guild = guilds[guild_counter]
            result = ProfileModule.create_guild_profile(guild)
            if result == 1:
                new_guild_count += 1
            for user_counter in range(len(guild.members)):
                user = guild.members[user_counter]
                # if user.id == self.bot.user.id:
                #    continue
                # print(f'{guild} -> {user.display_name}')
                result = ProfileModule.create_profile(user)
                if result == 1:
                    new_user_count += 1
        self.log.info(f'Новые пользователи: {new_user_count}')
        self.log.info(f'Новые гильдии: {new_guild_count}')
        # with open('settings.json', 'r') as sf:
        #     developer = disnake.utils.get(self.bot.users, id=json.load(sf)['dev_id'])
        #     await developer.send(embed=disnake.Embed(title='Данные индексации',
        #                                              description=f'Новые пользователи: {new_user_count}'
        #                                                          f'\nНовые гильдии: {new_guild_count}',
        #                                              colour=disnake.Colour.random()))


def setup(bot):
    bot.add_cog(Indexing(bot))
