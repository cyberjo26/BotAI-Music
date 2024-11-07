import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import re

ytdl_format_options = {
    'format': 'bestaudio',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True,
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
    'executable': 'C:\\ffmpeg\\bin\\ffmpeg.exe'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.inactivity_timers = {}  # Menyimpan timer untuk guild

    async def join_channel(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("Anda perlu bergabung ke voice channel terlebih dahulu!")

    async def play_music(self, ctx, url):
        if ctx.guild.voice_client is None:
            await self.join_channel(ctx)

        data = ytdl.extract_info(url, download=False)
        audio_url = data['url']
        title = data.get("title", "Lagu")
        uploader = data.get("uploader", "Tidak diketahui")
        thumbnail = data.get("thumbnail")

        ctx.guild.voice_client.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
                                    after=lambda e: self.play_next(ctx))

        embed = discord.Embed(title="Sedang Memutar 🎶", color=discord.Color.blue())
        embed.add_field(name="Judul", value=title, inline=False)
        embed.add_field(name="Uploader", value=uploader, inline=True)
        embed.add_field(name="Link", value=f"[Klik di sini untuk menonton]({url})", inline=True)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        await ctx.send(embed=embed)

    def play_next(self, ctx):
        if ctx.guild.id in self.song_queue and self.song_queue[ctx.guild.id]:
            next_url = self.song_queue[ctx.guild.id].pop(0)
            asyncio.run_coroutine_threadsafe(self.play_music(ctx, next_url), self.bot.loop)
        else:
            # Jika tidak ada lagu di antrean, mulai timer untuk memantau aktivitas
            self.inactivity_timers[ctx.guild.id] = self.bot.loop.call_later(30, 
                lambda: asyncio.run_coroutine_threadsafe(self.disconnect_if_inactive(ctx), self.bot.loop))

    async def disconnect_if_inactive(self, ctx):
        # Jika bot tidak sedang memutar musik, bot keluar dari voice channel
        if ctx.guild.voice_client and not ctx.guild.voice_client.is_playing():
            await ctx.guild.voice_client.disconnect()
            await ctx.send("👋 Tidak ada aktivitas selama 30 detik. Keluar dari voice channel.")

    async def search_youtube(self, query):
        search_opts = {'format': 'bestaudio', 'noplaylist': 'True'}
        with youtube_dl.YoutubeDL(search_opts) as ydl:
            results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
            return results

    def is_url(self, string):
        url_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')
        return bool(url_pattern.match(string))

    @commands.command(name='play')
    async def play(self, ctx, *, query: str = None):
        if not ctx.author.voice:
            await ctx.send("Anda perlu bergabung ke voice channel terlebih dahulu!")
            return

        if query is None:
            await ctx.send("Mohon masukkan kata kunci atau URL untuk memutar lagu. Contoh: `!play JVKE Golden Hour` atau `!play <URL>`")
            return

        if self.is_url(query):
            if ctx.guild.voice_client and ctx.guild.voice_client.is_playing():
                self.song_queue.setdefault(ctx.guild.id, []).append(query)
                await ctx.send("🎶 Lagu ditambahkan ke antrean.")
            else:
                await self.play_music(ctx, query)
                # Batalkan timer inactivity jika ada
                if ctx.guild.id in self.inactivity_timers:
                    self.inactivity_timers[ctx.guild.id].cancel()
                    del self.inactivity_timers[ctx.guild.id]
        else:
            results = await self.search_youtube(query)
            embed = discord.Embed(title="Pilih Lagu 🎶", description="Ketik nomor pilihan (misalnya `1`, `2`) untuk memilih.", color=discord.Color.blue())
            
            for i, entry in enumerate(results, start=1):
                embed.add_field(name=f"{i}. {entry['title']}", value=entry['webpage_url'], inline=False)

            message = await ctx.send(embed=embed)

            def check(msg):
                return msg.author == ctx.author and msg.content.isdigit() and 1 <= int(msg.content) <= len(results)

            try:
                choice = await self.bot.wait_for("message", check=check, timeout=30.0)
                index = int(choice.content) - 1
                if ctx.guild.voice_client and ctx.guild.voice_client.is_playing():
                    self.song_queue.setdefault(ctx.guild.id, []).append(results[index]['webpage_url'])
                    await ctx.send("🎶 Lagu ditambahkan ke antrean.")
                else:
                    await self.play_music(ctx, results[index]['webpage_url'])
                    # Batalkan timer inactivity jika ada
                    if ctx.guild.id in self.inactivity_timers:
                        self.inactivity_timers[ctx.guild.id].cancel()
                        del self.inactivity_timers[ctx.guild.id]
            except asyncio.TimeoutError:
                await ctx.send("Waktu habis. Silakan coba lagi.")
            finally:
                await message.delete()

    @commands.command(name='skip')
    async def skip(self, ctx):
        if not ctx.author.voice:
            await ctx.send("Anda perlu bergabung ke voice channel terlebih dahulu!")
            return

        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("⏭️ Lagu di-skip.")
        else:
            await ctx.send("Tidak ada lagu yang sedang diputar.")

    @commands.command(name='leave')
    async def leave(self, ctx):
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
            await ctx.send("👋 Keluar dari voice channel.")
        else:
            await ctx.send("Saya tidak berada di voice channel mana pun.")

async def setup(bot):
    await bot.add_cog(Music(bot))
