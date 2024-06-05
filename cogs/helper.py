import discord
from discord.ext import commands

class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.text_channel_text = []
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded: Helper")

    async def send_to_all(self,msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(msg)

    @commands.command(name="help", help="Displays all available commands")
    async def help(self, ctx):
        await ctx.send( """
```
General commands:
.ping - Tests if bot is responsive
.play <keywords/url> - Finds the song on youtube and plays it in your current voicechannel. Will resume if paused.
.queue - Shows the music queue
.skip - skips the current song
.clear - Empties the queue
.stop - Stops the current song, clears the queue and disconnects the bot
.pause - Pauses the current song
.resume - Resumes the song
```
""")

    @commands.command(name="cooked")
    async def cooked(self, ctx):
        try:
            with open('./images/cooked.jpg', 'rb') as f:
                picture = discord.File(f)
                await ctx.send(file=picture)
        except Exception as e:
            print(e)
            
async def setup(bot):
    await bot.add_cog(help(bot))