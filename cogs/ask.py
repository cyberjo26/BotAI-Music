from discord.ext import commands
from hercai import Hercai

class Ask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.herc = Hercai("")

    @commands.command(name='ask')
    async def ask(self, ctx, *, question: str = None):
        if question is None:
            await ctx.send("Mohon sertakan pertanyaan setelah perintah !ask. Contoh: `!ask Apa kabar?`")
            return

        question_result = self.herc.question(model="v3", content=question)
        response = question_result.get("reply", "Maaf, tidak ada jawaban yang tersedia.")
        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(Ask(bot))
