import discord
from discord.ext import commands
import config
import json


class CreateStringlessEmbedModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role(config.admin_role)
    @commands.command()
    async def create_stringless_embed(self, ctx, channel: discord.TextChannel, *, data):
        if ctx.message.author.guild_permissions.administrator:
            data = data.replace('\n', '\\n')
            print(data)
            data = json.loads(data)
            title = data['title']
            text = data['text']
            color = data['color']
            if color == 'random':
                color = discord.Colour.random()
            else:
                color = int(color, 16)
            show_author = data['show_author']
            if show_author in ['true', 'True']:
                show_author = True
            else:
                show_author = False
            try:
                footer = data['footer'].replace('\\', '')
            except KeyError:
                footer = None

            embed = discord.Embed(title=title, color=color, description=text)
            if footer:
                embed.set_footer(text=footer)
            if show_author:
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await channel.send(embed=embed)
        else:
            raise commands.errors.MissingPermissions('administrator')

    @create_stringless_embed.error
    async def create_embed_error(self, ctx, error):
        if isinstance(error, KeyError):
            await ctx.send(':exclamation:`Ошибка в структуре аргумента!`')
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(':no_entry:`Требуются права администратора!`')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':exclamation:`Необходимо передать данные в JSON формате`')
        elif isinstance(error, json.decoder.JSONDecodeError):
            await ctx.send(':exclamation:`Ошибка в структуре аргумента!`')
        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send(f':exclamation:`Произошла внутренняя ошибка : {error}`')


def setup(bot):
    bot.add_cog(CreateStringlessEmbedModule(bot))
