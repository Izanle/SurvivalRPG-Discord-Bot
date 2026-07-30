import random

import discord
from utils.users import (
    get_or_create_survivor,
    add_overos,
    update_health,
    get_inventory,
    add_item,
    use_item,
    update_quest_progress,
    update_stat,
    add_xp,
    get_equipped_gear,
    get_current_weather,
    add_effect,
)


class CombatView(discord.ui.View):
    def __init__(self, original_interact, e_name, e_data):
        super().__init__(timeout=120)
        self.original_interact = original_interact
        self.e_name = e_name
        self.e_hp, self.e_max_hp = e_data["hp"], e_data["hp"]
        self.e_data = e_data

    async def update_combat(self, interact: discord.Interaction, msg: str):
        s = get_or_create_survivor(str(interact.user.id), interact.user.display_name)
        embed = discord.Embed(
            title=f"⚔️ {self.e_data['emoji']} {self.e_name}",
            description=msg,
            color=self.e_data["color"],
        )
        embed.add_field(name="Tu Vida", value=f"❤️ {s['health']}/100", inline=True)
        embed.add_field(
            name="Vida Enemigo",
            value=f"🩸 {self.e_hp}/{self.e_max_hp}",
            inline=True,
        )
        if self.e_hp <= 0 or s["health"] <= 0:
            for btn in self.children:
                btn.disabled = True
        await interact.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Atacar", emoji="🗡️", style=discord.ButtonStyle.danger)
    async def btn_atacar(self, interact: discord.Interaction, btn: discord.ui.Button):
        if interact.user.id != self.original_interact.user.id:
            return

        # 1. Daño base del golpe
        player_dmg = random.randint(15, 25)

        # 2. Bono de arma equipada (Sistema de Equipamiento Oficial)
        arma_eq, _ = get_equipped_gear(str(interact.user.id))
        if arma_eq:
            from config.equipment import EQUIPMENT

            if arma_eq in EQUIPMENT:
                player_dmg += EQUIPMENT[arma_eq]["bonus_dano"]
        else:
            inventory = get_inventory(str(interact.user.id))
            if any(i["item"] == "Cóctel molotov" for i in inventory):
                player_dmg += 15

        self.e_hp -= player_dmg
        msg = f"🗡️ Atacaste y causaste **{player_dmg}** de daño.\n"

        if self.e_hp <= 0:
            self.e_hp = 0
            # --- FASE 12: Ganancia de XP por cazar ---
            add_xp(str(interact.user.id), 50)
            msg += f"\n💀 **¡Has derrotado a {self.e_name}!**"
            loot_o = random.randint(*self.e_data["loot_overos"])
            add_overos(str(interact.user.id), loot_o)
            msg += f"\n🦴 Obtuviste **{loot_o} Overos**."

            # Compatibilidad con el botín antiguo
            if self.e_data.get("loot_item") and random.random() > 0.5:
                add_item(str(interact.user.id), self.e_data["loot_item"], 1)
                msg += f"\n📦 Dejó caer: **{self.e_data['loot_item']} (x1)**."

            # NUEVO: Botín múltiple
            items_dropeados = []
            if "items" in self.e_data:
                for loot in self.e_data["items"]:
                    if random.random() <= (loot["chance"] / 100.0):
                        cantidad = random.randint(
                            loot["cantidad"][0], loot["cantidad"][1]
                        )
                        if cantidad > 0:
                            add_item(str(interact.user.id), loot["item"], cantidad)
                            items_dropeados.append(f"**{loot['item']} (x{cantidad})**")

            if items_dropeados:
                msg += f"\n📦 Dejó caer: {', '.join(items_dropeados)}."

            update_quest_progress(str(interact.user.id), "caceria", self.e_name)

            # --- NUEVO: SISTEMA DINÁMICO DE LOGROS POR JEFE ---
            logro_id = self.e_data.get("logro_derrota")
            if logro_id:
                from utils.users import unlock_achievement

                logro_jefe = unlock_achievement(str(interact.user.id), logro_id)
                if logro_jefe:
                    msg += (
                        f"\n\n🏆 **¡LOGRO ESPECIAL DESBLOQUEADO!** {logro_jefe['emoji']} **{logro_jefe['nombre']}**\n"
                        f"*{logro_jefe['descripcion']}*\n"
                        f"🎁 Recompensa: 🦴 {logro_jefe['recompensa_overos']} Overos"
                    )
                    if logro_jefe.get("recompensa_item"):
                        msg += f" y 📦 {logro_jefe['recompensa_item']}"

            # --- LOGROS: Actualizamos estadística general de enemigos derrotados ---
            nuevos_logros = update_stat(str(interact.user.id), "enemies_defeated")
            for logro in nuevos_logros:
                msg += (
                    f"\n\n🏆 **¡LOGRO DESBLOQUEADO!** {logro['emoji']} **{logro['nombre']}**\n"
                    f"*{logro['descripcion']}*\n"
                    f"🎁 Recompensa: 🦴 {logro['recompensa_overos']} Overos"
                    + (
                        f" y 📦 {logro['recompensa_item']}"
                        if logro.get("recompensa_item")
                        else ""
                    )
                )

        else:
            enemy_d = random.randint(*self.e_data["daño"])

            # Nota: Asegúrate de tener importada get_current_weather arriba en el archivo
            from config.world import get_current_weather

            _, clima_data, es_dia = get_current_weather()
            multiplicador = (
                1.0 + (clima_data["peligro"] / 100) + (0.15 if not es_dia else 0)
            )
            enemy_d = round(enemy_d * multiplicador)

            # --- APLICAMOS REDUCCIÓN DE ARMADURA ---
            _, armadura_eq = get_equipped_gear(str(interact.user.id))
            if armadura_eq:
                from config.equipment import EQUIPMENT

                if armadura_eq in EQUIPMENT:
                    reduccion = EQUIPMENT[armadura_eq]["reduccion_dano"]
                    enemy_d = round(enemy_d * (1 - (reduccion / 100)))

            update_health(str(interact.user.id), -enemy_d)
            msg += f"\n💥 El enemigo contraataca y te hace **{enemy_d}** de daño."

            if self.e_data.get("efecto") and random.random() < self.e_data.get(
                "efecto_probabilidad", 0
            ):
                from utils.users import add_effect  # <-- Asegúrate de importarlo

                add_effect(str(interact.user.id), self.e_data["efecto"])
                msg += f"\n🧪 ¡Te infectó con **{self.e_data['efecto']}**!"

        await self.update_combat(interact, msg)

    @discord.ui.button(label="Curarse", emoji="🩹", style=discord.ButtonStyle.success)
    async def btn_curar(self, interact: discord.Interaction, btn: discord.ui.Button):
        if interact.user.id != self.original_interact.user.id:
            return

        msg = "❌ No tienes objetos curativos rápidos.\n"
        for i in get_inventory(str(interact.user.id)):
            if i["item"] in ["Venda", "Botiquín", "Comida enlatada"]:
                exito, _ = use_item(str(interact.user.id), i["item"])
                if exito:
                    msg = f"🩹 Usaste {i['item']} rápido.\n"
                    break

        enemy_d = random.randint(*self.e_data["daño"])
        _, clima_data, es_dia = get_current_weather()
        multiplicador = (
            1.0 + (clima_data["peligro"] / 100) + (0.15 if not es_dia else 0)
        )
        enemy_d = round(enemy_d * multiplicador)

        # --- APLICAMOS REDUCCIÓN DE ARMADURA ---
        _, armadura_eq = get_equipped_gear(str(interact.user.id))
        if armadura_eq:
            from config.equipment import EQUIPMENT

            if armadura_eq in EQUIPMENT:
                reduccion = EQUIPMENT[armadura_eq]["reduccion_dano"]
                enemy_d = round(enemy_d * (1 - (reduccion / 100)))

        update_health(str(interact.user.id), -enemy_d)
        msg += f"\n💥 El enemigo aprovecha y te hace **{enemy_d}** de daño."
        await self.update_combat(interact, msg)

    @discord.ui.button(label="Huir", emoji="🏃", style=discord.ButtonStyle.secondary)
    async def btn_huir(self, interact: discord.Interaction, btn: discord.ui.Button):
        if interact.user.id != self.original_interact.user.id:
            return
        if random.random() > 0.4:
            self.e_hp = 0
            for b in self.children:
                b.disabled = True
            await interact.response.edit_message(
                embed=discord.Embed(
                    title="🏃 Huiste con éxito.",
                    color=discord.Color.light_grey(),
                ),
                view=self,
            )
        else:
            enemy_d = random.randint(*self.e_data["daño"])
            _, clima_data, es_dia = get_current_weather()
            multiplicador = (
                1.0 + (clima_data["peligro"] / 100) + (0.15 if not es_dia else 0)
            )
            enemy_d = round(enemy_d * multiplicador)

            # --- APLICAMOS REDUCCIÓN DE ARMADURA ---
            _, armadura_eq = get_equipped_gear(str(interact.user.id))
            if armadura_eq:
                from config.equipment import EQUIPMENT

                if armadura_eq in EQUIPMENT:
                    reduccion = EQUIPMENT[armadura_eq]["reduccion_dano"]
                    enemy_d = round(enemy_d * (1 - (reduccion / 100)))

            update_health(str(interact.user.id), -enemy_d)
            await self.update_combat(
                interact,
                f"❌ Tropezaste al huir. Recibes **{enemy_d}** de daño.",
            )
