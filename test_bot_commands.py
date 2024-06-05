# test_bot_commands.py
import pytest
from unittest.mock import AsyncMock, Mock
from discord.ext import commands
import discord

from cogs.ping import ping, setup

@pytest.mark.asyncio
async def test_ping_command():
    # Mocking the bot and context
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="/", intents=intents)
    await setup(bot)
    
    cmd = bot.get_command("ping")

    # Creating a mock context
    ctx = Mock()
    ctx.send = AsyncMock()

    # Invoking the command
    await cmd.callback(ctx)  # Correctly invoke the command callback with the mock context
    
    # Asserting that ctx.send was called with "Pong"
    ctx.send.assert_called_once_with("Pong")

@pytest.mark.asyncio
async def test_echo_command():
    # Mocking the bot and context
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="!", intents=intents)
    await setup(bot)
    
    # Finding the echo command
    cmd = bot.get_command("echo")

    # Creating a mock context and message
    ctx = Mock()
    ctx.send = AsyncMock()
    message_content = "Hello, world!"

    # Invoking the command
    await cmd.callback(ctx, message=message_content)  # Pass the mock context and message content
    
    # Asserting that ctx.send was called with the correct message
    ctx.send.assert_called_once_with(message_content)

# pytest run command
if __name__ == '__main__':
    pytest.main()
