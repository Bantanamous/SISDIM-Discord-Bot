# This program made by Shaymon Madrid with help from online resources such as videos, source code examples, and documentation files. 

import discord
from discord.ext import commands
from discord import Intents, Client, Message
import os
import asyncio
from dotenv import load_dotenv

#Important information being loaded
load_dotenv()
TOKEN = os.getenv('discord_token')
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
    await load()
    await bot.start(TOKEN)

asyncio.run(main())