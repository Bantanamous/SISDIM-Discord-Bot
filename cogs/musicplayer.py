import discord
from discord.ext import commands
import os
import asyncio
import yt_dlp
import urllib.parse, urllib.request, re

# Global initialization values
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents)

# Global variables
queues = {}
voice_clients = {}
youtube_base_url = 'https://www.youtube.com/'
youtube_results_url = youtube_base_url + 'results?'
youtube_watch_url = youtube_base_url + 'watch?v='
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)
discord.opus.load_opus
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
paused = False
volume = 0.25
class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded: Music Player")

    async def play_next(self, ctx):
        if ctx.guild.id in queues and queues[ctx.guild.id]:
            song_data = queues[ctx.guild.id].pop(0)
            await self.start_playing(ctx, song_data)

    @commands.command(name="play")
    async def play(self, ctx, *, query):
        if ctx.guild.id not in queues:
            queues[ctx.guild.id] = []

        try:
            if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_connected():
                voice_client = voice_clients[ctx.guild.id]
            else:
                voice_client = await ctx.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            await ctx.send(f"Error connecting to voice channel: {e}")
            return

        if not query.startswith("http"):
            query = urllib.parse.urlencode({"search_query": query})
            html_content = urllib.request.urlopen(youtube_results_url + query)
            search_results = re.findall(r'/watch\?v=(.{11})', html_content.read().decode())
            if not search_results:
                await ctx.send("No results found!")
                return
            query = youtube_watch_url + search_results[0]

        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
            if 'entries' in data:
                data = data['entries'][0]
            title = data['title']
            url = data['url']
            song_data = {"title": title, "url": url}
            if voice_client.is_playing() or paused:
                queues[ctx.guild.id].append(song_data)

            if not voice_client.is_playing() and not paused:
                await self.start_playing(ctx, song_data)
        except Exception as e:
            await ctx.send(f"Error: {e}")

    async def start_playing(self, ctx, song_data):
        try:
            ffmpeg_options_with_volume = {
                **ffmpeg_options,
                'options': f'-vn -filter:a "volume={volume}"'
            }
            player = discord.FFmpegOpusAudio(song_data['url'], **ffmpeg_options_with_volume)
            voice_clients[ctx.guild.id].play(player, after=lambda e: client.loop.create_task(self.play_next(ctx)))
            await ctx.send(f"Now playing: {song_data['title']}")
        except Exception as e:
            await ctx.send(f"Error playing song: {e}")

    @commands.command(name="clear")
    async def clear_queue(self, ctx):
        if ctx.guild.id in queues:
            queues[ctx.guild.id].clear()
            await ctx.send("Queue cleared!")
        else:
            await ctx.send("There is no queue to clear")

    @commands.command(name="pause")
    async def pause(self, ctx):
        try:
            voice_clients[ctx.guild.id].pause()
            global paused
            paused = True
        except Exception as e:
            await ctx.send(f"Error pausing: {e}")

    @commands.command(name="resume")
    async def resume(self, ctx):
        try:
            voice_clients[ctx.guild.id].resume()
            global paused
            paused = False
        except Exception as e:
            await ctx.send(f"Error resuming: {e}")

    @commands.command(name="stop")
    async def stop(self, ctx):
        try:
            voice_clients[ctx.guild.id].stop()
            await voice_clients[ctx.guild.id].disconnect()
            del voice_clients[ctx.guild.id]
            queues[ctx.guild.id].clear()
        except Exception as e:
            await ctx.send(f"Error stopping: {e}")

    @commands.command(name="queue")
    async def queue(self, ctx):
        if ctx.guild.id in queues and queues[ctx.guild.id]:
            queue_str = "\n".join([song_data['title'] for song_data in queues[ctx.guild.id]])
            await ctx.send(f"Current queue:\n{queue_str}")
        else:
            await ctx.send("The queue is empty!")

    @commands.command(name='skip')
    async def skip(self, ctx):
        try:
            voice_clients[ctx.guild.id].stop()
            await self.play_next(ctx)
            await ctx.send("Song skipped!")
        except Exception as e:
            print(e)
            
#command for chanking volume, currently non-functional, commented out to prevent issues.
#    @commands.command(name="volume")
#    async def volume(self, ctx, volume: float):
#        if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_connected():
#            voice_client = voice_clients[ctx.guild.id]
#            if voice_client.is_playing():
#                print(f"Current volume before adjustment: {voice_client.source.volume}")
#                voice_client.source.volume = volume
#                print(f"New volume after adjustment: {voice_client.source.volume}")
#                await ctx.send(f"Volume set to {volume}")
#            else:
#                await ctx.send("No audio is currently playing.")
#        else:
#            await ctx.send("Not connected to a voice channel or no audio is playing.")

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
