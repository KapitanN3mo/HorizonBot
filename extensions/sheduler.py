import disnake
from disnake.ext import commands

class Sheduler(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
    
    @commands.command()
    async def create_shedule(inter:disnake.CommandInteraction,
    name:str,
    expiration:str):
        try:
            date = datetime.datetime.strptime(expiration,'%Y.%m.%d')
        except:
            await inter.send('Ошибка: Некорректная запись даты.')
            return
        try:
            database.Shedule.insert(
                guild=inter.guild.id,
                name=name,
                expiration=date,
                author=database.User.get(database.User.user_id=inter.author.id,database.User.guild_id=inter.guild.id))
        except Exception as ex:
            await inter.send(f'Ошибка БД: {ex}')
            return
        await inter.send(f'Задача {name} создана!')
    
    @commands.command()
    async def sheduler(inter:disnake.CommandInteraction):
        pass
    
class ShedulerView(disnake.ui.View):
    def __init__(self,guild:disnake.Guild):
        self.interaction = None
        self.guild = guild
        self.shedules = []
        self.emb = disnake.Embed()
        self.render()
        self.index = 0
        
    def render():
        emb = disnake.Embed(title=f'Планы {self.guild.name}',color=disnake.Color.red(),description = '')
        shedules = [database.Shedule.select().where(database.Shedule.guild==self.guild.id)]
        if len(shedules) == 0:
            emb.description = "Планы нет"
        else:
            shedule = shedules[self.index]
            tasks = [*database.Task.shedule==shedule]
            counter = 1
            for task in tasks:
                author = guild.get_member(task.author.user_id)
                emb.description+=f'[{counter}] Задача для {author.display_name}\n{task.text}\n'
                counter +=1
            emb.add_row(name="Срок",value=datetime.datetime.now()-)
def setup(bot):
    bot.add_cog(Sheduler(bot))