import discord
from discord.ext import commands
import os
import discord.opus



async def load_cogs(bot):
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f'cogs.{filename[:-3]}')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await load_cogs(bot)

# Memuat token dari environment variable
bot.run(os.getenv("DISCORD_TOKEN"))
