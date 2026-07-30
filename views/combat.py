import random

import discord
from discord import ui
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
    transfer_item,
    get_connection,
    get_baul,
)


# --- MODAL PARA PEDIR OBJETOS EN EL SISTEMA DE BAÚL ---
class CantidadTransferirModal(ui.Modal):
    def __init__(self, item_name: str, max_qty: int, to_baul: bool, view_padre):
        titulo = f"Guardar {item_name}" if to_baul else f"Sacar {item_name}"
        super().__init__(
            title=titulo[:45]
        )  # Límite de 45 caracteres en títulos de Discord

        self.item_name = item_name
        self.max_qty = max_qty
        self.to_baul = to_baul
        self.view_padre = view_padre

        self.cantidad_input = ui.TextInput(
            label=f"Cantidad (Disponible: {max_qty})",
            placeholder="Ej: 1",
            default="1",
            min_length=1,
            max_length=5,
            required=True,
        )
        self.add_item(self.cantidad_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            cantidad = int(self.cantidad_input.value)
            if cantidad <= 0:
                await interaction.response.send_message(
                    "❌ La cantidad debe ser mayor a 0.", ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                "❌ Ingresa un número válido.", ephemeral=True
            )
            return

        # Ejecutamos la transferencia
        exito, msg = transfer_item(
            str(interaction.user.id), self.item_name, cantidad, to_baul=self.to_baul
        )

        # Actualizamos el Embed del baúl en la pantalla del usuario
        embed_actualizado = await self.view_padre.generar_embed(interaction.user.id)
        self.view_padre.actualizar_selects(interaction.user.id)

        await interaction.response.edit_message(
            embed=embed_actualizado, view=self.view_padre
        )
        await interaction.followup.send(msg, ephemeral=True)


class CombatView(discord.ui.View):
    def __init__(self, original_interact, e_name, e_data):
        super().__init__(timeout=120)
        self.original_interact = original_interact
        self.e_name = e_name
        self.e_hp, self.e_max_hp = e_data["hp"], e_data["hp"]
        self.e_data = e_data


# --- 2. MENÚ DESPLEGABLE DE SELECCIÓN DE OBJETOS ---
class ItemTransferSelect(ui.Select):
    def __init__(self, placeholder: str, items: list, to_baul: bool, view_padre):
        self.to_baul = to_baul
        self.view_padre = view_padre

        options = []
        is_disabled = False

        if not items:
            # Si no hay items, ponemos una opción de relleno básica
            options.append(
                discord.SelectOption(
                    label="Vacío",
                    description="No hay objetos para mover.",
                    value="none",
                )
            )
            # Marcamos que el menú entero debe estar deshabilitado
            is_disabled = True
        else:
            for item in items[:25]:  # Discord permite máximo 25 opciones por Select
                nombre = item["item"]
                cant = item["quantity"]
                options.append(
                    discord.SelectOption(
                        label=f"{nombre} (x{cant})",
                        value=f"{nombre}|{cant}",
                        description=f"Mover {nombre} al {'baúl' if to_baul else 'inventario'}",
                    )
                )

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options,
            disabled=is_disabled,  # <--- Deshabilitamos el Select entero aquí
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.defer()
            return

        item_name, cant_str = self.values[0].split("|")
        max_qty = int(cant_str)

        # Abrimos el Modal para pedir la cantidad
        from utils.users import (
            transfer_item,
        )  # Ajusta este import si es necesario según tu estructura

        modal = CantidadTransferirModal(
            item_name, max_qty, self.to_baul, self.view_padre
        )
        await interaction.response.send_modal(modal)


# --- 3. VISTA PRINCIPAL DEL BAÚL ---
class BaulView(ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.actualizar_selects(user_id)

    def obtener_inventario_activo(self, discord_id: str):
        """Función auxiliar para obtener los items de la mochila activa del jugador."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))
        survivor = cursor.fetchone()
        if not survivor:
            connection.close()
            return []

        cursor.execute(
            "SELECT item, quantity FROM inventory WHERE survivor_id = ?",
            (survivor["id"],),
        )
        items = cursor.fetchall()
        connection.close()
        return items

    def actualizar_selects(self, user_id: int):
        self.clear_items()

        mochila = self.obtener_inventario_activo(str(user_id))
        baul = get_baul(str(user_id))

        # Select para guardar de Mochila -> Baúl
        select_guardar = ItemTransferSelect(
            placeholder="📥 Selecciona un objeto para GUARDAR en el baúl...",
            items=mochila,
            to_baul=True,
            view_padre=self,
        )
        self.add_item(select_guardar)

        # Select para sacar de Baúl -> Mochila
        select_sacar = ItemTransferSelect(
            placeholder="📤 Selecciona un objeto para SACAR del baúl...",
            items=baul,
            to_baul=False,
            view_padre=self,
        )
        self.add_item(select_sacar)

    async def generar_embed(self, user_id: int) -> discord.Embed:
        mochila = self.obtener_inventario_activo(str(user_id))
        baul = get_baul(str(user_id))

        embed = discord.Embed(
            title="🧰 Almacenamiento del Refugio",
            description="Usa los menús desplegables abajo para guardar o sacar objetos de forma segura.",
            color=discord.Color.gold(),
        )

        # Sección Mochila
        txt_mochila = ""
        if not mochila:
            txt_mochila = "*Tu mochila está vacía.*"
        else:
            for obj in mochila:
                txt_mochila += f"• **{obj['item']}** (x{obj['quantity']})\n"
        embed.add_field(
            name=f"🎒 Mochila Activa ({len(mochila)}/15 slots)",
            value=txt_mochila,
            inline=True,
        )

        # Sección Baúl
        txt_baul = ""
        if not baul:
            txt_baul = "*El baúl está vacío.*"
        else:
            for obj in baul:
                txt_baul += f"• **{obj['item']}** (x{obj['quantity']})\n"
        embed.add_field(
            name=f"📦 Baúl Seguro ({len(baul)} objetos)", value=txt_baul, inline=True
        )

        embed.set_footer(
            text="El baúl es seguro e ilimitado. Los objetos guardados aquí no se pierden al morir."
        )
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Esta interfaz pertenece a otro superviviente.", ephemeral=True
            )
            return False
        return True

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
