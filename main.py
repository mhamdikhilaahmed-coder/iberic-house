import discord
import os
import threading
from discord.ext import commands
from keep_alive import app

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("Iberic House conectado")
    await bot.tree.sync()

async def setup_hook():
    await bot.load_extension("cogs.tickets")

bot.setup_hook = setup_hook

def run_bot():
    bot.run(os.environ["TOKEN"])

if __name__ == "__main__":
    print("Iniciando Flask + Discord bot")
    threading.Thread(target=run_bot).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
