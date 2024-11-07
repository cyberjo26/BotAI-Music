import discord
from discord.ext import commands
import time

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        websocket_ping = round(self.bot.latency * 1000)

        # API Ping
        start_time = time.perf_counter()
        message = await ctx.send("Mengukur ping API...")
        end_time = time.perf_counter()
        api_ping = round((end_time - start_time) * 1000)

        embed = discord.Embed(title="🏓 Ping", color=discord.Color.blue())
        embed.add_field(name="🌐 API Ping", value=f"{api_ping} ms", inline=False)
        embed.add_field(name="📶 WebSocket Ping", value=f"{websocket_ping} ms", inline=False)
        
        await message.edit(content=None, embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))
