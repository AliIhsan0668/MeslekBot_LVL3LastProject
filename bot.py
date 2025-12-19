import discord
from discord.ext import commands
from discord.ui import View
import sqlite3
import aiohttp
from config import TOKEN

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="*", intents=intents)

conn = sqlite3.connect("meslekler.db")
cursor = conn.cursor()

user_answers = {}

async def ollama_sor(prompt):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            }
        ) as r:
            data = await r.json()
            cevap = data.get("response", "").strip()
            if not cevap:
                return "Yapay zeka şu an cevap üretemedi."
            return cevap[:1800]

class StartView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Başla", style=discord.ButtonStyle.primary)
    async def basla(self, interaction: discord.Interaction, button):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id] = {}
        await interaction.followup.send(
            "Hangi alandasın?",
            view=AlanView(),
            ephemeral=True
        )

class AlanView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Sayısal", style=discord.ButtonStyle.secondary)
    async def sayisal(self, interaction: discord.Interaction, button):
        await self.handle(interaction, "Sayısal")

    @discord.ui.button(label="Sözel", style=discord.ButtonStyle.secondary)
    async def sozel(self, interaction: discord.Interaction, button):
        await self.handle(interaction, "Sözel")

    async def handle(self, interaction, alan):
        await interaction.response.defer(ephemeral=True)

        user_answers[interaction.user.id]["alan"] = alan

        await interaction.followup.send(
            "En çok ilgilendiğin alanı yaz.",
            ephemeral=True
        )

        msg = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == interaction.user.id
        )

        user_answers[interaction.user.id]["ilgi"] = msg.content

        await interaction.followup.send(
            "Teknolojiyle ilgileniyor musun?",
            view=TeknolojiView(),
            ephemeral=True
        )

class TeknolojiView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Evet", style=discord.ButtonStyle.success)
    async def evet(self, interaction: discord.Interaction, button):
        await self.finish(interaction, "Evet")

    @discord.ui.button(label="Hayır", style=discord.ButtonStyle.danger)
    async def hayir(self, interaction: discord.Interaction, button):
        await self.finish(interaction, "Hayır")

    async def finish(self, interaction, teknoloji):
        await interaction.response.defer()

        data = user_answers.get(interaction.user.id)
        if not data:
            await interaction.followup.send("Oturum bulunamadı.")
            return

        data["teknoloji"] = teknoloji

        prompt = f"""
Kullanıcı bilgileri:
Alan: {data['alan']}
İlgi alanı: {data['ilgi']}
Teknoloji ilgisi: {data['teknoloji']}

Bu bilgilere göre kullanıcıya detaylı bir kariyer önerisi yap.
Hangi mesleklerin uygun olduğunu ve nedenlerini açıkla.
"""

        ai_cevap = await ollama_sor(prompt)

        cursor.execute("SELECT meslek FROM meslekler ORDER BY RANDOM() LIMIT 1")
        db_meslek = cursor.fetchone()[0]

        await interaction.followup.send(
            f"Yapay zeka kariyer önerisi:\n{ai_cevap}\n\nVeritabanı önerisi: {db_meslek}"
        )

        user_answers.pop(interaction.user.id, None)

@bot.command()
async def kariyer(ctx):
    await ctx.send(
        "Kariyer testini başlatmak için butona bas.",
        view=StartView()
    )

bot.run(TOKEN)
