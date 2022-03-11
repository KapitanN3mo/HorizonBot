import disnake
from disnake.ext import commands
import pathlib
import os
from permissions import admin_permission_required


class HelpModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, command_name=None):
        help_embed = disnake.Embed(title=' ', colour=0x00FF80)
        functions = [{'use': 'h.fry {жертва} {на сколько кусочков нарезать}',
                      'desc': '**Хотите кого-то зажарить? Приятного аппетита!**'}]
        for command in functions:
            help_embed.add_field(name=command['desc'], value=command['use'], inline=False)
        help_embed.add_field(value='Знания о остальных командах вы должны добыть в бою',
                             name='Остальные команды:', inline=False)
        help_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=help_embed)

    @commands.command()
    @admin_permission_required
    async def admin_help(self, ctx, command_name=None):
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
            help_embed = disnake.Embed(title=f'Помощь для команды {command_name}', colour=0xFFFFFF,
                                       description=help_text)
            await ctx.send(embed=help_embed)

        else:
            comm = self.bot.all_commands
            help_text = '\n'.join(comm)
            help_embed = disnake.Embed(title=f'Список команд', colour=0xFFFFFF, description=help_text)
            await ctx.send(embed=help_embed)


def setup(bot):
    bot.add_cog(HelpModule(bot))
