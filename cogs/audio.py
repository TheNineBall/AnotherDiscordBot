import asyncio
import discord
import re
from discord.ext import commands
from utils.audio import linkutils, audiocontroller, utils, settings

# TODO 1. timed embeds?
#      2. queue list with tabs?
#      3. post playlist on disconnect?

MAX_SONG_PRELOAD = 10
EMBED_COLOR = 0x4dd4d0
HTTP_REGEX = '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})'


class Audio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def setup(self, guild):
        """setup guild specific variables"""
        if guild not in utils.guild_to_settings:
            utils.guild_to_settings[guild] = settings.Settings(guild)
        if guild not in utils.guild_to_audiocontroller:
            utils.guild_to_audiocontroller[guild] = audiocontroller.AudioController(self.bot, guild)

    async def cog_after_invoke(self, ctx):
        await ctx.message.delete()

    async def handle_reactions(self, payload):
        """handle reactions for messages that dont have reactions with bot.react"""
        if payload.emoji.name == '↩' or '↩️':
            m = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            if m.author.id == self.bot.user.id:
                x = re.search(HTTP_REGEX, m.embeds[0].description.replace(')', ' '))
                if x:
                    ctx = await self.bot.get_context(m)
                    if (await utils.is_connected(ctx) is not None):
                        await self._play_song(ctx=ctx, track=x.group())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id and before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == 300:
                    await voice.disconnect()
                if not voice.is_connected():
                    break

    async def cog_before_invoke(self, ctx):
       await ctx.message.delete()

    async def uconnect(self, ctx):
        vchannel = await utils.is_connected(ctx)
        if vchannel is not None:
            #await ctx.send('already connected')
            return
        current_guild = utils.get_guild(self.bot, ctx.message)
        if current_guild is None or ctx.author.voice is None:
            await ctx.send('please join a voice channel first')
            return
        if utils.guild_to_audiocontroller[current_guild] is None:
            utils.guild_to_audiocontroller[current_guild] = audiocontroller.AudioController(
                self.bot, current_guild)
        utils.guild_to_audiocontroller[current_guild] = audiocontroller.AudioController(
            self.bot, current_guild)
        await utils.guild_to_audiocontroller[current_guild].register_voice_channel(ctx.author.voice.channel)
        #await ctx.send("Connected to {} {}".format(ctx.author.voice.channel.name, ":white_check_mark:"))

    async def udisconnect(self, ctx, guild):
        if guild is not False:
            current_guild = guild
            await utils.guild_to_audiocontroller[current_guild].stop_player()
            await current_guild.voice_client.disconnect(force=True)
        else:
            current_guild = utils.get_guild(self.bot, ctx.message)
            if current_guild is None:
                await ctx.send('error')
                return
            if await utils.is_connected(ctx) is None:
                await ctx.send('error')
                return
            await utils.guild_to_audiocontroller[current_guild].stop_player()
            await current_guild.voice_client.disconnect(force=True)
            #await ctx.send("Disconnected from voice channel. Use '{}c' to rejoin.".format('?'))

    async def _skip_pre(self, user, ctx, song):
        """skip/remove a song and delte reactions"""
        ac = utils.guild_to_audiocontroller[utils.get_guild(self.bot, ctx.message)]
        if song == ac.current_song:
            ctx.author = user
            await self._skip(ctx)
        else:
            ac.playlist.remove(song)
        await song.emb.clear_reaction('❌')
        await song.emb.clear_reaction('🔁')

    @commands.command(name='connect', description='connect', help='connect', aliases=['c'])
    async def _connect(self, ctx):  # dest_channel_name: str
        await self.uconnect(ctx)

    @commands.command(name='disconnect', description='disconnect', help='disconnect', aliases=['dc'])
    async def _disconnect(self, ctx, guild=False):
        await self.udisconnect(ctx, guild)

    @commands.command(name='reset', description='reset', help='reset', aliases=['rs', 'restart'])
    async def _reset(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        if current_guild is None:
            #await ctx.send('error')
            return
        await utils.guild_to_audiocontroller[current_guild].stop_player()
        await current_guild.voice_client.disconnect(force=True)
        utils.guild_to_audiocontroller[current_guild] = audiocontroller.AudioController(
            self.bot, current_guild)
        await utils.guild_to_audiocontroller[current_guild].register_voice_channel(ctx.author.voice.channel)
        #await ctx.send("{} Connected to {}".format(":white_check_mark:", ctx.author.voice.channel.name))

    @commands.command(name='changechannel', description='change channel', help='change channel', aliases=['cc'])
    async def _change_channel(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        vchannel = await utils.is_connected(ctx)
        if vchannel == ctx.author.voice.channel:
            #await ctx.send("{} Already connected to {}".format(":white_check_mark:", vchannel.name))
            return
        if current_guild is None:
            #await ctx.send('error)
            return
        await utils.guild_to_audiocontroller[current_guild].stop_player()
        await current_guild.voice_client.disconnect(force=True)
        utils.guild_to_audiocontroller[current_guild] = audiocontroller.AudioController(
            self.bot, current_guild)
        await utils.guild_to_audiocontroller[current_guild].register_voice_channel(ctx.author.voice.channel)
        #await ctx.send("{} Switched to {}".format(":white_check_mark:", ctx.author.voice.channel.name))

    @commands.command(name='play', description='play song', help='play song', aliases=['p', 'yt', 'pl'])
    async def _play_song(self, ctx, *, track: str):
        current_guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        if (await utils.is_connected(ctx) == None):
            if await audiocontroller.uconnect(ctx) == False:
                return
        if track.isspace() or not track:
            return
        if await utils.play_check(ctx) == False:
            return
        # reset timer
        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)
        if audiocontroller.playlist.loop == True:
            #await ctx.send("Loop is enabled! Use {}loop to disable".format('?'))
            return
        song = await audiocontroller.process_song(track)
        if song is None:
            await ctx.send('song-error')
            return
        if song.origin == linkutils.Origins.Default:
            if audiocontroller.current_song != None and len(audiocontroller.playlist.playque) == 0:
                emb = await ctx.send(embed=song.info.format_output('now playing'))
                pass
            else:
                emb = await ctx.send(embed=song.info.format_output('added to queue'))
                pass
            song.emb = emb
            await self.bot.react.add(emb, '🔁', self._loop, True, (ctx,))
            await self.bot.react.add_new(emb, '❌', self._skip_pre, True, True, (ctx, song))
            await self.bot.react.add_new(emb, '↩', self._play_song, True, (ctx,), track=track)
        elif song.origin == linkutils.Origins.Playlist:
            await ctx.send('playlist added')
            pass

    @commands.command(name='loop', description='loop', help='loop', aliases=['l'])
    async def _loop(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        if await utils.play_check(ctx) == False:
            return
        if len(audiocontroller.playlist.playque) < 1 and current_guild.voice_client.is_playing() == False:
            #await ctx.send("No songs in queue!")
            return
        if audiocontroller.playlist.loop == False:
            audiocontroller.playlist.loop = True
            await ctx.send("Loop enabled")
        else:
            audiocontroller.playlist.loop = False
            await ctx.send("Loop disabled")

    @commands.command(name='shuffle', description='shuffle', help='shuffle', aliases=["sh"])
    async def _shuffle(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        if await utils.play_check(ctx) == False:
            return
        if current_guild is None:
            await ctx.send('error')
            return
        if current_guild.voice_client is None or not current_guild.voice_client.is_playing():
            await ctx.send("Queue is empty")
            return
        audiocontroller.playlist.shuffle()
        await ctx.send("Shuffled queue")
        for song in list(audiocontroller.playlist.playque)[:MAX_SONG_PRELOAD]:
            asyncio.ensure_future(audiocontroller.preload(song))

    @commands.command(name='pause', description='pause', help='pause')
    async def _pause(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        if await utils.play_check(ctx) == False:
            return
        if current_guild is None:
            await ctx.send('error')
            return
        if current_guild.voice_client is None or not current_guild.voice_client.is_playing():
            return
        current_guild.voice_client.pause()
        await ctx.send("Playback Paused")

    @commands.command(name='queue', description='', help='', aliases=['playlist', 'q'])
    async def _queue(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        if await utils.play_check(ctx) == False:
            return
        if current_guild is None:
            await ctx.send('error')
            return
        if current_guild.voice_client is None or not current_guild.voice_client.is_playing():
            await ctx.send("Queue is empty")
            return
        playlist = utils.guild_to_audiocontroller[current_guild].playlist
        embed = discord.Embed(title=":scroll: Queue [{}]".format(
            len(playlist.playque)), color=EMBED_COLOR, inline=False)
        # Embeds are limited to 25 fields
        for counter, song in enumerate(list(playlist.playque)[:min(MAX_SONG_PRELOAD, 25)], start=1):
            if song.info.title is None:
                embed.add_field(name="{}.".format(str(counter)), value="[{}]({})".format(
                    song.info.webpage_url, song.info.webpage_url), inline=False)
            else:
                embed.add_field(name="{}.".format(str(counter)), value="[{}]({})".format(
                    song.info.title, song.info.webpage_url), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='stop', description='', help='', aliases=['st'])
    async def _stop(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        if await utils.play_check(ctx) == False:
            return
        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.playlist.loop = False
        if current_guild is None:
            await ctx.send('error')
            return
        await utils.guild_to_audiocontroller[current_guild].stop_player()
        await ctx.send("Stopped all sessions")

    @commands.command(name='skip', description='', help='', aliases=['s'])
    async def _skip(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        if await utils.play_check(ctx) == False:
            return
        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.playlist.loop = False
        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)
        if current_guild is None:
            await ctx.send('error')
            return
        if current_guild.voice_client is None or (
                not current_guild.voice_client.is_paused() and not current_guild.voice_client.is_playing()):
            await ctx.send("Queue is empty")
            return
        current_guild.voice_client.stop()
        await ctx.send("Skipped current song")

    @commands.command(name='clear', description='', help='', aliases=['cl'])
    async def _clear(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        if await utils.play_check(ctx) == False:
            return
        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.clear_queue()
        current_guild.voice_client.stop()
        audiocontroller.playlist.loop = False
        await ctx.send("Cleared queue :no_entry_sign:")

    @commands.command(name='prev', description='', help='', aliases=['back'])
    async def _prev(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        if await utils.play_check(ctx) == False:
            return
        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.playlist.loop = False
        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)
        if current_guild is None:
            await ctx.send('error')
            return
        await utils.guild_to_audiocontroller[current_guild].prev_song()
        await ctx.send("Playing previous song :track_previous:")

    @commands.command(name='resume', description='', help='')
    async def _resume(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        if await utils.play_check(ctx) == False:
            return
        if current_guild is None:
            await ctx.send('error')
            return
        current_guild.voice_client.resume()
        await ctx.send("Resumed playback")

    @commands.command(name='songinfo', description='', help='', aliases=["np"])
    async def _songinfo(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        if await utils.play_check(ctx) == False:
            return
        if current_guild is None:
            await ctx.send('error')
            return
        song = utils.guild_to_audiocontroller[current_guild].current_song
        if song is None:
            return
        await ctx.send(embed=song.info.format_output('Song info'))

    @commands.command(name='history', description='', help='')
    async def _history(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        if await utils.play_check(ctx) == False:
            return
        if current_guild is None:
            await ctx.send('error')
            return
        await ctx.send(utils.guild_to_audiocontroller[current_guild].track_history())

    @commands.command(name='volume', description='', help='', aliases=["vol"])
    async def _volume(self, ctx, *args):
        if ctx.guild is None:
            await ctx.send('error')
            return
        if await utils.play_check(ctx) == False:
            return
        if len(args) == 0:
            await ctx.send("Current volume: {}% :speaker:".format(utils.guild_to_audiocontroller[ctx.guild]._volume))
            return
        try:
            volume = args[0]
            volume = int(volume)
            if volume > 200 or volume < 0:
                raise Exception('')
            current_guild = utils.get_guild(self.bot, ctx.message)
            await ctx.send('Volume set to {}%'.format(str(volume)))
            utils.guild_to_audiocontroller[current_guild].volume = volume
        except:
            await ctx.send("Error: Volume must be a number 1-200")
