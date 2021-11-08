import json
import logging
import discord
from discord.ext import commands
import os
from componets import get_msk_datetime, get_str_msk_datetime
from database import *

error_state = {1: 'Отправлено', 2: 'Принято', 3: 'Исправлено'}


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

    @commands.command()
    async def error_report(self, *, info):
        user = self.bot.get_user(357283670047850497)
        error_emb = discord.Embed(title='Сообщение о ошибке', colour=discord.Colour.red(), description=info)
        await user.send(error_emb)
        error_emb.add_field(name='Статус', value=error_state[1])
        error_emb.set_footer(text=get_str_msk_datetime())
        cursor.execute(sql.SQL('INSERT INTO error_rep(info,status,datetime) VALUE({info},{status},{datetime})').format(
            info=sql.Literal(info),
            status=sql.Literal(1),
            datetime=sql.Literal(get_str_msk_datetime())
        ))


def setup(bot):
    bot.add_cog(ServiceModule(bot))
