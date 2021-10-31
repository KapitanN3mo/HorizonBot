import asyncio
import datetime
import discord
from discord.ext import commands
from database import cursor, db
from componets import datetime_format, get_msk_datetime, config


class EventsModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tasks = []
        self.tasks.append(self.check_warns)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Бот готов, бан-хаммер блестит!')
        await self.bot.change_presence(status=discord.Status.online,activity=discord.Activity(type=discord.ActivityType.watching,name='кого-бы забанить?'))
        for task in self.tasks:
            self.bot.loop.create_task(task())

    async def check_warns(self):
        while True:
            cursor.execute('SELECT * FROM warns')
            warns = cursor.fetchall()
            channel = self.bot.get_channel(int(config.get('Global', 'notify_channel')))
            for warn in warns:
                if warn is None:
                    break
                warn_id, user, owner, reason, issued_datetime, expiration = warn
                expiration_time = datetime.datetime.strptime(issued_datetime, datetime_format) + datetime.timedelta(
                    days=expiration)
                if expiration_time <= get_msk_datetime().replace(tzinfo=None):
                    cursor.execute(f'DELETE FROM warns WHERE id = {warn_id} ')
                    db.commit()
                    print(f'Удалён варн {warn_id}')
                    user = self.bot.get_user(user)
                    if user is not None:
                        user = user.name
                    await channel.send(f':grin: `С пользователя {user} снят варн №{warn_id} по истечении срока`')
            await asyncio.sleep(300)


def setup(bot):
    bot.add_cog(EventsModule(bot))
