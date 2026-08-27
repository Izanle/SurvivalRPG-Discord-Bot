import importlib
import discord
from discord import ui
from discord.ext import commands

from data.database import init_database


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

OWNER_ID = 1414035229286596719

COGS = [
    "cogs.general",
    "cogs.survivors",
    "cogs.cntrl",
    "cogs.admin",
    "cogs.combat",
    "cogs.exploration",
    "cogs.shop",
    "cogs.utilities",
    "cogs.npcs",
    "cogs.quests",
    "cogs.shop",
]


MODULES = [
    "config.items",
    "config.effects",
    "config.events",
    "config.status",
    "config.npcs",
    "config.recipes",
    "config.shop",
    "config.shelter",
    "config.locations",
    "config.incursions",
    "utils.users",
    "data.database",
]


class Bot(commands.Bot):

    async def setup_hook(self):

        init_database()

        for cog in COGS:
            await self.load_extension(cog)


bot = Bot(command_prefix="!", intents=intents)


class ReloadSelect(ui.Select):

    def __init__(self):

        opciones = [
            discord.SelectOption(label="Recargar todo", value="all", emoji="🔄")
        ]

        for module in MODULES:

            opciones.append(
                discord.SelectOption(label=module, value=module, emoji="⚙️")
            )

        for cog in COGS:

            opciones.append(discord.SelectOption(label=cog, value=cog, emoji="🤖"))

        super().__init__(placeholder="Selecciona un módulo...", options=opciones)

    async def callback(self, interaction: discord.Interaction):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ No tienes permiso.", ephemeral=True
            )

            return

        modulo = self.values[0]

        await interaction.response.defer(ephemeral=True)

        recargados = []

        try:

            if modulo == "all":

                for module in MODULES:

                    mod = importlib.import_module(module)

                    importlib.reload(mod)

                    recargados.append(f"⚙️ {module}")

                for cog in COGS:

                    await bot.reload_extension(cog)

                    recargados.append(f"🤖 {cog}")

            elif modulo in MODULES:

                mod = importlib.import_module(modulo)

                importlib.reload(mod)

                recargados.append(f"⚙️ {modulo}")

            elif modulo in COGS:

                await bot.reload_extension(modulo)

                recargados.append(f"🤖 {modulo}")

            await interaction.followup.send(
                "✅ **Recarga completada:**\n\n" + "\n".join(recargados), ephemeral=True
            )

        except Exception as e:

            await interaction.followup.send(f"❌ Error:\n```{e}```", ephemeral=True)


class ReloadView(ui.View):

    def __init__(self):

        super().__init__(timeout=60)

        self.add_item(ReloadSelect())


@bot.tree.command(name="reload", description="Recarga módulos del bot.")
async def reload(interaction: discord.Interaction):

    if interaction.user.id != OWNER_ID:

        await interaction.response.send_message("❌ No tienes permiso.", ephemeral=True)

        return

    await interaction.response.send_message(
        "🔄 Selecciona qué quieres recargar:", view=ReloadView(), ephemeral=True
    )