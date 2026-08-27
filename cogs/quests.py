import discord

from config.quests import QUESTS
from utils.users import (has_survivor, 
    get_unlocked_achievements, 
    get_active_quest, 
    assign_random_quest, 
    claim_quest_reward, 
    add_item, 
    abandon_quest, 
    get_inventory)


# Comando logros
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

# Comando misiones
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
