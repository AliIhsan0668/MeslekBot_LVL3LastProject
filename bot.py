import discord
from discord.ext import commands
import sqlite3
from config import TOKEN

conn = sqlite3.connect("kariyer.db")
cursor = conn.cursor()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="*", intents=intents)

def meslek_belirle(yas, alan, ilgi, teknoloji):
    ilgi = ilgi.lower()
    if alan == "sayisal" and teknoloji == "evet":
        if "oyun" in ilgi:
            return "Oyun Geliştirici"
        if "çizim" in ilgi or "tasarım" in ilgi:
            return "UI/UX Tasarımcı"
        return "Yazılım Geliştirici"
    if alan == "sayisal" and teknoloji == "hayir":
        return "Matematik Öğretmeni"
    if alan == "sozel" and teknoloji == "evet":
        if "yazı" in ilgi or "edit" in ilgi:
            return "İçerik Üretici"
        return "Dijital Pazarlama Uzmanı"
    if alan == "sozel" and teknoloji == "hayir":
        if "konuşmak" in ilgi or "insan" in ilgi:
            return "Psikolog veya Danışman"
        return "Öğretmen"
    return "İnsan Kaynakları Uzmanı"


class AlanButon(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user
        self.value = None

    async def interaction_check(self, interaction):
        return interaction.user == self.user

    @discord.ui.button(label="Sayısal", style=discord.ButtonStyle.primary)
    async def sayisal(self, interaction, button):
        self.value = "sayisal"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Sözel", style=discord.ButtonStyle.primary)
    async def sozel(self, interaction, button):
        self.value = "sozel"
        self.stop()
        await interaction.response.defer()


class EvetHayirButon(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user
        self.value = None

    async def interaction_check(self, interaction):
        return interaction.user == self.user

    @discord.ui.button(label="Evet", style=discord.ButtonStyle.primary)
    async def evet(self, interaction, button):
        self.value = "evet"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Hayır", style=discord.ButtonStyle.primary)
    async def hayir(self, interaction, button):
        self.value = "hayir"
        self.stop()
        await interaction.response.defer()


@bot.command()
async def kariyer(ctx):
    user = ctx.author

    await ctx.send("Kariyer formu başlıyor.")

    await ctx.send("Yaşın kaç?")
    yas_msg = await bot.wait_for("message", check=lambda m: m.author == user)
    yas = yas_msg.content

    view1 = AlanButon(user)
    msg = await ctx.send("Hangi alandasın?", view=view1)
    await view1.wait()
    alan = view1.value

    await msg.edit(content="En çok neyle ilgileniyorsun?", view=None)
    ilgi_msg = await bot.wait_for("message", check=lambda m: m.author == user)
    ilgi = ilgi_msg.content

    view2 = EvetHayirButon(user)
    msg2 = await ctx.send("Teknolojiye ilgin var mı?", view=view2)
    await view2.wait()
    teknoloji = view2.value

    sonuc = meslek_belirle(yas, alan, ilgi, teknoloji)

    cursor.execute("""
    INSERT INTO cevaplar (user_id, yas, alan, ilgi, teknoloji, sonuc)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user.id, yas, alan, ilgi, teknoloji, sonuc))
    conn.commit()

    await ctx.send(f"Sana uygun meslek: {sonuc}")

bot.run(TOKEN)
