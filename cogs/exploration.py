import discord
import random
from discord.ext import commands

from config.locations import LOCATIONS
from config.events import EVENTS
from views.incursions import IncursionView
from datetime import datetime, timedelta
from utils.users import (
    has_survivor,
    get_or_create_survivor,
    increase_effect_progress,
    update_effects,
    apply_effect_damage,
    get_last_explore,
    update_quest_progress,
    add_item,
    add_effect,
    add_overos,
    get_current_weather,
    update_health,
    reduce_active_effects,
    remove_item,
    update_last_explore,
    resolve_event_condition,
    update_stat,
    add_xp,
    has_active_effect,
)


class Exploration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando explorar
    @discord.app_commands.command(
        name="explorar", description="Explora los alrededores..."
    )
    @discord.app_commands.describe(lugar="Lugar a explorar.")
    @discord.app_commands.choices(
        lugar=[
            discord.app_commands.Choice(name=f"{d['emoji']} {n}", value=n)
            for n, d in LOCATIONS.items()
        ]
    )
    async def explorar(
        self,
        interaction: discord.Interaction,
        lugar: discord.app_commands.Choice[str] = None,
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
                "💀 Estás muerto. No puedes explorar hasta volver a la vida.",
                ephemeral=True,
            )

        increase_effect_progress(str(interaction.user.id))
        update_effects(str(interaction.user.id))
        apply_effect_damage(str(interaction.user.id))

        last_explore = get_last_explore(str(interaction.user.id))
        if last_explore:
            ultima_exploracion = datetime.strptime(last_explore, "%Y-%m-%d %H:%M:%S")
            cooldown = timedelta(minutes=2)
            if datetime.now() < ultima_exploracion + cooldown:
                restante = (ultima_exploracion + cooldown) - datetime.now()
                minutos = restante.seconds // 60
                segundos = restante.seconds % 60
                return await interaction.response.send_message(
                    f"⏳ Aún no puedes explorar. Espera {minutos} minutos y {segundos} segundos."
                )

        lugar_nombre = None
        if lugar:
            lugar_nombre = lugar.value if hasattr(lugar, "value") else str(lugar)

        eventos_especificos = [
            e for e in EVENTS if e.get("lugares") and lugar_nombre in e["lugares"]
        ]
        eventos_globales = [e for e in EVENTS if not e.get("lugares")]

        if lugar_nombre and eventos_especificos:
            if random.random() <= 0.75:
                eventos_disponibles = eventos_especificos
            else:
                eventos_disponibles = eventos_globales
        else:
            eventos_disponibles = eventos_globales

        tiene_moral = has_active_effect(str(interaction.user.id), "moral")
        pesos = []
        for evento_posible in eventos_disponibles:
            peso = evento_posible["chance"]
            if tiene_moral:
                if evento_posible.get("damage", 0) > 0:
                    peso *= 0.8
                if evento_posible.get("item") is not None:
                    peso *= 1.1
            pesos.append(peso)

        evento = random.choices(eventos_disponibles, weights=pesos, k=1)[0]
        evento, item_consumido = resolve_event_condition(
            str(interaction.user.id), evento
        )

        tiene_energia = has_active_effect(str(interaction.user.id), "energia")
        evitar_dano = False
        if (
            tiene_energia
            and evento.get("damage", 0) > 0
            and evento.get("damage", 0) <= 5
            and random.random() <= 0.5
        ):
            evitar_dano = True

        reduce_active_effects(str(interaction.user.id))

        if isinstance(evento["overos"], tuple):
            cantidad_overos = random.randint(evento["overos"][0], evento["overos"][1])
        else:
            cantidad_overos = evento["overos"]

        moral_bonus = (
            max(1, round(cantidad_overos * 0.1))
            if tiene_moral and cantidad_overos > 0
            else 0
        )
        clima_nombre, clima_data, es_dia = get_current_weather()

        peligro_extra = clima_data["peligro"] + (15 if not es_dia else 0)
        dano_final = evento.get("damage", 0)
        if dano_final > 0:
            dano_final = round(dano_final * (1 + (peligro_extra / 100)))

        bonus_loot_total = clima_data["loot_bonus"] + (10 if not es_dia else 0)
        if cantidad_overos > 0 and bonus_loot_total > 0:
            bonus_clima = max(1, round(cantidad_overos * (bonus_loot_total / 100)))
            cantidad_overos += bonus_clima

        if cantidad_overos > 0:
            add_overos(str(interaction.user.id), cantidad_overos)

        mensaje = (
            f"{LOCATIONS[lugar_nombre]['emoji']} **{lugar_nombre}**\n\n{evento['mensaje']}"
            if lugar_nombre
            else evento["mensaje"]
        )

        if cantidad_overos > 0:
            mensaje += f"\n\n🦴 Has encontrado **{cantidad_overos} Overos**."
        if moral_bonus > 0:
            mensaje += f"\n\n🍫 Tu buen ánimo te ayudó a encontrar **{moral_bonus} Overos** extra."

        if evitar_dano:
            mensaje += (
                "\n\n⚡ Gracias a tu energía, lograste esquivar el daño a tiempo."
            )
        else:
            if dano_final > 0:
                update_health(str(interaction.user.id), -dano_final)
                mensaje += f"\n\n❤️ Has perdido **{dano_final}** puntos de vida (Afectado por el clima)."
            if evento["effect"] is not None:
                add_effect(str(interaction.user.id), evento["effect"])
                mensaje += f"\n\n🧪 Nuevo efecto: **{evento['effect']}**"

        items_encontrados = []

        if evento.get("item") is not None:
            add_item(str(interaction.user.id), evento["item"], 1)
            items_encontrados.append(f"**{evento['item']} (x1)**")

        if "items" in evento:
            for loot in evento["items"]:
                if random.random() <= (loot["chance"] / 100.0):
                    cantidad = random.randint(loot["cantidad"][0], loot["cantidad"][1])
                    if cantidad > 0:
                        add_item(str(interaction.user.id), loot["item"], cantidad)
                        items_encontrados.append(f"**{loot['item']} (x{cantidad})**")

        if items_encontrados:
            mensaje += f"\n\n🎒 Has encontrado: {', '.join(items_encontrados)}."

        if item_consumido is not None:
            remove_item(str(interaction.user.id), item_consumido, 1)
            mensaje += f"\n\n🔧 Has usado: **{item_consumido}**."

        update_last_explore(str(interaction.user.id))

        if lugar_nombre:
            update_quest_progress(str(interaction.user.id), "exploracion", lugar_nombre)

        nuevos_logros = update_stat(str(interaction.user.id), "explorations")
        for logro in nuevos_logros:
            mensaje += (
                f"\n\n🏆 **¡LOGRO DESBLOQUEADO!** {logro['emoji']} **{logro['nombre']}**\n*{logro['descripcion']}*\n🎁 Recompensa: 🦴 {logro['recompensa_overos']} Overos"
                + (
                    f" y 📦 {logro['recompensa_item']}"
                    if logro["recompensa_item"]
                    else ""
                )
            )
        add_xp(str(interaction.user.id), 25)
        await interaction.response.send_message(mensaje)

    # Comando incursionar
    @discord.app_commands.command(
        name="incursionar",
        description="Inicia una exploración profunda y narrativa por habitaciones en una zona.",
    )
    @discord.app_commands.describe(lugar="Zona que deseas incursionar a fondo.")
    @discord.app_commands.choices(
        lugar=[
            discord.app_commands.Choice(name=f"{d['emoji']} {n}", value=n)
            for n, d in LOCATIONS.items()
        ]
    )
    async def incursionar(
        self, interaction: discord.Interaction, lugar: discord.app_commands.Choice[str]
    ):
        if not has_survivor(str(interaction.user.id)):
            return await interaction.response.send_message(
                "❌ Primero debes crear tu perfil con **/perfil**."
            )

        lugar_nombre = lugar.value if hasattr(lugar, "value") else str(lugar)

        from config.incursions import INCURSIONS

        if lugar_nombre not in INCURSIONS:
            return await interaction.response.send_message(
                f"⚠️ La incursión profunda para **{lugar_nombre}** todavía está mapeándose. Prueba con el **Hospital**.",
                ephemeral=True,
            )

        data_zona = INCURSIONS[lugar_nombre]
        nodo_inicio = data_zona["nodos"]["inicio"]

        embed = discord.Embed(
            title=data_zona["titulo"],
            description=nodo_inicio["descripcion"],
            color=data_zona["color"],
        )

        view = IncursionView(str(interaction.user.id), lugar_nombre)
        await interaction.response.send_message(embed=embed, view=view)


# Función requerida para registrar el Cog en el bot
async def setup(bot):
    await bot.add_cog(Exploration(bot))
