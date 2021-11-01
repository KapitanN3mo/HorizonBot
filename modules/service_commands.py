import json
import logging
import discord
from discord.ext import commands
import os


class ServiceModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_role(901491325969522768)
    @commands.command()
    async def get_no_help(self, ctx):
        comm_list = self.bot.all_commands
        help_texts = os.listdir('help_texts')
        ok_help = []
        for command_name in comm_list:
            if f'{command_name}.txt' in help_texts:
                ok_help.append(command_name)
        comm_list.pop('get_no_help')
        comm_list.pop('help')
        for name in ok_help:
            comm_list.pop(name)

        await ctx.send('```Файл справки не найден для команд:\n' + '\n'.join(comm_list) + '```')

    @commands.has_role(901491325969522768)
    @commands.command()
    async def info(self, ctx):
        try:
            temp_size = f"{os.path.getsize('temp.ini') / 1024:.{2}f}"
        except FileNotFoundError:
            temp_size = 'NotFound'
        try:
            msg_size = f"{os.path.getsize('reaction_roles.txt') / 1024:.{2}f}"
        except FileNotFoundError:
            msg_size = 'NotFound'
        message = f'''```Размер служебных файлов:
temp.ini - {temp_size} KB
reaction_roles.txt - {msg_size} KB```'''
        await ctx.send(message)


def setup(bot):
    bot.add_cog(ServiceModule(bot))
