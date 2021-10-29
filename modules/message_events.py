import math
import discord
from discord.ext import commands
from database import cursor, db
from componets import config
import re


class EventsModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        cursor.execute(f'SELECT message_count,xp FROM server_users WHERE id = {message.author.id}')
        result = cursor.fetchone()
        if result is None:
            user_data = [message.author.id, 1, 1, 0, 'normal', '{}', '{"send_dm_voice":"false"}', 'none']
            cursor.execute(f'INSERT INTO server_users VALUES(?,?,?,?,?,?,?,?)', user_data)
            db.commit()
        else:
            old_count = result[0]
            old_xp = result[1]
            old_count += 1
            xp_multiplier = int(config.get('Profile', 'xp_message_multiplier'))
            total_xp = int(xp_multiplier + old_xp)
            cursor.execute(
                f'''UPDATE server_users SET message_count = {old_count},xp = {total_xp} WHERE id = {message.author.id}''')
            db.commit()


def mat_search(text):
    return re.findall(
        r'[хxh][уyu][юйиuiяеeё]|[еe][б6b][аa@uio0иоуyкkнhnlлсcтыbь]|ё[б6b][аa@uio0иоуyкkнhnlлсcтыbь]|д.л[б6b]'
        r'[аa@o0оыbьееёиui]|[дdаa@ыьъo0о][еeё][б6b]|[еe][б6b][ееё][тцмш]|[еe][б6b][ееё]н[ьbяееиuiн]|[сc]ц?[уyыb][кч4]|'
        r'[б6b]л[яэ]|г.ндон|г.вн|моч[аa@]|жоп|п[ееёиui]зд|cum|конч|[сc][сcц]ц?[уyаa@ыb]|м[аa@]нд|м[иui]н[еe]т|[б6b]зд.|др'
        r'[иuiее][сc][тн]|[сc][иui]р[ыьbаa@][ткл]|[сc]р[аa@][ткл]|[хxh][еe]р|п[иui]д.р|fu[сc]k|[сc]unt|[сc]ock|др[аa@o0о]'
        r'[тч]|п[еe]рд|св[аa@o0о]л[аa@o0о]|[еe]лд[аa@]|муд[аa@иuio0оeе]|з[аa@o0о]луп|п.т[аa@o0о]ску|тр[аa@]х.|ф[аa@]к|п.скуд',
        text.lower())


def setup(bot):
    bot.add_cog(EventsModule(bot))
