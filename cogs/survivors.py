from config.npcs import NPCS, RUMORES
from config.shelter import SHELTER_LEVELS
from datetime import datetime
import random

import discord
from discord.ext import commands
from config.quests import QUESTS
from utils.users import (
    get_or_create_survivor,
    add_overos,
    get_effects,
    remove_effect,
    update_health,
    get_inventory,
    add_item,
    has_survivor,
    get_active_effects,
    get_overos,
    get_or_create_shelter,
    rest_in_shelter,
    upgrade_shelter,
    get_active_quest,
    assign_random_quest,
    claim_quest_reward,
    abandon_quest,
    get_current_weather,
    get_unlocked_achievements,
    get_equipped_gear,
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

    # Comando npc
    @discord.app_commands.command(
        name="npc",
        description="Busca a otros supervivientes en la zona para interactuar.",
    )
    async def npc(self, interaction: discord.Interaction):
        if not has_survivor(str(interaction.user.id)):
            await interaction.response.send_message(
                "❌ Primero debes crear tu perfil con **/perfil**."
            )
            return

        opciones = [
            discord.SelectOption(
                label=nombre,
                description=datos["descripcion"][:100],
                emoji=datos["emoji"],
                value=nombre,
            )
            for nombre, datos in NPCS.items()
        ]

        select = discord.ui.Select(
            placeholder="¿A quién estás buscando?", options=opciones
        )

        async def select_callback(interaction_select: discord.Interaction):
            npc_nombre = select.values[0]
            datos_npc = NPCS[npc_nombre]

            embed = discord.Embed(
                title=f"{datos_npc['emoji']} {npc_nombre}",
                description=f"*{datos_npc['saludo']}*",
                color=datos_npc["color"],
            )

            view = discord.ui.View(timeout=120)

            if npc_nombre == "La Doctora":

                async def btn_curar_callback(btn_interact: discord.Interaction):
                    if str(btn_interact.user.id) != str(interaction.user.id):
                        return

                    costo = 50
                    if get_overos(str(btn_interact.user.id)) < costo:
                        return await btn_interact.response.send_message(
                            f"❌ Necesitas {costo} Overos para el tratamiento.",
                            ephemeral=True,
                        )

                    add_overos(str(btn_interact.user.id), -costo)
                    update_health(str(btn_interact.user.id), 100)

                    efectos = get_effects(str(btn_interact.user.id))
                    for efecto in efectos:
                        remove_effect(str(btn_interact.user.id), efecto["effect"])

                    await btn_interact.response.send_message(
                        "🩺 **La Doctora:** Listo. Te he vendado y limpiado las heridas. ¡Ten más cuidado ahí fuera!"
                    )

                btn_curar = discord.ui.Button(
                    label="Tratamiento Completo (50 Overos)",
                    style=discord.ButtonStyle.success,
                    emoji="❤️",
                )
                btn_curar.callback = btn_curar_callback
                view.add_item(btn_curar)

            elif npc_nombre == "El Informante":

                async def btn_rumor_callback(btn_interact: discord.Interaction):
                    if str(btn_interact.user.id) != str(interaction.user.id):
                        return

                    costo = 10
                    if get_overos(str(btn_interact.user.id)) < costo:
                        return await btn_interact.response.send_message(
                            f"❌ Necesitas {costo} Overos para comprar información.",
                            ephemeral=True,
                        )

                    add_overos(str(btn_interact.user.id), -costo)
                    rumor = random.choice(RUMORES)
                    await btn_interact.response.send_message(
                        f'🕵️ **El Informante susurra:** *"{rumor}"*'
                    )

                btn_rumor = discord.ui.Button(
                    label="Comprar Rumor (10 Overos)",
                    style=discord.ButtonStyle.primary,
                    emoji="🗣️",
                )
                btn_rumor.callback = btn_rumor_callback
                view.add_item(btn_rumor)

            elif npc_nombre == "El Mercader Errante":

                async def btn_comprar_callback(btn_interact: discord.Interaction):
                    if str(btn_interact.user.id) != str(interaction.user.id):
                        return

                    costo = 200
                    if get_overos(str(btn_interact.user.id)) < costo:
                        return await btn_interact.response.send_message(
                            f"❌ Necesitas {costo} Overos. ¡No hago caridad!",
                            ephemeral=True,
                        )

                    add_overos(str(btn_interact.user.id), -costo)
                    add_item(str(btn_interact.user.id), "Cóctel molotov", 1)
                    await btn_interact.response.send_message(
                        "🎒 **Mercader:** Un trato justo. Disfruta de tu Cóctel Molotov, úsalo con sabiduría."
                    )

                btn_comprar = discord.ui.Button(
                    label="Comprar Arma Especial (200 Overos)",
                    style=discord.ButtonStyle.danger,
                    emoji="🧨",
                )
                btn_comprar.callback = btn_comprar_callback
                view.add_item(btn_comprar)

            await interaction_select.response.edit_message(
                content=None, embed=embed, view=view
            )

        select.callback = select_callback
        view_inicial = discord.ui.View()
        view_inicial.add_item(select)

        await interaction.response.send_message(
            "Mira a tu alrededor. ¿Con quién quieres hablar?", view=view_inicial
        )

    # ==========================================
    # SISTEMA DE MUNDO DINÁMICO (FASE 10)
    # ==========================================
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

    # ==========================================
    # COMANDO DE LOGROS (FASE 11)
    # ==========================================
    @discord.app_commands.command(
        name="logros",
        description="Muestra tus medallas y logros desbloqueados en el páramo.",
    )
    async def logros(self, interaction: discord.Interaction):
        if not has_survivor(str(interaction.user.id)):
            return await interaction.response.send_message(
                "❌ Primero debes crear tu perfil con **/perfil**."
            )

        from config.achievements import ACHIEVEMENTS

        unlocked = get_unlocked_achievements(str(interaction.user.id))
        unlocked_ids = {row["achievement_id"]: row["unlocked_at"] for row in unlocked}

        embed = discord.Embed(
            title="🏆 Vitrina de Logros",
            description="Aquí están las medallas que has conseguido demostrando tu valía.",
            color=discord.Color.gold(),
        )

        for ach_id, data in ACHIEVEMENTS.items():
            if ach_id in unlocked_ids:
                fecha = unlocked_ids[ach_id][:10]  # Tomamos solo el año, mes y día
                embed.add_field(
                    name=f"{data['emoji']} {data['nombre']} (Desbloqueado: {fecha})",
                    value=f"*{data['descripcion']}*",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="🔒 Logro Oculto",
                    value="*Sigue explorando y sobreviviendo para desbloquearlo.*",
                    inline=False,
                )

        if not unlocked_ids:
            embed.description = "Aún no has desbloqueado ningún logro. ¡Sal ahí fuera y completa misiones!"

        await interaction.response.send_message(embed=embed)

    # ==========================================
    # SISTEMA DE MISIONES (FASE 9)
    # ==========================================
    @discord.app_commands.command(
        name="misiones",
        description="Revisa el tablón de anuncios y gestiona tu misión actual.",
    )
    async def misiones(self, interaction: discord.Interaction):
        if not has_survivor(str(interaction.user.id)):
            return await interaction.response.send_message(
                "❌ Primero debes crear tu perfil con **/perfil**."
            )

        quest = get_active_quest(str(interaction.user.id))
        embed = discord.Embed(title="📜 Tablón de Misiones", color=discord.Color.gold())

        class MisionView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)

            @discord.ui.button(
                label="Aceptar Nueva",
                style=discord.ButtonStyle.primary,
                emoji="📌",
                disabled=bool(quest),
            )
            async def btn_aceptar(
                self, btn_interact: discord.Interaction, button: discord.ui.Button
            ):
                if btn_interact.user.id != interaction.user.id:
                    return
                exito, _ = assign_random_quest(str(btn_interact.user.id))
                if exito:
                    await btn_interact.response.send_message(
                        "✅ Has aceptado una misión. Usa `/misiones` de nuevo para verla.",
                        ephemeral=True,
                    )
                else:
                    await btn_interact.response.send_message(
                        "❌ Ya tienes una misión.", ephemeral=True
                    )

            @discord.ui.button(
                label="Reclamar Recompensa",
                style=discord.ButtonStyle.success,
                emoji="🎁",
                disabled=not bool(quest),
            )
            async def btn_reclamar(
                self, btn_interact: discord.Interaction, button: discord.ui.Button
            ):
                if btn_interact.user.id != interaction.user.id:
                    return

                # Guardamos la ID de la misión antes de que claim_quest_reward la elimine de la DB
                current_quest_id = quest["quest_id"] if quest else None

                exito, msg = claim_quest_reward(str(btn_interact.user.id))

                # Si la misión se completó con éxito, entregamos las recompensas múltiples
                if exito and current_quest_id:
                    q_data = QUESTS.get(current_quest_id)
                    if q_data and "recompensa_items" in q_data:
                        recompensas_extras = []
                        for reward in q_data["recompensa_items"]:
                            add_item(
                                str(btn_interact.user.id),
                                reward["item"],
                                reward["cantidad"],
                            )
                            recompensas_extras.append(
                                f"**{reward['item']} (x{reward['cantidad']})**"
                            )
                        if recompensas_extras:
                            msg += f"\n🎁 ¡También has recibido: {', '.join(recompensas_extras)}!"

                await btn_interact.response.send_message(msg, ephemeral=not exito)

            @discord.ui.button(
                label="Abandonar",
                style=discord.ButtonStyle.danger,
                emoji="🗑️",
                disabled=not bool(quest),
            )
            async def btn_abandonar(
                self, btn_interact: discord.Interaction, button: discord.ui.Button
            ):
                if btn_interact.user.id != interaction.user.id:
                    return
                abandon_quest(str(btn_interact.user.id))
                await btn_interact.response.send_message(
                    "🗑️ Misión abandonada.", ephemeral=True
                )

        if quest:
            q_data = QUESTS[quest["quest_id"]]
            embed.description = (
                f"**{q_data['emoji']} {q_data['titulo']}**\n{q_data['descripcion']}"
            )

            if q_data["tipo"] == "recoleccion":
                inv = get_inventory(str(interaction.user.id))
                cant = sum(i["quantity"] for i in inv if i["item"] == q_data["target"])
                embed.add_field(
                    name="En inventario",
                    value=f"{cant}/{q_data['required']} {q_data['target']}",
                )
            else:
                embed.add_field(
                    name="Progreso",
                    value=f"{quest['progress']}/{quest['required']} {q_data['target']}",
                )

            # Construimos el texto de las recompensas dinámicamente
            txt_recompensa = f"🦴 {q_data['recompensa_overos']} Overos"
            if "recompensa_items" in q_data:
                for reward in q_data["recompensa_items"]:
                    txt_recompensa += f"\n📦 {reward['item']} x{reward['cantidad']}"
            elif q_data.get("recompensa_item"):
                txt_recompensa += f"\n📦 {q_data['recompensa_item']} x1"
            else:
                txt_recompensa += "\n📦 Ninguno"

            embed.add_field(
                name="Recompensa",
                value=txt_recompensa,
            )
        else:
            embed.description = "No tienes ninguna misión activa en este momento. ¡Busca trabajo en el tablón!"

        await interaction.response.send_message(embed=embed, view=MisionView())


async def setup(bot):
    await bot.add_cog(Survivors(bot))
