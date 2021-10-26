import discord
from discord.ext import commands
import pathlib
import os


class HelpModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self,ctx, command_name=None):
        if command_name is not None:
            help_texts = os.listdir('help_texts')
            if f'{command_name}.txt' in help_texts:
                path = pathlib.Path('help_texts', f'{command_name}.txt')
                with open(path, 'r', encoding='utf-8') as text:
                    help_text = ''.join(text.readlines())
            else:
                if command_name in self.bot.all_commands:
                    help_text = '`Команда существует, но справка для неё отсутствует`'
                else:
                    help_text = '`Команда не найдена`'
            help_embed = discord.Embed(title=f'Помощь для команды {command_name}', colour=0xFFFFFF,
                                       description=help_text)
            await ctx.send(embed=help_embed)

        else:
            comm = self.bot.all_commands
            help_text = '\n'.join(comm)
            help_embed = discord.Embed(title=f'Список команд', colour=0xFFFFFF, description=help_text)
            await ctx.send(embed=help_embed)


def setup(bot):
    bot.add_cog(HelpModule(bot))
