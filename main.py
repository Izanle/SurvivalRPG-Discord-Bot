import os

import discord
from dotenv import load_dotenv


load_dotenv()


TOKEN = os.getenv("DISCORD_TOKEN")

bot = discord.Client(intents=discord.Intents.default())

@bot.event
async def on_ready():

    print(f"✅ Conectado como {bot.user}")

    print("Extensiones cargadas:")
    print(bot.extensions)

    try:

        sincronizados = await bot.tree.sync()

        print("Comandos sincronizados:")

        for comando in sincronizados:
            print(f"- {comando.name}")

    except Exception as e:

        print(e)

bot.run(TOKEN)
