import discord
from discord.ext import commands
import json
import datetime
import random
from discord_components import Button, ButtonStyle
import math
import asyncio

from modules.datetime import get_msk_datetime
from modules.permissions import admin_permission_required


class PollModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_permission_required
    async def create_poll(self, ctx, channel: discord.TextChannel, *, poll_info: str):
        poll_info = json.loads(poll_info)
        poll_variants = poll_info['variants']
        poll_time = poll_info['time']
        poll_author = poll_info['author']
        poll_body = ''
        reaction_list = []
        for variant in poll_variants:
            text = variant['text']
            emoji = variant['emoji']
            reaction_list.append(emoji)
            poll_body += f'{emoji} - {text}\n'
        embed = discord.Embed(title='Голосование', colour=discord.Colour.random(), description=poll_body)
        if poll_author in ['True', 'true']:
            author = ctx.message.author
            embed.set_author(name=author, icon_url=author.avatar_url)
        time = datetime.datetime(int(poll_time['year']), int(poll_time['month']), int(poll_time['day']),
                                 int(poll_time['hour']),
                                 int(poll_time['minute']))
        if time < get_msk_datetime().replace(tzinfo=None):
            raise Exception('Некорректное вренмя!')
        poll_id = random.randint(100000, 999999)
        embed.set_footer(text=f'ID #{poll_id} Время окончания: -  {time}')
        message = await channel.send(embed=embed)
        for reaction in reaction_list:
            await message.add_reaction(reaction)
        delay = (time - get_msk_datetime().replace(tzinfo=None)).seconds
        comp = [[
            Button(style=ButtonStyle.green, label='Продолжить', custom_id='confirm'),
            Button(style=ButtonStyle.red, label='Отмена', custom_id='cancel')
        ]]
        msg = f':exclamation: Вы уверены, что хотите установить таймер на {delay // 60} минут {delay % 60} секунд?'
        if delay // 60 > 60:
            msg += f'(Это {math.ceil(delay / 60 / 60)} часа!)'
        await ctx.send(msg, components=comp)
        confirm_response = await self.bot.wait_for('button_click')
        if confirm_response.author == ctx.message.author and confirm_response.channel == ctx.message.channel:
            if confirm_response.component.label == 'Продолжить':
                await confirm_response.respond(content='ОК :ok_hand:')
                await asyncio.sleep(delay)
                poll_report = ''
                message = discord.utils.get(self.bot.cached_messages, id=message.id)
                emb = discord.Embed(title=f'Результат опроса #{poll_id}', colour=discord.Colour.random())
                for react in message.reactions:
                    poll_text = 'Текст не найден'
                    for var in poll_variants:
                        if var['emoji'] == react.emoji:
                            poll_text = var['text']
                    poll_report += f'{poll_text} - {len(await react.users().flatten())}\n'
                emb.add_field(name='Итого:', value=poll_report)
                await ctx.message.channel.send(embed=emb)
            elif confirm_response.component.label == 'Отмена':
                await confirm_response.respond(content=':no_entry: Отменено!')

    @create_poll.error
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
    bot.add_cog(PollModule(bot))
