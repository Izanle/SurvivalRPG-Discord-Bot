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
from config.effects import SURVIVOR_EFFECTS
from config.recipes import RECIPES
from config.shop import SHOP_ITEMS
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
    reset_survivor,
    get_inventory,
    add_item,
    use_item,
    has_survivor,
    apply_effect_damage,
    clear_inventory,
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
)


class CantidadModal(discord.ui.Modal):
    def __init__(self, objeto):
        super().__init__(title="Cantidad de objeto")
        self.objeto = objeto
        self.cantidad = discord.ui.TextInput(
            label="Cantidad", placeholder="Ejemplo: 5", required=True
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

        add_item(str(interaction.user.id), self.objeto, cantidad)
        await interaction.response.send_message(
            f"✅ Agregado: {self.objeto} x{cantidad}", ephemeral=True
        )


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

    @discord.app_commands.command(
        name="efecto", description="Añade un efecto (solo para pruebas)."
    )
    @discord.app_commands.describe(efecto="Nombre del efecto.")
    async def efecto(self, interaction: discord.Interaction, efecto: str):
        if interaction.user.id != 1414035229286596719:
            await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando.", ephemeral=True
            )
            return

        add_effect(str(interaction.user.id), efecto)
        await interaction.response.send_message(f"🧪 Efecto agregado: **{efecto}**")

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

        if effects:
            effects_text = "\n".join(
                (
                    f"• {effect['effect']} "
                    f"({effect['progress']}/"
                    f"{SURVIVOR_EFFECTS[effect['effect']]['exploraciones']})"
                    if SURVIVOR_EFFECTS[effect["effect"]]["exploraciones"] is not None
                    else f"• {effect['effect']}"
                )
                for effect in effects
            )
        else:
            effects_text = "Ninguno"

        if active_effects:
            active_effects_text = "\n".join(
                f"• {effect['effect']} " f"({effect['duration']} exploraciones)"
                for effect in active_effects
            )
        else:
            active_effects_text = "Ninguno"

        await interaction.response.send_message(
            f"🕯️ Registro encontrado:\n\n"
            f"🔍 Nombre: {survivor['name']}\n"
            f"👁️ Estado: {survivor['status']}\n"
            f"❤️ Vida: {survivor['health']}/100\n"
            f"🦴 Overos: {survivor['overos']}\n\n"
            f"🧪 Estados:\n{effects_text}\n\n"
            f"✨ Efectos activos:\n{active_effects_text}\n\n"
            f"📜 Registrado: {fecha}"
        )

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

    @discord.app_commands.command(
        name="objeto", description="Agrega objetos al inventario (admin)."
    )
    async def objeto(self, interaction: discord.Interaction):
        OWNER_ID = "1414035229286596719"
        if str(interaction.user.id) != OWNER_ID:
            await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando."
            )
            return

        opciones = []
        for item, data in ITEMS.items():
            opciones.append(
                discord.SelectOption(
                    label=item,
                    description=data["descripcion"][:100],
                    emoji=data.get("emoji") if data.get("emoji") else "📦",
                    value=item,
                )
            )

        select = discord.ui.Select(
            placeholder="Selecciona un objeto...", options=opciones
        )

        async def callback(interaction_select: discord.Interaction):
            objeto_seleccionado = select.values[0]
            await interaction_select.response.send_modal(
                CantidadModal(objeto_seleccionado)
            )

        select.callback = callback
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(
            "📦 Selecciona el objeto que quieres agregar:", view=view
        )

    @discord.app_commands.command(
        name="limpiar_inventario", description="Limpia todo el inventario del jugador."
    )
    async def limpiar_inventario(self, interaction: discord.Interaction):
        OWNER_ID = "1414035229286596719"
        if str(interaction.user.id) != OWNER_ID:
            await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando."
            )
            return

        clear_inventory(str(interaction.user.id))
        await interaction.response.send_message("🧹 Inventario limpiado correctamente.")

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
                await interaction.response.send_message(
                    f"⏳ Aún no puedes explorar. Espera {minutos} minutos y {segundos} segundos."
                )
                return

        # VERSIÓN SEGURA: Extrae el nombre sin importar cómo lo envíe Discord
        lugar_nombre = None
        if lugar:
            lugar_nombre = lugar.value if hasattr(lugar, "value") else str(lugar)

        eventos_disponibles = []
        for evento_posible in EVENTS:
            lugares_evento = evento_posible.get("lugares")
            if not lugares_evento:
                eventos_disponibles.append(evento_posible)
            elif lugar_nombre and lugar_nombre in lugares_evento:
                eventos_disponibles.append(evento_posible)

        if not eventos_disponibles:
            eventos_disponibles = [
                evento_posible
                for evento_posible in EVENTS
                if not evento_posible.get("lugares")
            ]

        tiene_moral = has_active_effect(str(interaction.user.id), "moral")
        pesos = []
        for evento_posible in eventos_disponibles:
            peso = evento_posible["chance"]
            if tiene_moral:
                if evento_posible["damage"] > 0:
                    peso *= 0.8
                if evento_posible["item"] is not None:
                    peso *= 1.1
            pesos.append(peso)

        evento = random.choices(eventos_disponibles, weights=pesos, k=1)[0]
        evento, item_consumido = resolve_event_condition(
            str(interaction.user.id), evento
        )

        tiene_energia = has_active_effect(str(interaction.user.id), "energia")
        evitar_dano = False
        if tiene_energia and evento["damage"] > 0:
            if evento["damage"] <= 5:
                if random.random() <= 0.5:
                    evitar_dano = True

        reduce_active_effects(str(interaction.user.id))

        # --- CÁLCULO BASE DE OVEROS Y MORAL ---
        if isinstance(evento["overos"], tuple):
            cantidad_overos = random.randint(evento["overos"][0], evento["overos"][1])
        else:
            cantidad_overos = evento["overos"]

        moral_bonus = 0
        if tiene_moral and cantidad_overos > 0:
            moral_bonus = max(1, round(cantidad_overos * 0.1))
            cantidad_overos += moral_bonus

        # --- INTEGRACIÓN CLIMA Y HORA (FASE 10) ---
        clima_nombre, clima_data, es_dia = get_current_weather()

        peligro_extra = clima_data["peligro"]
        if not es_dia:
            peligro_extra += 15  # La noche castiga más

        # Daño final afectado por el clima
        dano_final = evento["damage"]
        if dano_final > 0:
            dano_final = round(dano_final * (1 + (peligro_extra / 100)))

        # Bono de botín por clima / noche
        bonus_loot_total = clima_data["loot_bonus"] + (10 if not es_dia else 0)
        if cantidad_overos > 0 and bonus_loot_total > 0:
            bonus_clima = max(1, round(cantidad_overos * (bonus_loot_total / 100)))
            cantidad_overos += bonus_clima

        # Sumamos todos los overos calculados al jugador de golpe
        if cantidad_overos > 0:
            add_overos(str(interaction.user.id), cantidad_overos)

        # --- CONSTRUCCIÓN DEL MENSAJE ---
        if lugar_nombre:
            emoji_lugar = LOCATIONS[lugar_nombre]["emoji"]
            mensaje = f"{emoji_lugar} **{lugar_nombre}**\n\n" + evento["mensaje"]
        else:
            mensaje = evento["mensaje"]

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

        if evento["item"] is not None:
            add_item(str(interaction.user.id), evento["item"])
            mensaje += f"\n\n🎒 Has encontrado: **{evento['item']}**."

        if item_consumido is not None:
            remove_item(str(interaction.user.id), item_consumido, 1)
            mensaje += f"\n\n🔧 Has usado: **{item_consumido}**."

        update_last_explore(str(interaction.user.id))

        # PROGRESO DE MISIÓN (FASE 9)
        if lugar_nombre:
            update_quest_progress(str(interaction.user.id), "exploracion", lugar_nombre)

        await interaction.response.send_message(mensaje)

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

    @discord.app_commands.command(
        name="reset", description="Reinicia tu superviviente (solo desarrollo)."
    )
    async def reset(self, interaction: discord.Interaction):
        if interaction.user.id != 1414035229286596719:
            await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando.", ephemeral=True
            )
            return
        reset_survivor(str(interaction.user.id))
        await interaction.response.send_message("✅ Superviviente reiniciado.")

    # ==========================================
    # SISTEMA DE COMBATE PVE (FASE 8)
    # ==========================================

    @discord.app_commands.command(
        name="cazar",
        description="Adéntrate en una zona peligrosa para buscar enemigos.",
    )
    async def cazar(self, interaction: discord.Interaction):

        if not has_survivor(str(interaction.user.id)):
            await interaction.response.send_message(
                "❌ Primero debes crear tu perfil con **/perfil**."
            )
            return

        survivor = get_or_create_survivor(
            str(interaction.user.id), interaction.user.display_name
        )

        if survivor["status"] == "Muerto":
            await interaction.response.send_message(
                "💀 Estás muerto. No puedes pelear en este estado.", ephemeral=True
            )
            return

        # Importamos la configuración localmente para no saturar los imports de arriba
        from config.enemies import ENEMIES

        # Elegimos un enemigo al azar
        enemigo_nombre = random.choice(list(ENEMIES.keys()))
        enemigo_data = dict(ENEMIES[enemigo_nombre])  # Hacemos una copia

        # --- LÓGICA DE LA INTERFAZ DE COMBATE ---
        class CombatView(discord.ui.View):
            def __init__(self, original_interact, e_name, e_data):
                super().__init__(timeout=120)
                self.original_interact = original_interact
                self.e_name = e_name
                self.e_hp = e_data["hp"]
                self.e_max_hp = e_data["hp"]
                self.e_data = e_data

            # Función para refrescar la pantalla de combate
            async def update_combat(self, interact: discord.Interaction, msg: str):
                s = get_or_create_survivor(
                    str(interact.user.id), interact.user.display_name
                )
                player_hp = s["health"]

                embed = discord.Embed(
                    title=f"⚔️ Combate: {self.e_data['emoji']} {self.e_name}",
                    description=msg,
                    color=self.e_data["color"],
                )
                embed.add_field(
                    name="Tu Vida", value=f"❤️ {player_hp}/100", inline=True
                )
                embed.add_field(
                    name="Vida Enemigo",
                    value=f"🩸 {self.e_hp}/{self.e_max_hp}",
                    inline=True,
                )

                # Si alguien muere, apagamos los botones
                if self.e_hp <= 0 or player_hp <= 0:
                    for btn in self.children:
                        btn.disabled = True
                    await interact.response.edit_message(embed=embed, view=self)
                else:
                    await interact.response.edit_message(embed=embed, view=self)

            @discord.ui.button(
                label="Atacar", emoji="🗡️", style=discord.ButtonStyle.danger
            )
            async def btn_atacar(
                self, interact: discord.Interaction, button: discord.ui.Button
            ):
                if interact.user.id != self.original_interact.user.id:
                    return

                # Calculamos nuestro daño (Si tiene Cóctel Molotov en inventario, pega más fuerte)
                player_dmg = random.randint(15, 25)
                inventory = get_inventory(str(interact.user.id))
                tiene_arma = any(i["item"] == "Cóctel molotov" for i in inventory)

                if tiene_arma:
                    player_dmg += 15  # Bonus de arma especial

                self.e_hp -= player_dmg
                msg = f"🗡️ Has atacado y causado **{player_dmg}** de daño.\n"

                # Si matamos al enemigo
                if self.e_hp <= 0:
                    self.e_hp = 0
                    msg += f"\n💀 **¡Has derrotado a {self.e_name}!**"

                    # Damos Overos
                    loot_o = random.randint(*self.e_data["loot_overos"])
                    add_overos(str(interact.user.id), loot_o)
                    msg += f"\n🦴 Obtuviste **{loot_o} Overos**."

                    # Damos Objeto (50% de probabilidad)
                    if self.e_data["loot_item"] and random.random() > 0.5:
                        add_item(str(interact.user.id), self.e_data["loot_item"], 1)
                        msg += f"\n📦 Dejó caer: **{self.e_data['loot_item']}**."
                else:
                    # El enemigo contraataca
                    enemy_d = random.randint(*self.e_data["daño"])
                    update_health(str(interact.user.id), -enemy_d)
                    msg += (
                        f"\n💥 El enemigo contraataca y te hace **{enemy_d}** de daño."
                    )

                    # Posible infección o estado
                    if self.e_data.get("efecto") and random.random() < self.e_data.get(
                        "efecto_probabilidad", 0
                    ):
                        add_effect(str(interact.user.id), self.e_data["efecto"])
                        msg += f"\n🧪 ¡Te ha causado el estado **{self.e_data['efecto']}**!"

                await self.update_combat(interact, msg)

            @discord.ui.button(
                label="Curarse", emoji="🩹", style=discord.ButtonStyle.success
            )
            async def btn_curar(
                self, interact: discord.Interaction, button: discord.ui.Button
            ):
                if interact.user.id != self.original_interact.user.id:
                    return

                inventory = get_inventory(str(interact.user.id))
                healed = False
                msg = ""

                # Buscamos algo para curarnos rápidamente sin salir del combate
                for i in inventory:
                    if i["item"] in ["Venda", "Botiquín", "Comida enlatada"]:
                        exito, _ = use_item(str(interact.user.id), i["item"])
                        if exito:
                            healed = True
                            msg = f"🩹 Usaste tu {i['item']} rápidamente en medio de la pelea.\n"
                            break

                if not healed:
                    msg = "❌ No tienes objetos curativos rápidos (Venda, Botiquín o Comida enlatada).\n"

                # El enemigo aprovecha que nos curamos para pegarnos
                enemy_d = random.randint(*self.e_data["daño"])
                update_health(str(interact.user.id), -enemy_d)
                msg += f"\n💥 Mientras estabas distraído, el enemigo te golpea y hace **{enemy_d}** de daño."

                await self.update_combat(interact, msg)

            @discord.ui.button(
                label="Huir", emoji="🏃", style=discord.ButtonStyle.secondary
            )
            async def btn_huir(
                self, interact: discord.Interaction, button: discord.ui.Button
            ):
                if interact.user.id != self.original_interact.user.id:
                    return

                # 60% de probabilidad de escapar con éxito
                if random.random() > 0.4:
                    self.e_hp = 0
                    for btn in self.children:
                        btn.disabled = True
                    embed = discord.Embed(
                        title="🏃 Escapatoria exitosa",
                        description="Corriste tan rápido como pudiste y lograste huir del combate con vida.",
                        color=discord.Color.light_grey(),
                    )
                    await interact.response.edit_message(embed=embed, view=self)
                else:
                    enemy_d = random.randint(*self.e_data["daño"])
                    update_health(str(interact.user.id), -enemy_d)
                    msg = f"❌ Tropezaste al intentar huir. El enemigo te alcanza y te hace **{enemy_d}** de daño."
                    await self.update_combat(interact, msg)

        # Enviamos el mensaje inicial del combate
        view = CombatView(interaction, enemigo_nombre, enemigo_data)

        embed_inicio = discord.Embed(
            title="⚔️ ¡Peligro Inminente!",
            description=f"Te has adentrado en una zona peligrosa y te topaste con un **{enemigo_nombre}**.\n¿Qué vas a hacer?",
            color=enemigo_data["color"],
        )
        embed_inicio.add_field(
            name="Tu Vida", value=f"❤️ {survivor['health']}/100", inline=True
        )
        embed_inicio.add_field(
            name="Vida Enemigo",
            value=f"🩸 {enemigo_data['hp']}/{enemigo_data['hp']}",
            inline=True,
        )

        await interaction.response.send_message(embed=embed_inicio, view=view)

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
                exito, msg = claim_quest_reward(str(btn_interact.user.id))
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

            embed.add_field(
                name="Recompensa",
                value=f"🦴 {q_data['recompensa_overos']}\n📦 {q_data.get('recompensa_item', 'Nada')}",
            )
        else:
            embed.description = "No tienes ninguna misión activa en este momento. ¡Busca trabajo en el tablón!"

        await interaction.response.send_message(embed=embed, view=MisionView())

    @discord.app_commands.command(
        name="reset", description="Reinicia tu superviviente (solo desarrollo)."
    )
    async def reset(self, interaction: discord.Interaction):
        if interaction.user.id != 1414035229286596719:
            return
        reset_survivor(str(interaction.user.id))
        await interaction.response.send_message("✅ Superviviente reiniciado.")


async def setup(bot):
    await bot.add_cog(Survivors(bot))
