import datetime

import discord
from discord.ext import commands
from database import cursor, db
from componets import datetime_format, get_msk_datetime


class EventsModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tasks = []
        self.tasks.append(self.check_warns)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Бот готов, бан-хаммер блестит!')
        for task in self.tasks:
            self.bot.loop.create_task(task())

    async def check_warns(self):
        cursor.execute('SELECT * FROM warns')
        warns = cursor.fetchall()
        for warn in warns:
            if warn is None:
                break
            warn_id, user, owner, reason, issued_datetime, expiration = warn
            expiration_time = datetime.datetime.strptime(issued_datetime, datetime_format) + datetime.timedelta(
                days=expiration)
            if expiration_time <= get_msk_datetime():
                cursor.execute(f'DELETE FROM warns WHERE id = {warn_id} ')
                db.commit()
        print(warns)


def setup(bot):
    bot.add_cog(EventsModule(bot))
