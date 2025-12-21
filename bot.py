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
            return cevap[:1800] if cevap else "Cevap üretilemedi."

class StartView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Başla", style=discord.ButtonStyle.primary)
    async def basla(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id] = {}
        await interaction.followup.send("Hangi alandasın?", view=AlanView(), ephemeral=True)

class AlanView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Sayısal", style=discord.ButtonStyle.secondary)
    async def sayisal(self, interaction, button):
        await self.handle(interaction, "Sayısal")

    @discord.ui.button(label="Sözel", style=discord.ButtonStyle.secondary)
    async def sozel(self, interaction, button):
        await self.handle(interaction, "Sözel")

    async def handle(self, interaction, alan):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id]["alan"] = alan

        await interaction.followup.send("En çok ilgilendiğin alanı yaz:", ephemeral=True)
        msg = await bot.wait_for("message", check=lambda m: m.author.id == interaction.user.id)
        user_answers[interaction.user.id]["ilgi"] = msg.content

        await interaction.followup.send("Teknolojiyle ilgileniyor musun?", view=TeknolojiView(), ephemeral=True)

class TeknolojiView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Evet", style=discord.ButtonStyle.success)
    async def evet(self, interaction, button):
        await self.next(interaction, "Evet")

    @discord.ui.button(label="Hayır", style=discord.ButtonStyle.danger)
    async def hayir(self, interaction, button):
        await self.next(interaction, "Hayır")

    async def next(self, interaction, teknoloji):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id]["teknoloji"] = teknoloji
        await interaction.followup.send("Üniversite düşünüyor musun?", view=UniversiteView(), ephemeral=True)

class UniversiteView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Evet", style=discord.ButtonStyle.success)
    async def evet(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id]["universite"] = "Evet"
        await interaction.followup.send("Üniversite sınavına girdin mi?", view=UniSinavView(), ephemeral=True)

    @discord.ui.button(label="Hayır", style=discord.ButtonStyle.danger)
    async def hayir(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id]["universite"] = "Hayır"
        await interaction.followup.send("İnsanlarla iletişimi sever misin?", view=IletisimView(), ephemeral=True)

class UniSinavView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Evet", style=discord.ButtonStyle.success)
    async def evet(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id]["uni_sinav"] = "Evet"
        await interaction.followup.send("Üniversite türü tercihin?", view=UniTurView(), ephemeral=True)

    @discord.ui.button(label="Hayır", style=discord.ButtonStyle.danger)
    async def hayir(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id]["uni_sinav"] = "Hayır"
        await interaction.followup.send("Üniversite türü tercihin?", view=UniTurView(), ephemeral=True)

class UniTurView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Devlet", style=discord.ButtonStyle.secondary)
    async def devlet(self, interaction, button):
        await self.next(interaction, "Devlet")

    @discord.ui.button(label="Vakıf", style=discord.ButtonStyle.secondary)
    async def vakif(self, interaction, button):
        await self.next(interaction, "Vakıf")

    @discord.ui.button(label="Fark etmez", style=discord.ButtonStyle.secondary)
    async def fark(self, interaction, button):
        await self.next(interaction, "Fark etmez")

    async def next(self, interaction, secim):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id]["uni_tur"] = secim
        await interaction.followup.send("Eğitim şekli tercihin?", view=EgitimView(), ephemeral=True)

class EgitimView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Örgün", style=discord.ButtonStyle.secondary)
    async def orgun(self, interaction, button):
        await self.next(interaction, "Örgün")

    @discord.ui.button(label="Uzaktan", style=discord.ButtonStyle.secondary)
    async def uzaktan(self, interaction, button):
        await self.next(interaction, "Uzaktan")

    @discord.ui.button(label="Fark etmez", style=discord.ButtonStyle.secondary)
    async def fark(self, interaction, button):
        await self.next(interaction, "Fark etmez")

    async def next(self, interaction, secim):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id]["egitim"] = secim
        await interaction.followup.send("İnsanlarla iletişimi sever misin?", view=IletisimView(), ephemeral=True)

class IletisimView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Evet", style=discord.ButtonStyle.success)
    async def evet(self, interaction, button):
        await self.next(interaction, "Evet")

    @discord.ui.button(label="Hayır", style=discord.ButtonStyle.danger)
    async def hayir(self, interaction, button):
        await self.next(interaction, "Hayır")

    async def next(self, interaction, secim):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id]["iletisim"] = secim
        await interaction.followup.send("Yaratıcı işleri sever misin?", view=YaraticilikView(), ephemeral=True)

class YaraticilikView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Evet", style=discord.ButtonStyle.success)
    async def evet(self, interaction, button):
        await self.next(interaction, "Evet")

    @discord.ui.button(label="Kısmen", style=discord.ButtonStyle.secondary)
    async def kismen(self, interaction, button):
        await self.next(interaction, "Kısmen")

    @discord.ui.button(label="Hayır", style=discord.ButtonStyle.danger)
    async def hayir(self, interaction, button):
        await self.next(interaction, "Hayır")

    async def next(self, interaction, secim):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id]["yaraticilik"] = secim
        await interaction.followup.send("Çalışma şekli tercihin?", view=CalismaView(), ephemeral=True)

class CalismaView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Masa Başı", style=discord.ButtonStyle.secondary)
    async def masa(self, interaction, button):
        await self.finish(interaction, "Masa Başı")

    @discord.ui.button(label="Hareketli", style=discord.ButtonStyle.secondary)
    async def saha(self, interaction, button):
        await self.finish(interaction, "Hareketli")

    async def finish(self, interaction, secim):
        await interaction.response.defer(ephemeral=True)
        user_answers[interaction.user.id]["calisma"] = secim

        data = user_answers[interaction.user.id]

        prompt = f"""
Alan: {data.get('alan')}
İlgi: {data.get('ilgi')}
Teknoloji: {data.get('teknoloji')}
Üniversite: {data.get('universite')}
Üniversite sınavı: {data.get('uni_sinav')}
Üniversite türü: {data.get('uni_tur')}
Eğitim şekli: {data.get('egitim')}
İletişim: {data.get('iletisim')}
Yaratıcılık: {data.get('yaraticilik')}
Çalışma şekli: {data.get('calisma')}

Bu bilgilere göre kariyer ve üniversite/bölüm önerisi yap.
"""

        cevap = await ollama_sor(prompt)
        await interaction.followup.send(cevap, ephemeral=True)

@bot.command()
async def kariyer(ctx):
    await ctx.send("Kariyer testini başlatmak için butona bas.", view=StartView())

# ================= EKLENEN KOMUTLAR =================

@bot.command()
async def yapimci(ctx):
    embed = discord.Embed(
        title="Yapımcı Bilgileri",
        description=(
            "Yapımcı: Ali İhsan Coşkun\n\n"
            "2009 doğumlu bir bilgisayarcı\n"
            "Hasan Hüseyin Akdede Fen Lisesi öğrencisi\n\n"
            "Bu bot, bitirme projesi kapsamında geliştirilmiştir."
        ),
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed)

@bot.command()
async def info(ctx):
    mesaj = (
        "Kariyer Botu Kullanım Bilgileri\n\n"
        "Bu bot, kullanıcıya uygun meslek ve üniversite/bölüm önerileri sunmak amacıyla geliştirilmiştir.\n\n"
        "Kullanım:\n"
        "1. *kariyer komutunu yazın.\n"
        "2. Ekrana gelen butonlardan size uygun olanları seçin.\n"
        "3. Gerekli yerlerde yazılı cevap verin.\n"
        "4. Tüm sorular tamamlandığında yapay zeka size özel bir öneri sunar.\n\n"
        "Komutlar:\n"
        "*kariyer : Kariyer testini başlatır\n"
        "*yapimci : Yapımcı bilgilerini gösterir\n"
        "*info    : Bu mesajı gösterir"
    )
    await ctx.send(mesaj)

bot.run(TOKEN)
