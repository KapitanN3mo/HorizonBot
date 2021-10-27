import discord
from discord.ext import commands
from database import cursor, db


class EventsModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        cursor.execute(f'SELECT message_count FROM server_users WHERE id = {message.author.id}')
        result = cursor.fetchone()
        print(result)
        if result is None:
            user_data = [message.author.id, 1, 0, 0, 'empty', 'empty', 'empty', 'empty']
            cursor.execute(f'INSERT INTO server_users VALUES(?,?,?,?,?,?,?,?)', user_data)
            db.commit()
        else:
            result = result[0]
            result += 1
            cursor.execute(f'UPDATE server_users SET message_count = {result} WHERE id = {message.author.id}')
            db.commit()
        # await self.bot.process_commands(message)


def setup(bot):
    bot.add_cog(EventsModule(bot))
