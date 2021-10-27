import logging
import discord
from discord.ext import commands
import os

logger = logging.getLogger('EVENTS')


class ServiceModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready!')
        logger.info('Бот успешно запущен!')

    @commands.has_role(901491325969522768)
    @commands.command()
    async def get_no_help(self, ctx):
        comm_list = self.bot.all_commands
        help_texts = os.listdir('help_texts')
        ok_help = []
        for command_name in comm_list:
            if f'{command_name}.txt' in help_texts:
                print(comm_list)
                ok_help.append(command_name)
        comm_list.pop('get_no_help')
        comm_list.pop('help')
        for name in ok_help:
            comm_list.pop(name)

        await ctx.send('```Файл справки не найден для команд:\n' + '\n'.join(comm_list) + '```')


def setup(bot):
    bot.add_cog(ServiceModule(bot))
