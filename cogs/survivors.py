from config.events import EVENTS
from config.locations import LOCATIONS
from config.npcs import NPCS, RUMORES
from config.shelter import SHELTER_LEVELS
from datetime import datetime, timedelta
import random

import discord
from discord.ext import commands
from config.quests import QUESTS
from config.items import ITEMS
from config.recipes import RECIPES
from config.shop import SHOP_ITEMS
from config.enemies import ENEMIES
from utils.users import (
    get_or_create_survivor,
    add_overos,
    get_effects,
    add_effect,
    remove_effect,
    update_last_explore,
    get_last_explore,
    increase_effect_progress,
    update_effects,
    update_health,
    get_inventory,
    add_item,
    use_item,
    has_survivor,
    apply_effect_damage,
    reduce_active_effects,
    get_active_effects,
    has_active_effect,
    remove_item,
    resolve_event_condition,
    craft_item,
    get_overos,
    buy_item,
    sell_item,
    get_or_create_shelter,
    rest_in_shelter,
    upgrade_shelter,
    get_active_quest,
    assign_random_quest,
    claim_quest_reward,
    abandon_quest,
    update_quest_progress,
    get_current_weather,
    update_stat,
    get_unlocked_achievements,
    add_xp,
    get_equipped_gear,
    equip_item,
)


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

        # Obtenemos el inventario del jugador para las puertas bloqueadas
        survivor = get_or_create_survivor(self.user_id, "Jugador")
        inventario = survivor.get("inventory", {})

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
                # Revisa si el jugador tiene el ítem en la cantidad necesaria (al menos 1)
                for item_db in inventario:
                    if item_db["item"] == req_item and item_db["cantidad"] > 0:
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
            if "loot" in nodo_data:
                item_info = nodo_data["loot"]
                add_item(self.user_id, item_info["item"], item_info["cantidad"])
                msg_extra += f"\n📦 Encontraste: **{item_info['item']} (x{item_info['cantidad']})**"

            if "overos" in nodo_data and nodo_data["overos"][1] > 0:
                min_o, max_o = nodo_data["overos"]
                cant_o = random.randint(min_o, max_o)
                if cant_o > 0:
                    add_overos(self.user_id, cant_o)
                    msg_extra += f"\n🦴 Encontraste: **{cant_o} Overos**"

            if "damage" in nodo_data:
                msg_extra += (
                    f"\n⚠️ Recibiste **{nodo_data['damage']} de daño** por el entorno."
                )
                # Aquí podrías llamar a tu función real de daño a futuro

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
        await interaction.response.send_message(
            "⚔️ ¡Derrotaste al enemigo de la zona!", ephemeral=True
        )
        self.nodo_actual = "inicio"
        self.actualizar_botones()

        # Volvemos a generar el embed del inicio para que el mensaje no se quede vacío
        from config.incursions import INCURSIONS

        data_zona = INCURSIONS.get(self.lugar)
        nodo_inicio = data_zona["nodos"]["inicio"]
        embed = discord.Embed(
            title=data_zona["titulo"],
            description=nodo_inicio["descripcion"],
            color=data_zona["color"],
        )
        embed.add_field(
            name="Combate superado",
            value="Lograste abrirte paso y vuelves a una zona segura.",
        )
        await interaction.message.edit(embed=embed, view=self)

    async def callback_combat_huir(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "🏃 Lograste huir despavorido de regreso al inicio.", ephemeral=True
        )
        self.nodo_actual = "inicio"
        self.actualizar_botones()

        from config.incursions import INCURSIONS

        data_zona = INCURSIONS.get(self.lugar)
        nodo_inicio = data_zona["nodos"]["inicio"]
        embed = discord.Embed(
            title=data_zona["titulo"],
            description=nodo_inicio["descripcion"],
            color=data_zona["color"],
        )
        embed.add_field(
            name="Huida táctica", value="Escapaste por poco. Al menos sigues con vida."
        )
        await interaction.message.edit(embed=embed, view=self)


class TransaccionModal(discord.ui.Modal):
    def __init__(self, objeto, tipo):
        # tipo: "comprar" o "vender"
        super().__init__(title=f"Cantidad a {tipo}")
        self.objeto = objeto
        self.tipo = tipo
        self.cantidad = discord.ui.TextInput(
            label="Cantidad", placeholder="Ejemplo: 3", required=True
        )
        self.add_item(self.cantidad)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            cantidad = int(self.cantidad.value)
        except ValueError:
            await interaction.response.send_message(
                "❌ La cantidad debe ser un número.", ephemeral=True
            )
            return

        if self.tipo == "comprar":
            exito, mensaje = buy_item(str(interaction.user.id), self.objeto, cantidad)
        else:
            exito, mensaje = sell_item(str(interaction.user.id), self.objeto, cantidad)

        await interaction.response.send_message(mensaje)


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

    # Comando inventario
    @discord.app_commands.command(
        name="inventario", description="Muestra los objetos que tienes."
    )
    async def inventario(self, interaction: discord.Interaction):
        items = get_inventory(str(interaction.user.id))

        if not items:
            await interaction.response.send_message("🎒 Inventario vacío.")
            return

        paginas = []
        objetos_por_pagina = 5

        for i in range(0, len(items), objetos_por_pagina):
            pagina = items[i : i + objetos_por_pagina]
            embed = discord.Embed(
                title="🎒 Inventario del superviviente",
                description=f"Página {len(paginas) + 1}",
                color=discord.Color.dark_green(),
            )

            for item in pagina:
                data = ITEMS.get(item["item"])
                if data:
                    embed.add_field(
                        name=(
                            f"{data.get('emoji', '📦')} "
                            f"{item['item']} x{item['quantity']}"
                        ),
                        value=data["descripcion"],
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=f"📦 {item['item']} x{item['quantity']}",
                        value="Objeto desconocido.",
                        inline=False,
                    )
            paginas.append(embed)

        pagina_actual = 0

        class InventarioView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)

            @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
            async def anterior(
                self, button_interaction: discord.Interaction, button: discord.ui.Button
            ):
                nonlocal pagina_actual
                if pagina_actual > 0:
                    pagina_actual -= 1
                    await button_interaction.response.edit_message(
                        embed=paginas[pagina_actual], view=self
                    )
                else:
                    await button_interaction.response.defer()

            @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
            async def siguiente(
                self, button_interaction: discord.Interaction, button: discord.ui.Button
            ):
                nonlocal pagina_actual
                if pagina_actual < len(paginas) - 1:
                    pagina_actual += 1
                    await button_interaction.response.edit_message(
                        embed=paginas[pagina_actual], view=self
                    )
                else:
                    await button_interaction.response.defer()

        view = InventarioView()
        if len(paginas) == 1:
            view.clear_items()

        await interaction.response.send_message(embed=paginas[0], view=view)

    # ==========================================
    # COMANDO DE EQUIPAMIENTO
    # ==========================================
    @discord.app_commands.command(
        name="equipar",
        description="Equípate armas, armaduras o desequípate para ir sin nada.",
    )
    async def equipar(self, interaction: discord.Interaction):
        if not has_survivor(str(interaction.user.id)):
            return await interaction.response.send_message(
                "❌ Primero debes crear tu perfil con **/perfil**."
            )

        items = get_inventory(str(interaction.user.id))
        from config.equipment import EQUIPMENT

        equips_disponibles = [i for i in items if i["item"] in EQUIPMENT]
        arma_eq, armadura_eq = get_equipped_gear(str(interaction.user.id))

        opciones = []

        # Agregamos opciones fijas para desequipar si tiene algo puesto
        if arma_eq:
            opciones.append(
                discord.SelectOption(
                    label="Desequipar Arma",
                    description="Guarda tu arma actual",
                    emoji="❌",
                    value="desequipar_arma",
                )
            )
        if armadura_eq:
            opciones.append(
                discord.SelectOption(
                    label="Desequipar Armadura",
                    description="Quítate tu protección actual",
                    emoji="❌",
                    value="desequipar_armadura",
                )
            )

        # Agregamos los objetos del inventario que se pueden equipar
        for i in equips_disponibles:
            opciones.append(
                discord.SelectOption(
                    label=i["item"],
                    description=EQUIPMENT[i["item"]]["descripcion"][:100],
                    emoji=EQUIPMENT[i["item"]]["emoji"],
                    value=i["item"],
                )
            )

        if not opciones:
            embed_vacio = discord.Embed(
                title="🛡️ Zona de Equipamiento",
                description=f"**Equipamiento Actual:**\n🗡️ Arma: {arma_eq or 'Ninguna'}\n🛡️ Armadura: {armadura_eq or 'Ninguna'}\n\n❌ *No tienes armas ni armaduras para equiparte, y no llevas nada puesto para desequipar.*",
                color=discord.Color.dark_grey(),
            )
            return await interaction.response.send_message(
                embed=embed_vacio, ephemeral=True
            )

        select = discord.ui.Select(
            placeholder="Selecciona qué deseas hacer con tu equipo...", options=opciones
        )

        async def callback(i_select: discord.Interaction):
            objeto = select.values[0]
            exito, mensaje = equip_item(str(i_select.user.id), objeto)
            await i_select.response.send_message(mensaje, ephemeral=True)

        select.callback = callback
        view = discord.ui.View().add_item(select)

        embed = discord.Embed(
            title="🛡️ Gestión de Equipamiento",
            description=f"**Tu Equipo Actual:**\n🗡️ Arma: {arma_eq or 'Ninguna'}\n🛡️ Armadura: {armadura_eq or 'Ninguna'}\n\n*Selecciona del menú desplegable:*",
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # Comando usar
    @discord.app_commands.command(
        name="usar", description="Usa un objeto de tu inventario."
    )
    async def usar(self, interaction: discord.Interaction):
        items = get_inventory(str(interaction.user.id))
        if not items:
            await interaction.response.send_message("🎒 Inventario vacío.")
            return

        usable_items = []
        for item in items:
            data = ITEMS.get(item["item"])
            if data and data["usable"]:
                usable_items.append(item)

        if not usable_items:
            await interaction.response.send_message(
                "❌ No tienes objetos que puedas usar."
            )
            return

        opciones = []
        for item in usable_items:
            data = ITEMS[item["item"]]
            opciones.append(
                discord.SelectOption(
                    label=item["item"],
                    description=data["descripcion"][:100],
                    emoji=data.get("emoji", "📦"),
                    value=item["item"],
                )
            )

        select = discord.ui.Select(
            placeholder="Selecciona un objeto...", options=opciones
        )

        async def callback(interaction_select: discord.Interaction):
            objeto = select.values[0]
            exito, mensaje = use_item(str(interaction_select.user.id), objeto)
            await interaction_select.response.send_message(mensaje)

        select.callback = callback
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(
            "🎒 Selecciona un objeto para usar:", view=view
        )

    # Comando crear
    @discord.app_commands.command(
        name="crear",
        description="Combina objetos de tu inventario para crear algo nuevo.",
    )
    async def crear(self, interaction: discord.Interaction):
        if not has_survivor(str(interaction.user.id)):
            await interaction.response.send_message(
                "❌ Primero debes crear tu perfil con **/perfil**."
            )
            return

        opciones = []
        for resultado, receta in RECIPES.items():
            data = ITEMS.get(resultado)
            ingredientes_texto = ", ".join(
                f"{cantidad}x {ingrediente}"
                for ingrediente, cantidad in receta["ingredientes"].items()
            )
            opciones.append(
                discord.SelectOption(
                    label=resultado,
                    description=ingredientes_texto[:100],
                    emoji=data.get("emoji") if data else "🛠️",
                    value=resultado,
                )
            )

        select = discord.ui.Select(
            placeholder="Selecciona qué quieres crear...", options=opciones
        )

        async def callback(interaction_select: discord.Interaction):
            resultado = select.values[0]
            exito, mensaje = craft_item(str(interaction_select.user.id), resultado)
            await interaction_select.response.send_message(mensaje)

        select.callback = callback
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(
            "🛠️ Selecciona qué quieres crear:", view=view
        )

    # Comando tienda
    @discord.app_commands.command(
        name="tienda", description="Muestra los objetos disponibles para comprar."
    )
    async def tienda(self, interaction: discord.Interaction):
        paginas = []
        objetos_por_pagina = 5

        for i in range(0, len(SHOP_ITEMS), objetos_por_pagina):
            grupo = SHOP_ITEMS[i : i + objetos_por_pagina]
            embed = discord.Embed(
                title="🛒 Tienda del superviviente",
                description=f"Página {len(paginas) + 1}",
                color=discord.Color.gold(),
            )

            for nombre in grupo:
                data = ITEMS.get(nombre)
                if data is None:
                    continue
                embed.add_field(
                    name=f"{data.get('emoji', '📦')} {nombre} — {data['valor']} Overos",
                    value=data["descripcion"],
                    inline=False,
                )
            paginas.append(embed)

        await interaction.response.send_message(embed=paginas[0])

    # Comando comprar
    @discord.app_commands.command(
        name="comprar", description="Compra objetos de la tienda con tus Overos."
    )
    async def comprar(self, interaction: discord.Interaction):
        if not has_survivor(str(interaction.user.id)):
            await interaction.response.send_message(
                "❌ Primero debes crear tu perfil con **/perfil**."
            )
            return

        opciones = []
        for nombre in SHOP_ITEMS:
            data = ITEMS.get(nombre)
            if data is None:
                continue
            opciones.append(
                discord.SelectOption(
                    label=nombre,
                    description=f"{data['valor']} Overos — {data['descripcion'][:80]}",
                    emoji=data.get("emoji", "📦"),
                    value=nombre,
                )
            )

        select = discord.ui.Select(
            placeholder="Selecciona qué quieres comprar...", options=opciones
        )

        async def callback(interaction_select: discord.Interaction):
            objeto = select.values[0]
            await interaction_select.response.send_modal(
                TransaccionModal(objeto, "comprar")
            )

        select.callback = callback
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(
            f"🛒 Tienes **{get_overos(str(interaction.user.id))} Overos**. "
            "Selecciona qué quieres comprar:",
            view=view,
        )

    # Comando vender
    @discord.app_commands.command(
        name="vender", description="Vende objetos de tu inventario a cambio de Overos."
    )
    async def vender(self, interaction: discord.Interaction):
        items = get_inventory(str(interaction.user.id))
        if not items:
            await interaction.response.send_message("🎒 Inventario vacío.")
            return

        opciones = []
        for item in items:
            data = ITEMS.get(item["item"])
            if data is None or data.get("categoria") == "Especial":
                continue

            precio_venta = round(data["valor"] * 0.5)
            opciones.append(
                discord.SelectOption(
                    label=f"{item['item']} (x{item['quantity']})",
                    description=f"Vender por {precio_venta} Overos c/u",
                    emoji=data.get("emoji", "📦"),
                    value=item["item"],
                )
            )

        if not opciones:
            await interaction.response.send_message(
                "❌ No tienes objetos que puedas vender."
            )
            return

        select = discord.ui.Select(
            placeholder="Selecciona qué quieres vender...", options=opciones
        )

        async def callback(interaction_select: discord.Interaction):
            objeto = select.values[0]
            await interaction_select.response.send_modal(
                TransaccionModal(objeto, "vender")
            )

        select.callback = callback
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(
            "🎒 Selecciona qué quieres vender:", view=view
        )

    # Comando explorar (CON LOGROS FASE 11)
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

        lugar_nombre = None
        if lugar:
            lugar_nombre = lugar.value if hasattr(lugar, "value") else str(lugar)

        # Separamos limpiamente los tipos de eventos
        eventos_especificos = [
            e for e in EVENTS if e.get("lugares") and lugar_nombre in e["lugares"]
        ]
        eventos_globales = [e for e in EVENTS if not e.get("lugares")]

        # Determinamos qué grupo usar para la exploración
        if lugar_nombre and eventos_especificos:
            # 75% de probabilidad de evento temático de la zona, 25% de evento global genérico
            if random.random() <= 0.75:
                eventos_disponibles = eventos_especificos
            else:
                eventos_disponibles = eventos_globales
        else:
            # Si no eligió lugar o el lugar no tiene eventos configurados, usamos globales
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

        # --- NUEVO SISTEMA DE MÚLTIPLES OBJETOS ---
        items_encontrados = []

        # 1. Compatibilidad con eventos antiguos (un solo objeto)
        if evento.get("item") is not None:
            add_item(str(interaction.user.id), evento["item"], 1)
            items_encontrados.append(f"**{evento['item']} (x1)**")

        # 2. Nuevo sistema (lista de objetos con probabilidad)
        if "items" in evento:
            for loot in evento["items"]:
                # Comprobar si el jugador tiene la suerte de encontrar este objeto
                if random.random() <= (loot["chance"] / 100.0):
                    # Generar una cantidad aleatoria
                    cantidad = random.randint(loot["cantidad"][0], loot["cantidad"][1])
                    if cantidad > 0:
                        add_item(str(interaction.user.id), loot["item"], cantidad)
                        items_encontrados.append(f"**{loot['item']} (x{cantidad})**")

        # Si encontró al menos un objeto, agregarlo al mensaje
        if items_encontrados:
            mensaje += f"\n\n🎒 Has encontrado: {', '.join(items_encontrados)}."

        if item_consumido is not None:
            remove_item(str(interaction.user.id), item_consumido, 1)
            mensaje += f"\n\n🔧 Has usado: **{item_consumido}**."

        update_last_explore(str(interaction.user.id))

        if lugar_nombre:
            update_quest_progress(str(interaction.user.id), "exploracion", lugar_nombre)

        # --- LOGROS: Actualizamos estadística de exploraciones ---
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
        # --- FASE 12: Ganancia de XP por explorar ---
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

        # Por ahora tenemos configurado el Hospital con nodos narrativos
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
    # SISTEMA DE COMBATE PVE (FASE 8 + 9 + 10 + EQUIPO)
    # ==========================================
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

        class CombatView(discord.ui.View):
            def __init__(self, original_interact, e_name, e_data):
                super().__init__(timeout=120)
                self.original_interact = original_interact
                self.e_name = e_name
                self.e_hp, self.e_max_hp = e_data["hp"], e_data["hp"]
                self.e_data = e_data

            async def update_combat(self, interact: discord.Interaction, msg: str):
                s = get_or_create_survivor(
                    str(interact.user.id), interact.user.display_name
                )
                embed = discord.Embed(
                    title=f"⚔️ {self.e_data['emoji']} {self.e_name}",
                    description=msg,
                    color=self.e_data["color"],
                )
                embed.add_field(
                    name="Tu Vida", value=f"❤️ {s['health']}/100", inline=True
                )
                embed.add_field(
                    name="Vida Enemigo",
                    value=f"🩸 {self.e_hp}/{self.e_max_hp}",
                    inline=True,
                )
                if self.e_hp <= 0 or s["health"] <= 0:
                    for btn in self.children:
                        btn.disabled = True
                await interact.response.edit_message(embed=embed, view=self)

            @discord.ui.button(
                label="Atacar", emoji="🗡️", style=discord.ButtonStyle.danger
            )
            async def btn_atacar(
                self, interact: discord.Interaction, btn: discord.ui.Button
            ):
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
                                    add_item(
                                        str(interact.user.id), loot["item"], cantidad
                                    )
                                    items_dropeados.append(
                                        f"**{loot['item']} (x{cantidad})**"
                                    )

                    if items_dropeados:
                        msg += f"\n📦 Dejó caer: {', '.join(items_dropeados)}."

                    update_quest_progress(str(interact.user.id), "caceria", self.e_name)

                    # --- LOGROS: Actualizamos estadística de enemigos derrotados ---
                    nuevos_logros = update_stat(
                        str(interact.user.id), "enemies_defeated"
                    )
                    for logro in nuevos_logros:
                        msg += (
                            f"\n\n🏆 **¡LOGRO DESBLOQUEADO!** {logro['emoji']} **{logro['nombre']}**\n*{logro['descripcion']}*\n🎁 Recompensa: 🦴 {logro['recompensa_overos']} Overos"
                            + (
                                f" y 📦 {logro['recompensa_item']}"
                                if logro["recompensa_item"]
                                else ""
                            )
                        )

                else:
                    enemy_d = random.randint(*self.e_data["daño"])
                    _, clima_data, es_dia = get_current_weather()
                    multiplicador = (
                        1.0
                        + (clima_data["peligro"] / 100)
                        + (0.15 if not es_dia else 0)
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
                    msg += (
                        f"\n💥 El enemigo contraataca y te hace **{enemy_d}** de daño."
                    )
                    if self.e_data.get("efecto") and random.random() < self.e_data.get(
                        "efecto_probabilidad", 0
                    ):
                        add_effect(str(interact.user.id), self.e_data["efecto"])
                        msg += f"\n🧪 ¡Te infectó con **{self.e_data['efecto']}**!"
                await self.update_combat(interact, msg)

            @discord.ui.button(
                label="Curarse", emoji="🩹", style=discord.ButtonStyle.success
            )
            async def btn_curar(
                self, interact: discord.Interaction, btn: discord.ui.Button
            ):
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

            @discord.ui.button(
                label="Huir", emoji="🏃", style=discord.ButtonStyle.secondary
            )
            async def btn_huir(
                self, interact: discord.Interaction, btn: discord.ui.Button
            ):
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
                        1.0
                        + (clima_data["peligro"] / 100)
                        + (0.15 if not es_dia else 0)
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
