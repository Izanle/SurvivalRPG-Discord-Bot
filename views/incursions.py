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
)


class IncursionCombatView(discord.ui.View):
    def __init__(
        self, original_interact, incursion_view, e_name, e_data, nodo_exito, nodo_huida
    ):
        super().__init__(timeout=120)
        self.original_interact = original_interact
        self.incursion_view = incursion_view
        self.e_name = e_name
        self.e_data = e_data
        self.e_hp = e_data["hp"]
        self.e_max_hp = e_data["hp"]
        self.nodo_exito = nodo_exito
        self.nodo_huida = nodo_huida

    async def update_combat(self, interact: discord.Interaction, msg: str):
        s = get_or_create_survivor(str(interact.user.id), "Jugador")
        embed = discord.Embed(
            title=f"⚔️ {self.e_data['emoji']} {self.e_name}",
            description=msg,
            color=self.e_data["color"],
        )
        embed.add_field(name="Tu Vida", value=f"❤️ {s['health']}/100", inline=True)
        embed.add_field(
            name="Vida Enemigo", value=f"🩸 {self.e_hp}/{self.e_max_hp}", inline=True
        )

        if self.e_hp <= 0 or s["health"] <= 0:
            self.clear_items()
            if self.e_hp <= 0 and s["health"] > 0:
                btn_continuar = discord.ui.Button(
                    label="Continuar incursión",
                    style=discord.ButtonStyle.success,
                    emoji="➡️",
                )
                btn_continuar.callback = self.btn_continuar_callback
                self.add_item(btn_continuar)
            elif s["health"] <= 0:
                embed.color = discord.Color.dark_red()

        await interact.response.edit_message(embed=embed, view=self)

    async def btn_continuar_callback(self, interact: discord.Interaction):
        if interact.user.id != self.original_interact.user.id:
            return

        # Volvemos a la incursion en el nodo correspondiente
        self.incursion_view.nodo_actual = self.nodo_exito
        self.incursion_view.actualizar_botones()

        from config.incursions import INCURSIONS

        data_zona = INCURSIONS.get(self.incursion_view.lugar)
        nodo_data = data_zona["nodos"].get(self.nodo_exito)
        embed = discord.Embed(
            title=data_zona["titulo"],
            description=nodo_data["descripcion"],
            color=data_zona["color"],
        )
        await interact.response.edit_message(embed=embed, view=self.incursion_view)

    @discord.ui.button(label="Atacar", emoji="🗡️", style=discord.ButtonStyle.danger)
    async def btn_atacar(self, interact: discord.Interaction, btn: discord.ui.Button):
        if interact.user.id != self.original_interact.user.id:
            return

        player_dmg = random.randint(15, 25)
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
            add_xp(str(interact.user.id), 50)
            update_quest_progress(str(interact.user.id), "caceria", self.e_name)
            msg += f"\n💀 **¡Has derrotado a {self.e_name}!**"
            loot_o = random.randint(*self.e_data["loot_overos"])
            add_overos(str(interact.user.id), loot_o)
            msg += f"\n🦴 Obtuviste **{loot_o} Overos**."

            if "items" in self.e_data:
                items_dropeados = []
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

            # Logros
            nuevos_logros = update_stat(str(interact.user.id), "enemies_defeated")
            for logro in nuevos_logros:
                msg += f"\n\n🏆 **¡LOGRO DESBLOQUEADO!** {logro['emoji']} **{logro['nombre']}**\n🎁 Recompensa: 🦴 {logro['recompensa_overos']} Overos"
        else:
            enemy_d = random.randint(*self.e_data["daño"])
            _, armadura_eq = get_equipped_gear(str(interact.user.id))
            if armadura_eq:
                from config.equipment import EQUIPMENT

                if armadura_eq in EQUIPMENT:
                    reduccion = EQUIPMENT[armadura_eq]["reduccion_dano"]
                    enemy_d = round(enemy_d * (1 - (reduccion / 100)))

            update_health(str(interact.user.id), -enemy_d)
            msg += f"\n💥 El enemigo contraataca y te hace **{enemy_d}** de daño."

            s = get_or_create_survivor(str(interact.user.id), "Jugador")
            if s["health"] <= 0:
                msg += "\n\n💀 **Tus heridas fueron demasiado graves. HAS MUERTO.**"

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
        _, armadura_eq = get_equipped_gear(str(interact.user.id))
        if armadura_eq:
            from config.equipment import EQUIPMENT

            if armadura_eq in EQUIPMENT:
                reduccion = EQUIPMENT[armadura_eq]["reduccion_dano"]
                enemy_d = round(enemy_d * (1 - (reduccion / 100)))

        update_health(str(interact.user.id), -enemy_d)
        msg += f"\n💥 El enemigo aprovecha y te hace **{enemy_d}** de daño."

        s = get_or_create_survivor(str(interact.user.id), "Jugador")
        if s["health"] <= 0:
            msg += "\n\n💀 **Tus heridas fueron demasiado graves. HAS MUERTO.**"
            self.clear_items()
        await self.update_combat(interact, msg)

    @discord.ui.button(label="Huir", emoji="🏃", style=discord.ButtonStyle.secondary)
    async def btn_huir(self, interact: discord.Interaction, btn: discord.ui.Button):
        if interact.user.id != self.original_interact.user.id:
            return

        if random.random() > 0.4:
            self.incursion_view.nodo_actual = self.nodo_huida
            self.incursion_view.actualizar_botones()
            from config.incursions import INCURSIONS

            data_zona = INCURSIONS.get(self.incursion_view.lugar)
            nodo_data = data_zona["nodos"].get(self.nodo_huida)
            embed = discord.Embed(
                title=data_zona["titulo"],
                description="🏃 Escapaste por poco...\n\n" + nodo_data["descripcion"],
                color=data_zona["color"],
            )
            await interact.response.edit_message(embed=embed, view=self.incursion_view)
        else:
            enemy_d = random.randint(*self.e_data["daño"])
            _, armadura_eq = get_equipped_gear(str(interact.user.id))
            if armadura_eq:
                from config.equipment import EQUIPMENT

                if armadura_eq in EQUIPMENT:
                    reduccion = EQUIPMENT[armadura_eq]["reduccion_dano"]
                    enemy_d = round(enemy_d * (1 - (reduccion / 100)))
            update_health(str(interact.user.id), -enemy_d)
            s = get_or_create_survivor(str(interact.user.id), "Jugador")
            msg = f"❌ Tropezaste al huir. Recibes **{enemy_d}** de daño."
            if s["health"] <= 0:
                msg += "\n\n💀 **HAS MUERTO al intentar escapar.**"
                self.clear_items()
            await self.update_combat(interact, msg)


class IncursionView(discord.ui.View):
    def __init__(self, user_id: str, lugar: str):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.lugar = lugar
        self.nodo_actual = "inicio"
        self.opciones_usadas = set()  # ¡MECÁNICA 2! Guarda las opciones de 1 solo uso
        self.actualizar_botones()

    def actualizar_botones(self):
        self.clear_items()
        from config.incursions import INCURSIONS

        data_zona = INCURSIONS.get(self.lugar)
        if not data_zona:
            return
        nodo_data = data_zona["nodos"].get(self.nodo_actual)
        if not nodo_data or nodo_data.get("tipo") == "fin":
            return

        if nodo_data.get("tipo") == "combate":
            btn_atacar = discord.ui.Button(
                label="Atacar", style=discord.ButtonStyle.danger, emoji="⚔️"
            )
            btn_atacar.callback = self.callback_combat_atacar
            self.add_item(btn_atacar)

            btn_huir = discord.ui.Button(
                label="Huir", style=discord.ButtonStyle.secondary, emoji="🏃"
            )
            btn_huir.callback = self.callback_combat_huir
            self.add_item(btn_huir)
            return

        # Usamos tu función nativa get_inventory (ya importada arriba)
        inventario = get_inventory(self.user_id)

        for i, opcion in enumerate(nodo_data.get("opciones", [])):
            uid_opcion = (
                f"{self.nodo_actual}_{i}"  # ID único para este botón en esta habitación
            )

            # ¡MECÁNICA 2 (Un solo uso)! Si ya la usamos, saltamos este botón y no lo dibujamos
            if opcion.get("un_solo_uso") and uid_opcion in self.opciones_usadas:
                continue

            btn = discord.ui.Button(
                label=opcion["label"],
                style=discord.ButtonStyle.primary,
                emoji=opcion.get("emoji", "➡️"),
            )

            # ¡MECÁNICA 1 (Requisitos)! Verificamos si necesita un ítem
            req_item = opcion.get("requiere_item")
            if req_item:
                tiene_item = False
                # Revisa si el jugador tiene el ítem, buscando "quantity" como en tu base de datos
                if inventario:
                    for item_db in inventario:
                        if item_db["item"] == req_item and item_db["quantity"] > 0:
                            tiene_item = True
                            break

                if not tiene_item:
                    btn.style = discord.ButtonStyle.secondary
                    btn.disabled = True
                    btn.label = f"{opcion['label']} (Requiere: {req_item})"

            btn.callback = self.crear_callback_opcion(opcion, uid_opcion)
            self.add_item(btn)

    def crear_callback_opcion(self, opcion: dict, uid_opcion: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != int(self.user_id):
                return await interaction.response.send_message(
                    "❌ Esta no es tu incursión.", ephemeral=True
                )

            # Si era de un solo uso, lo registramos para que desaparezca al actualizar
            if opcion.get("un_solo_uso"):
                self.opciones_usadas.add(uid_opcion)

            # ¡MECÁNICA 3 (Azar)! Determinamos a qué nodo va
            siguiente = opcion.get("siguiente")
            if not siguiente and "siguiente_azar" in opcion:
                caminos = opcion["siguiente_azar"]
                nodos = [c["nodo"] for c in caminos]
                pesos = [c["probabilidad"] for c in caminos]
                siguiente = random.choices(nodos, weights=pesos, k=1)[0]

            self.nodo_actual = siguiente
            from config.incursions import INCURSIONS

            data_zona = INCURSIONS.get(self.lugar)
            nodo_data = data_zona["nodos"].get(self.nodo_actual)

            embed = discord.Embed(
                title=data_zona["titulo"],
                description=nodo_data["descripcion"],
                color=data_zona["color"],
            )

            msg_extra = ""
            items_a_dar = []
            if "items" in nodo_data:
                items_a_dar.extend(nodo_data["items"])
            elif "loot" in nodo_data:
                items_a_dar.append(nodo_data["loot"])

            if items_a_dar:
                encontrados = []
                for item_info in items_a_dar:
                    cant = item_info.get("cantidad", 1)
                    if cant > 0:
                        add_item(self.user_id, item_info["item"], cant)
                        encontrados.append(f"**{item_info['item']} (x{cant})**")
                if encontrados:
                    msg_extra += f"\n📦 Encontraste: {', '.join(encontrados)}"

            if "overos" in nodo_data and nodo_data["overos"][1] > 0:
                min_o, max_o = nodo_data["overos"]
                cant_o = random.randint(min_o, max_o)
                if cant_o > 0:
                    add_overos(self.user_id, cant_o)
                    msg_extra += f"\n🦴 Encontraste: **{cant_o} Overos**"

            if "damage" in nodo_data:
                from utils.users import update_health, get_or_create_survivor

                # 1. Aplicamos el daño real a la base de datos (en negativo para restar)
                dano = nodo_data["damage"]
                update_health(self.user_id, -dano)
                msg_extra += f"\n⚠️ Recibiste **{dano} de daño** por el entorno."

                # 2. Comprobamos si este daño acaba de matar al jugador
                survivor = get_or_create_survivor(self.user_id, "Jugador")
                if survivor["status"] == "Muerto":
                    embed.add_field(name="Resultados", value=msg_extra, inline=False)
                    embed.add_field(
                        name="💀 HAS MUERTO",
                        value="Tus heridas fueron demasiado graves y tu cuerpo no resistió. Has caído en el páramo.",
                        inline=False,
                    )
                    embed.color = (
                        discord.Color.dark_red()
                    )  # Cambiamos el color a rojo sangre
                    self.clear_items()  # Borramos todos los botones para que no pueda seguir jugando
                    await interaction.response.edit_message(embed=embed, view=self)
                    return

            if msg_extra:
                embed.add_field(name="Resultados", value=msg_extra, inline=False)

            if nodo_data.get("tipo") == "fin":
                self.clear_items()
                embed.add_field(
                    name="Fin de la Incursión",
                    value="Has salido de la zona de forma segura.",
                    inline=False,
                )
                await interaction.response.edit_message(embed=embed, view=self)
                return

            self.actualizar_botones()
            await interaction.response.edit_message(embed=embed, view=self)

        return callback

    async def callback_combat_atacar(self, interaction: discord.Interaction):
        from config.incursions import INCURSIONS
        from config.enemies import ENEMIES

        data_zona = INCURSIONS.get(self.lugar)
        nodo_data = data_zona["nodos"].get(self.nodo_actual)

        enemigo_nombre = nodo_data.get("enemigo", "Infectado")
        enemigo_data = dict(ENEMIES[enemigo_nombre])

        # Obtenemos los nodos a los que irá si gana o si logra escapar
        nodo_exito = nodo_data.get("siguiente_exito", "inicio")
        nodo_huida = nodo_data.get("siguiente_huida", "inicio")

        view_combate = IncursionCombatView(
            original_interact=interaction,
            incursion_view=self,
            e_name=enemigo_nombre,
            e_data=enemigo_data,
            nodo_exito=nodo_exito,
            nodo_huida=nodo_huida,
        )

        survivor = get_or_create_survivor(self.user_id, "Jugador")
        embed = discord.Embed(
            title=f"⚔️ {enemigo_data['emoji']} {enemigo_nombre}",
            description="¡Te has enzarzado en combate cuerpo a cuerpo por los pasillos!",
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

        # Cambiamos el mensaje para que muestre el combate real
        await interaction.response.edit_message(embed=embed, view=view_combate)

    async def callback_combat_huir(self, interaction: discord.Interaction):
        from config.incursions import INCURSIONS

        data_zona = INCURSIONS.get(self.lugar)
        nodo_data = data_zona["nodos"].get(self.nodo_actual)

        # Si decides ni siquiera intentar atacar, retrocedes de inmediato
        self.nodo_actual = nodo_data.get("siguiente_huida", "inicio")
        self.actualizar_botones()

        nodo_nuevo = data_zona["nodos"].get(self.nodo_actual)
        embed = discord.Embed(
            title=data_zona["titulo"],
            description="🏃 Decides no arriesgarte y retrocedes de inmediato.\n\n"
            + nodo_nuevo["descripcion"],
            color=data_zona["color"],
        )
        await interaction.response.edit_message(embed=embed, view=self)
