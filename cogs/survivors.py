from config.shelter import SHELTER_LEVELS
from datetime import datetime

import discord
from views.combat import BaulView
from discord.ext import commands
from utils.users import (
    get_or_create_survivor,
    get_effects,
    has_survivor,
    get_active_effects,
    get_or_create_shelter,
    rest_in_shelter,
    upgrade_shelter,
    get_current_weather,
    get_equipped_gear,
    revive_survivor,
)


class Survivors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando perfil
    @discord.app_commands.command(
        name="perfil", description="Muestra tu registro de superviviente"
    )
    async def perfil(self, interaction: discord.Interaction):
        survivor = get_or_create_survivor(
            str(interaction.user.id), interaction.user.display_name
        )
        effects = get_effects(str(interaction.user.id))
        active_effects = get_active_effects(str(interaction.user.id))
        fecha = datetime.strptime(survivor["created_at"], "%Y-%m-%d %H:%M:%S").strftime(
            "%d/%m/%Y"
        )

        # Acceso seguro a las columnas row de sqlite3
        nivel = survivor["level"] if "level" in survivor.keys() else 1
        xp = survivor["xp"] if "xp" in survivor.keys() else 0
        xp_max = nivel * 100

        # Obtenemos el equipo actual (Arma y Armadura)
        arma_eq, armadura_eq = get_equipped_gear(str(interaction.user.id))

        effects_text = (
            "\n".join(f"• {e['effect']}" for e in effects) if effects else "Ninguno"
        )
        active_effects_text = (
            "\n".join(f"• {e['effect']} ({e['duration']} exp.)" for e in active_effects)
            if active_effects
            else "Ninguno"
        )

        await interaction.response.send_message(
            f"🕯️ **Registro de Superviviente**\n\n"
            f"🔍 Nombre: {survivor['name']}\n"
            f"⭐ Nivel: {nivel} (XP: {xp}/{xp_max})\n"
            f"👁️ Condición: {survivor['status']}\n"
            f"❤️ Vida: {survivor['health']}/100\n"
            f"🦴 Overos: {survivor['overos']}\n\n"
            f"⚔️ **Equipamiento:**\n"
            f"• Arma: {arma_eq or 'Ninguna'}\n"
            f"• Armadura: {armadura_eq or 'Ninguna'}\n\n"
            f"🧪 Efectos negativos:\n{effects_text}\n\n"
            f"✨ Efectos activos:\n{active_effects_text}\n\n"
            f"📜 Registrado: {fecha}"
        )

    # Comando de refugio
    @discord.app_commands.command(
        name="refugio", description="Gestiona tu refugio, descansa y mejóralo."
    )
    async def refugio(self, interaction: discord.Interaction):
        if not has_survivor(str(interaction.user.id)):
            await interaction.response.send_message(
                "❌ Primero debes crear tu perfil con **/perfil**."
            )
            return

        shelter = get_or_create_shelter(str(interaction.user.id))
        nivel = shelter["level"]
        datos_actuales = SHELTER_LEVELS[nivel]

        embed = discord.Embed(
            title=f"⛺ Refugio: {datos_actuales['nombre']} (Nivel {nivel})",
            description=datos_actuales["descripcion"],
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="💤 Curación al dormir",
            value=f"+{datos_actuales['cura_descanso']} Vida",
        )
        embed.add_field(
            name="⏳ Tiempo de espera",
            value=f"{datos_actuales['cooldown_horas']} Horas",
        )

        if nivel + 1 in SHELTER_LEVELS:
            datos_siguientes = SHELTER_LEVELS[nivel + 1]
            req_overos = datos_siguientes["costo_overos"]
            req_items = ", ".join(
                [f"{k} (x{v})" for k, v in datos_siguientes["costo_items"].items()]
            )
            if not req_items:
                req_items = "Ninguno"

            embed.add_field(
                name=f"⬆️ Requisitos Nivel {nivel + 1}",
                value=f"**Overos:** {req_overos}\n**Objetos:** {req_items}",
                inline=False,
            )

        class RefugioView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)

            @discord.ui.button(
                label="Descansar", emoji="💤", style=discord.ButtonStyle.success
            )
            async def btn_descansar(
                self, btn_interact: discord.Interaction, button: discord.ui.Button
            ):
                if btn_interact.user.id != interaction.user.id:
                    return await btn_interact.response.send_message(
                        "❌ Este no es tu refugio.", ephemeral=True
                    )

                exito, mensaje = rest_in_shelter(str(btn_interact.user.id))
                await btn_interact.response.send_message(mensaje, ephemeral=not exito)

            @discord.ui.button(
                label="Mejorar Refugio", emoji="⬆️", style=discord.ButtonStyle.primary
            )
            async def btn_mejorar(
                self, btn_interact: discord.Interaction, button: discord.ui.Button
            ):
                if btn_interact.user.id != interaction.user.id:
                    return await btn_interact.response.send_message(
                        "❌ Este no es tu refugio.", ephemeral=True
                    )

                exito, mensaje = upgrade_shelter(str(btn_interact.user.id))
                await btn_interact.response.send_message(mensaje, ephemeral=not exito)

                if exito:
                    for item in self.children:
                        item.disabled = True
                    await btn_interact.message.edit(view=self)

        view = RefugioView()

        if nivel + 1 not in SHELTER_LEVELS:
            view.children[1].disabled = True
            view.children[1].label = "Nivel Máximo"

        await interaction.response.send_message(embed=embed, view=view)


   #Comando de clima
    @discord.app_commands.command(
        name="clima", description="Revisa la hora y el clima actual en el páramo."
    )
    async def clima(self, interaction: discord.Interaction):
        clima_nombre, clima_data, es_dia = get_current_weather()

        momento_icono = "☀️ De Día" if es_dia else "🌙 De Noche"
        color_embed = discord.Color.blue() if es_dia else discord.Color.dark_purple()

        embed = discord.Embed(
            title=f"🌍 Estado del Mundo: {momento_icono}",
            description=f"**Clima actual:** {clima_data['emoji']} {clima_nombre}\n*{clima_data['desc']}*",
            color=color_embed,
        )

        # Mostramos los efectos del clima
        bono_loot = clima_data["loot_bonus"]
        peligro = clima_data["peligro"]

        if not es_dia:
            bono_loot += 10
            peligro += 15
            embed.set_footer(
                text="La noche aumenta un 15% el peligro y un 10% el botín."
            )

        embed.add_field(name="⚠️ Peligro de daño", value=f"+{peligro}% extra")
        embed.add_field(name="🎁 Probabilidad de botín", value=f"+{bono_loot}% extra")

        await interaction.response.send_message(embed=embed)

    # Comando para reanimarse
    @discord.app_commands.command(
        name="reanimación", description="Revive tras esperar 1 hora desde tu muerte."
    )
    async def revivir(self, interaction: discord.Interaction):
        await interaction.response.defer()
        exito, msg = revive_survivor(str(interaction.user.id))

        color = discord.Color.green() if exito else discord.Color.red()
        embed = discord.Embed(title="⚰️ Resurrección", description=msg, color=color)
        await interaction.followup.send(embed=embed)

    # Comando para ver el baúl
    @discord.app_commands.command(
        name="baul",
        description="Abre el baúl del refugio para guardar o sacar objetos.",
    )
    async def baul(self, interaction: discord.Interaction):
        await interaction.response.defer()

        view = BaulView(interaction.user.id)
        embed = await view.generar_embed(interaction.user.id)

        await interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Survivors(bot))
