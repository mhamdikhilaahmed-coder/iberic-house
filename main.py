import discord, os, threading
from discord.ext import commands
from keep_alive import run

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("Iberic House conectado")
    await bot.tree.sync()

async def setup_hook():
    await bot.load_extension("cogs.tickets")

bot.setup_hook = setup_hook
threading.Thread(target=run).start()
bot.run(os.environ["TOKEN"])
