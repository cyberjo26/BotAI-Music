import discord
from discord.ext import commands
import os

class CodeGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="code")
    async def code(self, ctx, mode: str = None, filename: str = None, *, code_content: str = None):
        if mode not in ["new", "edit"]:
            await ctx.send("Mode tidak valid. Gunakan `new` untuk membuat file atau `edit` untuk mengedit file.")
            return
        if filename is None or code_content is None:
            await ctx.send("Format tidak lengkap. Gunakan `!code new <nama_file.py> <kode>` atau `!code edit <nama_file.py> <kode>`.")
            return

        if not filename.endswith(".py"):
            await ctx.send("Nama file harus berakhiran `.py`. Contoh: `ask.py`")
            return
        
        cogs_folder = "cogs"
        filepath = os.path.join(cogs_folder, filename)

        if not os.path.exists(cogs_folder):
            os.makedirs(cogs_folder)

        if mode == "new":
            if os.path.exists(filepath):
                await ctx.send(f"❌ File `{filename}` sudah ada. Gunakan `edit` untuk mengedit file ini.")
                return
            try:
                with open(filepath, "w") as file:
                    file.write(code_content)
                await ctx.send(f"✅ File `{filename}` berhasil dibuat di folder `{cogs_folder}`.")
            except Exception as e:
                await ctx.send(f"❌ Terjadi kesalahan saat membuat file: {e}")

        elif mode == "edit":
            if not os.path.exists(filepath):
                await ctx.send(f"❌ File `{filename}` tidak ditemukan. Gunakan `new` untuk membuat file ini.")
                return
            try:
                with open(filepath, "w") as file:
                    file.write(code_content)
                await ctx.send(f"✅ File `{filename}` berhasil diperbarui.")
            except Exception as e:
                await ctx.send(f"❌ Terjadi kesalahan saat mengedit file: {e}")

async def setup(bot):
    await bot.add_cog(CodeGenerator(bot))