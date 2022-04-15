import asyncio
import datetime
import os
import pathlib
import random
import shutil
import traceback

import disnake
import yt_dlp
from disnake.ext import commands
from assets import emojis
import core
from assets import emojis

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}
music_dir = pathlib.Path('music')
if not os.path.exists(music_dir):
    os.mkdir(music_dir)
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


class MusicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def music_help(self, inter: disnake.CommandInteraction):
        """Справка для музыки [BETA]"""
        text = '```[play] {url/name} - запуск воспроизведения. (Используется один раз для старта.' \
               ' Для добавления треков использовать [add])\n' \
               '[add] {url/name} - добавить новый трек в очередь воспроизведения\n' \
               '[queue] - просмотреть очередь воспроизведения\n' \
               '[playlist_loop] - зациклить весь список\n' \
               '[loop] - зациклить один трек\n' \
               '[next] - следующий трек\n' \
               '[back] - предыдущий трек\n' \
               '[shuffle] - перемешать треки\n' \
               '[stop] - остановить воспроизведение\n' \
               '[pause] - поставить на паузу\n' \
               '[resume] - возобновить воспроизведение\n' \
               '[select] {queue_id} - проиграть сейчас трек под номером {queue_id} из списка\n' \
               '[move] {first_track,second_track} - переместить {first_track} на позицию {second_track}, при этом' \
               ' {second_track} смещается на одну позицию вперёд\n' \
               '[swap] {first_track,second_track} - меняет местами {first_track} и {second_track}\n' \
               '[remove] {track_id} - удаляет трек из списка```'
        emb = disnake.Embed(title='Справка по модулю [MUSIC]', colour=disnake.Colour.purple(), description=text)
        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text='Справочное бюро', icon_url=self.bot.user.display_avatar)
        await inter.send(embed=emb)

    @commands.command()
    async def play(self, ctx: commands.Context, *, url: str):
        print('play')
        try:
            voice_channel: disnake.VoiceChannel = ctx.author.voice.channel
        except:
            await ctx.send(f'{emojis.exclamation}`Что бы слушать музыку, надо быть на связи с космосом!`')
            return
        if Players.is_using(ctx.guild):
            await ctx.send(
                f'{emojis.exclamation}`Очередь воспроизведения уже создана! Используйте add что-бы добавить в очередь`')
            return
        try:
            voice_client = await voice_channel.connect()
            player = MusicPlayer(ctx.guild, ctx.author, ctx.channel)
            p = Players(ctx.guild, ctx.author, player)
            await self._add(ctx, url)
            p.player.play()
        except disnake.errors.ClientException:
            await ctx.send(f'{emojis.exclamation}`Я конечно могу много чего, но разорваться на части не могу!`')

    @commands.command()
    async def add(self, ctx: commands.Context, *, url):
        await self._add(ctx, url)

    async def _add(self, ctx, url):
        player = Players.get_player(ctx.guild)
        if player is None:
            await ctx.send(f'{emojis.no_entry} `Музыка ещё не запущена! (Воспользуйтесь командой play)`')
        else:
            if 'https://' in url:
                is_url = True
            else:
                is_url = False
            result = await YouTubeSource.from_url(url)
            if 'entries' in result:
                if is_url:
                    duration = 0
                    for en in result['entries']:
                        player.queue.append(en)
                        duration += en['duration']
                else:
                    result = result['entries'][0]
                    duration = result['duration']
                    player.queue.append(result)
            else:
                duration = result['duration']
            emb = disnake.Embed(title=f'Добавлен {"плейлист" if "entries" in result else "трек"}',
                                color=disnake.Colour(0x9B34F0))
            emb.description = f"[{result['title']}]({result['webpage_url']})"
            emb.add_field(name='Длительность', value=f'`{datetime.timedelta(seconds=duration)}`')
            emb.add_field(name='Позиция в очереди', value=str(len(player.queue)))
            emb.set_thumbnail(url=result['thumbnail'])
            emb.set_author(
                icon_url='https://cdn.discordapp.com/attachments/940641488122044476/947085322469122088/radiofm4-fm4.gif',
                name='Музыка горизонта')
            await ctx.send(embed=emb)

    @commands.command()
    async def playlist_loop(self, ctx: commands.Context):
        p = Players.get_player(ctx.guild)
        p.is_playlist_loop = not p.is_playlist_loop
        if p.is_playlist_loop:
            emoji = emojis.repeat_all_unicode
        else:
            emoji = emojis.x_unicode
        await ctx.message.add_reaction(emoji)

    @commands.command()
    async def next(self, ctx: commands.Context):
        p = Players.get_player(ctx.guild)
        p.next()
        await ctx.message.add_reaction(emojis.next_track_unicode)

    @commands.command()
    async def shuffle(self, ctx: commands.Context):
        p = Players.get_player(ctx.guild)
        p.shuffle()
        await ctx.message.add_reaction(emojis.shuffle_unicode)

    @commands.command()
    async def back(self, ctx: commands.Context):
        p = Players.get_player(ctx.guild)
        p.back()
        await ctx.message.add_reaction(emojis.previous_track_unicode)

    @commands.command()
    async def stop(self, ctx: commands.Context):
        p = Players.get_player(ctx.guild)
        p.is_stop = True
        p.finalize()
        await ctx.message.add_reaction(emojis.stop_unicode)

    @commands.command()
    async def pause(self, ctx: commands.Context):
        p = Players.get_player(ctx.guild)
        p.pause()
        await ctx.message.add_reaction(emojis.pause_unicode)

    @commands.command()
    async def resume(self, ctx: commands.Context):
        p = Players.get_player(ctx.guild)
        p.resume()
        await ctx.message.add_reaction(emojis.resume_unicode)

    @commands.command()
    async def queue(self, ctx: commands.Context):
        emb = disnake.Embed(title=' ', color=disnake.Colour(0xA7E6F0), description='')
        emb.set_author(
            icon_url='https://cdn.discordapp.com/attachments/940641488122044476/947085322469122088/radiofm4-fm4.gif',
            name='Музыка горизонта')
        counter = 0
        p = Players.get_player(ctx.guild)
        if p is None:
            await ctx.send(f'{emojis.exclamation}`Плейлист пуст!`')
            return
        for track in p.queue:
            new_s = f'{"**-> ** " if counter == p.pointer else ""}**{counter + 1}: **{track["title"]}\n'
            if len(emb.description + new_s) > 5900:
                await ctx.send(f'{emojis.exclamation}`Невозможно вывести весь плейлист`')
            else:
                emb.description += new_s
                counter += 1
        await ctx.send(embed=emb)

    @commands.command()
    async def select(self, ctx, index: int):
        p = Players.get_player(ctx.guild)
        p.pointer = int(index) - 1
        p.restart_play()
        await ctx.message.add_reaction(emojis.white_check_mark_unicode)

    @commands.command()
    async def move(self, ctx, wi, fi):
        p = Players.get_player(ctx.guild)
        p.move(wi, fi)
        await ctx.message.add_reaction(emojis.white_check_mark_unicode)

    @commands.command()
    async def loop(self, ctx):
        p = Players.get_player(ctx.guild)
        p.is_loop = not p.is_loop
        if p.is_loop:
            emoji = emojis.repeat_one_unicode
        else:
            emoji = emojis.x_unicode
        await ctx.message.add_reaction(emoji)

    @commands.command()
    async def swap(self, ctx, wi, fi):
        p = Players.get_player(ctx.guild)
        p.swap(wi, fi)
        await ctx.message.add_reaction(emojis.white_check_mark_unicode)

    @commands.command()
    async def remove(self, ctx, i):
        p = Players.get_player(ctx.guild)
        p.remove(i)
        await ctx.message.add_reaction(emojis.white_check_mark_unicode)


class MusicPlayer:
    def __init__(self, guild: disnake.Guild, owner, text_channel):
        self.owner = owner
        self.guild = guild
        self.queue = []
        self.text_channel = text_channel
        self.bot = core.Bot.get_bot()
        self.is_stop = False
        self.is_loop = False
        self.is_playlist_loop = False
        self.pointer = 0
        self.audio_stream = None
        self.id = random.randint(0, 50)

    def remove(self, i):
        try:
            self.queue.remove(self.queue[int(i) - 1])
        except IndexError:
            self.bot.loop.create_task(self.text_channel.send(f'{emojis.exclamation}`Неверные индексы очереди!`'))

    def swap(self, wi, fi):
        try:
            t1 = self.queue[int(wi) - 1]
            t2 = self.queue[int(fi) - 1]
            self.queue[int(wi) - 1] = t1
            self.queue[int(fi) - 1] = t2
        except IndexError:
            self.bot.loop.create_task(self.text_channel.send(f'{emojis.exclamation}`Неверные индексы очереди!`'))

    def shuffle(self):
        self.queue.sort(key=lambda x: random.randint(0, 100))

    def pause(self, user=True):
        if self.guild.voice_client.is_playing():
            self.guild.voice_client.pause()
        else:
            if user:
                self.bot.loop.create_task(self.text_channel.send(f'{emojis.exclamation} `Музыка и так на паузе!`'))

    def resume(self):
        voice_client = self.guild.voice_client
        if voice_client.is_playing():
            self.bot.loop.create_task(
                self.text_channel.send(f'{emojis.exclamation}`Эээээ, музыка и так играет! Хватить кнопки тыкать!`'))
        voice_client.resume()

    def move(self, wi, fi):
        try:
            t_index = self.queue.index(self.queue[int(fi) - 1])
            self.queue.insert(t_index, self.queue[int(wi) - 1])
        except IndexError:
            self.bot.loop.create_task(self.text_channel.send(f'{emojis.exclamation}`Неверный индекс`'))

    def play(self):
        if self.is_stop:
            return
        if self.is_playlist_loop:
            if self.pointer >= len(self.queue):
                self.pointer = 0
        filename = ytdl.prepare_filename(self.queue[self.pointer])
        if not os.path.exists(pathlib.Path(music_dir, filename)):
            # print(self.queue[self.pointer]['webpage_url'])
            ytdl.download([self.queue[self.pointer]['webpage_url']])
            shutil.move(filename, pathlib.Path(music_dir, filename))
        voice_client = self.guild.voice_client
        # self.pause(user=False)
        voice_client.pause()
        attempt_counter = 0
        while True:
            try:
                self.audio_stream = disnake.FFmpegPCMAudio(executable='ffmpeg.exe',
                                                           source=str(pathlib.Path(music_dir, filename)))
                voice_client.play(self.audio_stream, after=self._next)
                break
            except ValueError:
                attempt_counter += 1
            if attempt_counter == 10:
                # print(10)
                break

    def _next(self, error):
        if error:
            print(traceback.print_exception(error))
            self.bot.loop.create_task(
                self.text_channel.send(f'{emojis.exclamation} При воспроизведении произошла ошибка: {error}'))
            self.finalize()
        else:
            if self.guild.voice_client is not None:
                self.next(user=False)

    def back(self):
        self.pointer -= 1
        self.restart_play()

    def next(self, user=True):
        if user or not self.is_loop:
            self.pointer += 1
        self.restart_play()

    def restart_play(self):
        try:
            self.audio_stream.cleanup()
        except:
            pass
        try:
            self.pause(user=False)
        except Exception as ex:
            print(f'\n{ex}')
        try:
            self.play()
        except IndexError:
            self.finalize()
        except AttributeError:
            pass

    async def add(self, name):
        data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(name, download=False))
        self.queue.append(data)

    def finalize(self):
        # print(self.id)
        self.bot.loop.create_task(
            self.text_channel.send(f'{emojis.white_check_mark} `Очередь воспроизведения окончена!`'))
        try:
            self.guild.voice_client.stop()
            self.bot.loop.create_task(self.guild.voice_client.disconnect())
        except AttributeError:
            pass
        self.bot.loop.create_task(self.clear_cache(self.queue))
        Players.del_player(self.guild)

    async def clear_cache(self, queue):
        for data in queue:
            filename = ytdl.prepare_filename(data)
            try:
                os.remove(pathlib.Path(music_dir, filename))
            except PermissionError:
                await asyncio.sleep(1)
                self.bot.loop.create_task(self.clear_cache([data]))
            except FileNotFoundError:
                continue


class YouTubeSource:
    @classmethod
    async def from_url(cls, url):
        loop = core.Bot.get_bot().loop
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        return data


class Players:
    all_players = []

    def __init__(self, guild: disnake.Guild, owner: disnake.Member, player: MusicPlayer):
        self.guild = guild
        self.owner = owner
        self.all_players.append(self)
        self.player = player

    @classmethod
    def get_owner(cls, guild: disnake.Guild):
        for pl in cls.all_players:
            if pl.guild.id == guild.id:
                return pl.owner
        else:
            return None

    @classmethod
    def is_using(cls, guild: disnake.Guild):
        if guild.id in [g.guild.id for g in cls.all_players]:
            return True
        else:
            return False

    @classmethod
    def get_player(cls, guild: disnake.Guild):
        for pl in cls.all_players:
            if pl.guild.id == guild.id:
                return pl.player
        else:
            return None

    @classmethod
    def del_player(cls, guild):
        for pl in cls.all_players:
            if pl.guild.id == guild.id:
                cls.all_players.remove(pl)


def setup(bot: commands.Bot):
    bot.add_cog(MusicCommands(bot))
