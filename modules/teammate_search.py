import json
import os

import discord
from discord.ext import commands
from componets import config, convert_number_to_emoji
from database import *


class GameReactModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.add_reaction_listener = None
        self.remove_reaction_listener = None
        self.role_data = None
        self.load_role_data()

    admin_role = int(config.get('Global', 'admin_role'))

    @commands.has_role(admin_role)
    @commands.command()
    async def game_role_embed(self, ctx: commands.Context, channel: discord.TextChannel, *,
                              data: str):
        emb_data = json.loads(data)
        guild = ctx.author.guild
        title = emb_data['title']
        color = int(emb_data['color'], 16)
        games = sorted(emb_data['games'])
        text = ''
        counter = 1
        save_data = []
        emojis = {}
        for game in games:
            game = game.replace('\\', '')
            check_role = discord.utils.get(guild.roles, name=game)
            if check_role is None:
                game_role = await guild.create_role(name=game, reason=f'Автоматичская роль игры {game}',
                                                    colour=discord.Colour.default(), mentionable=True)
            else:
                game_role = check_role
            emoji = convert_number_to_emoji(counter)
            text += f'{emoji}-{game_role.mention}\n'
            emojis[emoji] = game_role.id
            counter += 1
            if counter == 10:
                embed = discord.Embed(title=title, colour=color, description=text)
                msg = await channel.send(embed=embed)
                for em in emojis:
                    await msg.add_reaction(em)
                save_data.append({'message_id': msg.id, 'info': emojis})
                text = ''
                counter = 1
                emojis = {}
        if text != '':
            embed = discord.Embed(title=title, colour=color, description=text)
            msg = await channel.send(embed=embed)
            for em in emojis:
                await msg.add_reaction(em)
            save_data.append({'message_id': msg.id, 'info': emojis})
        self.save_role_data(save_data)

    @commands.has_role(admin_role)
    @commands.command()
    async def remove_role_embed(self, ctx: commands.Context, channel: discord.TextChannel, message_id: int):
        channel = discord.utils.get(ctx.author.guild.channels, id=channel.id)
        message_to_remove = await channel.fetch_message(message_id)
        if message_to_remove is None:
            await ctx.send('```Ой, произошла ошибка! Не удлаось найти сообщение!```')
            return
        cursor.execute(sql.SQL('SELECT * FROM react_role WHERE id = {message_to_remove_id}').format(
            message_to_remove_id=sql.Literal(message_to_remove.id)
        ))
        res = cursor.fetchone()
        if res is None:
            await ctx.send('```Сообщение которое вы пытаетесь удалить не относиться к системе выдаче ролей!```')
            return
        cursor.execute(sql.SQL('DELETE FROM react_role WHERE id = {message_id}').format(
            message_id=sql.Literal(message_id)
        ))
        db.commit()
        await message_to_remove.delete()
        await ctx.send(f'```Отлично, сообщение удалено!```')
        self.load_role_data()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        user = payload.member
        emoji = payload.emoji.name
        if user.id == self.bot.user.id:
            return
        for mes in self.role_data:
            if payload.message_id == mes['message_id']:
                role_id = mes['role_info'][emoji]
                role = discord.utils.get(user.guild.roles, id=role_id)
                await user.add_roles(role, reason='Роль выдана по реакции')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)
        user = discord.utils.get(guild.members, id=payload.user_id)
        emoji = payload.emoji.name
        if user.id == self.bot.user.id:
            return
        for mes in self.role_data:
            if payload.message_id == mes['message_id']:
                role_id = mes['role_info'][emoji]
                role = discord.utils.get(user.guild.roles, id=role_id)
                await user.remove_roles(role, reason='Роль удалена по реакции')

    def save_role_data(self, save_data):
        for data in save_data:
            message = data['message_id']
            role_info = data['info']
            cursor.execute(sql.SQL('INSERT INTO react_role(id,info) VALUES ({message_id},{role_info})').format(
                id=sql.Literal(message),
                info=sql.Literal(json.dumps(role_info))
            ))
        db.commit()
        self.load_role_data()

    def load_role_data(self):
        msg_list = []
        cursor.execute('SELECT * FROM react_role')
        role_data = cursor.fetchall()
        for msg in role_data:
            message_id = msg[0]
            info = json.loads(msg[1])
            msg_list.append({'message_id': message_id, 'role_info': info})
        self.role_data = msg_list


def setup(bot):
    bot.add_cog(GameReactModule(bot))
