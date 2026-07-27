import discord
import random
from discord.ext import commands

from views.combat import CombatView
from config.locations import LOCATIONS
from config.enemies import ENEMIES
from utils.users import has_survivor, get_or_create_survivor


# ==========================================
# SISTEMA DE COMBATE PVE (FASE 8 + 9 + 10 + EQUIPO)
# ==========================================
class CombatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="cazar",
        description="Adéntrate en una zona peligrosa para buscar enemigos.",
    )
    @discord.app_commands.describe(lugar="Zona en la que quieres cazar (opcional).")
    @discord.app_commands.choices(
        lugar=[
            discord.app_commands.Choice(name=f"{datos['emoji']} {nombre}", value=nombre)
            for nombre, datos in LOCATIONS.items()
        ]
    )
    async def cazar(
        self,
        interaction: discord.Interaction,
        lugar: discord.app_commands.Choice[str] | None = None,
    ):
        if not has_survivor(str(interaction.user.id)):
            return await interaction.response.send_message(
                "❌ Primero debes crear tu perfil con **/perfil**."
            )

        survivor = get_or_create_survivor(
            str(interaction.user.id), interaction.user.display_name
        )
        if survivor["status"] == "Muerto":
            return await interaction.response.send_message(
                "💀 Estás muerto.", ephemeral=True
            )

        # Obtener el nombre del lugar si se proporcionó
        lugar_nombre = None
        if lugar:
            lugar_nombre = lugar.value if hasattr(lugar, "value") else str(lugar)

        # Separar enemigos globales y específicos de la zona
        enemigos_especificos = {
            k: v
            for k, v in ENEMIES.items()
            if v.get("lugares") and lugar_nombre in v["lugares"]
        }
        enemigos_globales = {k: v for k, v in ENEMIES.items() if not v.get("lugares")}

        # Lógica de probabilidad 75/25 igual que la exploración
        pool_enemigos = {}
        if lugar_nombre and enemigos_especificos:
            if random.random() <= 0.75:
                pool_enemigos = enemigos_especificos
            else:
                pool_enemigos = enemigos_globales
        else:
            # Si no hay lugar o el lugar no tiene enemigos, usar globales
            pool_enemigos = enemigos_globales

        # Si por alguna razón no hay enemigos globales (seguridad), tomar todos
        if not pool_enemigos:
            pool_enemigos = ENEMIES

        # Extraer nombres y pesos del pool seleccionado
        nombres = list(pool_enemigos.keys())
        pesos = [pool_enemigos[n].get("peso", 50) for n in nombres]

        # Elegir enemigo basado en su peso
        enemigo_nombre = random.choices(nombres, weights=pesos, k=1)[0]
        enemigo_data = dict(ENEMIES[enemigo_nombre])

        embed = discord.Embed(
            title="⚔️ ¡Peligro!",
            description=f"Te topaste con un **{enemigo_nombre}**.",
            color=enemigo_data["color"],
        )
        embed.add_field(
            name="Tu Vida", value=f"❤️ {survivor['health']}/100", inline=True
        )
        embed.add_field(
            name="Vida Enemigo",
            value=f"🩸 {enemigo_data['hp']}/{enemigo_data['hp']}",
            inline=True,
        )
        await interaction.response.send_message(
            embed=embed, view=CombatView(interaction, enemigo_nombre, enemigo_data)
        )


async def setup(bot):
    await bot.add_cog(CombatCog(bot))
