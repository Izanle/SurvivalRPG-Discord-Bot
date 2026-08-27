import discord
import random   
from discord.ext import commands

from config.npcs import NPCS, RUMORES
from utils.users import (
    has_survivor,
    get_overos,
    add_overos,
    update_health,
    get_effects,
    remove_effect,
    add_item,
)

class NPCs(commands.Cog):
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

    async def setup(bot):
        await bot.add_cog(NPCS(bot))