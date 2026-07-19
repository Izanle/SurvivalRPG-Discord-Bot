from config.events import EVENTS
from config.locations import LOCATIONS
from datetime import datetime, timedelta
import random

import discord
from discord.ext import commands

from config.shelter import SHELTER_LEVELS
from config.items import ITEMS
from config.effects import SURVIVOR_EFFECTS
from config.recipes import RECIPES
from config.shop import SHOP_ITEMS
from utils.users import (
    get_or_create_survivor,
    add_overos,
    get_effects,
    add_effect,
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

    # Agrega un efecto de prueba.
    @discord.app_commands.command(
        name="efecto", description="Añade un efecto (solo para pruebas)."
    )
    @discord.app_commands.describe(efecto="Nombre del efecto.")
    async def efecto(self, interaction: discord.Interaction, efecto: str):

        # Solo tú puedes usarlo.
        if interaction.user.id != 1414035229286596719:
            await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando.", ephemeral=True
            )
            return

        add_effect(str(interaction.user.id), efecto)

        await interaction.response.send_message(f"🧪 Efecto agregado: **{efecto}**")

    # Muestra el perfil del superviviente.
    @discord.app_commands.command(
        name="perfil", description="Muestra tu registro de superviviente"
    )
    async def perfil(self, interaction: discord.Interaction):

        survivor = get_or_create_survivor(
            str(interaction.user.id), interaction.user.display_name
        )

        # Obtenemos todos los efectos del jugador.
        effects = get_effects(str(interaction.user.id))
        active_effects = get_active_effects(str(interaction.user.id))

        fecha = datetime.strptime(survivor["created_at"], "%Y-%m-%d %H:%M:%S").strftime(
            "%d/%m/%Y"
        )

        # Construimos el texto de los efectos.
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

            # Construimos el texto de efectos activos.
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

    # Muestra el inventario del jugador.
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

    # Comando administrativo para agregar objetos.
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

    # Comando para limpiar el inventario, SOLO ADMIN
    @discord.app_commands.command(
        name="limpiar_inventario", description="Limpia todo el inventario del jugador."
    )
    async def limpiar_inventario(self, interaction: discord.Interaction):

        # Cambia este número por tu ID de Discord.
        OWNER_ID = "1414035229286596719"

        if str(interaction.user.id) != OWNER_ID:

            await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando."
            )
            return

        clear_inventory(str(interaction.user.id))

        await interaction.response.send_message("🧹 Inventario limpiado correctamente.")

    # Usa un objeto del inventario mediante menú.
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

    # Comando de crafting: combina objetos del inventario.
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

    # Muestra los objetos disponibles en la tienda.
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

    # Compra un objeto de la tienda.
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

    # Vende un objeto del inventario.
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

    # Primer comando de exploración (Actualizado).
    @discord.app_commands.command(
        name="explorar", description="Explora los alrededores en busca de algo..."
    )
    @discord.app_commands.describe(
        lugar="Lugar específico a explorar (opcional). Si no eliges, exploras alrededores genéricos."
    )
    @discord.app_commands.choices(
        lugar=[
            discord.app_commands.Choice(name=f"{data['emoji']} {nombre}", value=nombre)
            for nombre, data in LOCATIONS.items()
        ]
    )
    async def explorar(
        self,
        interaction: discord.Interaction,
        lugar: discord.app_commands.Choice[str] = None,
    ):

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
                "💀 Estás muerto. No puedes explorar hasta volver a la vida.",
                ephemeral=True,
            )
            return

        increase_effect_progress(str(interaction.user.id))
        update_effects(str(interaction.user.id))
        apply_effect_damage(str(interaction.user.id))

        last_explore = get_last_explore(str(interaction.user.id))

        if last_explore:
            ultima_exploracion = datetime.strptime(last_explore, "%Y-%m-%d %H:%M:%S")

            cooldown = timedelta(minutes=0)

            if datetime.now() < ultima_exploracion + cooldown:
                restante = (ultima_exploracion + cooldown) - datetime.now()

                minutos = restante.seconds // 60
                segundos = restante.seconds % 60

                await interaction.response.send_message(
                    f"⏳ Aún no puedes explorar. Espera {minutos} minutos y {segundos} segundos."
                )
                return

        print("Última exploración:", last_explore)

        lugar_nombre = lugar.value if lugar else None

        # Filtramos los eventos disponibles según el lugar.
        eventos_disponibles = []

        for evento_posible in EVENTS:

            lugares_evento = evento_posible.get("lugares")

            if not lugares_evento:
                eventos_disponibles.append(evento_posible)

            elif lugar_nombre and lugar_nombre in lugares_evento:
                eventos_disponibles.append(evento_posible)

        # Seguridad: si por algún motivo no queda ningún evento
        if not eventos_disponibles:
            eventos_disponibles = [
                evento_posible
                for evento_posible in EVENTS
                if not evento_posible.get("lugares")
            ]

        tiene_moral = has_active_effect(str(interaction.user.id), "moral")

        # Calculamos los pesos de cada evento.
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

        # Si el evento tiene condiciones (reacciona a objetos del inventario)
        evento, item_consumido = resolve_event_condition(
            str(interaction.user.id), evento
        )

        if tiene_moral:
            print("🍫 El superviviente tiene moral alta")

        tiene_energia = has_active_effect(str(interaction.user.id), "energia")

        evitar_dano = False

        if tiene_energia and evento["damage"] > 0:

            if evento["damage"] <= 5:

                if random.random() <= 0.5:

                    evitar_dano = True

        if tiene_energia:
            print("⚡ El superviviente tiene energía activa")

        reduce_active_effects(str(interaction.user.id))

        # Obtenemos la cantidad de Overos del evento.
        if isinstance(evento["overos"], tuple):
            cantidad_overos = random.randint(evento["overos"][0], evento["overos"][1])
        else:
            cantidad_overos = evento["overos"]

        moral_bonus = 0

        if tiene_moral and cantidad_overos > 0:
            moral_bonus = max(1, round(cantidad_overos * 0.1))
            cantidad_overos += moral_bonus

        # Si el evento entrega Overos, los agregamos al jugador.
        if cantidad_overos > 0:
            add_overos(str(interaction.user.id), cantidad_overos)

        # Construimos el mensaje que verá el jugador.
        if lugar_nombre:
            emoji_lugar = LOCATIONS[lugar_nombre]["emoji"]
            mensaje = f"{emoji_lugar} **{lugar_nombre}**\n\n" + evento["mensaje"]
        else:
            mensaje = evento["mensaje"]

        # Si encontró Overos, lo indicamos.
        if cantidad_overos > 0:
            mensaje += f"\n\n🦴 Has encontrado **{cantidad_overos} Overos**."

        if moral_bonus > 0:
            mensaje += (
                f"\n\n🍫 Tu buen ánimo te ayudó a encontrar "
                f"**{moral_bonus} Overos** extra."
            )

        if evitar_dano:
            mensaje += (
                "\n\n⚡ Gracias a tu energía, lograste esquivar el daño a tiempo."
            )
        else:
            if evento["damage"] > 0:
                update_health(str(interaction.user.id), -evento["damage"])
                mensaje += f"\n\n❤️ Has perdido **{evento['damage']}** puntos de vida."

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

        await interaction.response.send_message(mensaje)

    # Comando interactivo del refugio (Fase 6)
    @discord.app_commands.command(
        name="refugio", description="Gestiona tu refugio, descansa y mejóralo."
    )
    async def refugio(self, interaction: discord.Interaction):

        if not has_survivor(str(interaction.user.id)):
            await interaction.response.send_message(
                "❌ Primero debes crear tu perfil con **/perfil**."
            )
            return

        # Obtenemos los datos actuales
        shelter = get_or_create_shelter(str(interaction.user.id))
        nivel = shelter["level"]
        datos_actuales = SHELTER_LEVELS[nivel]

        # Creamos un Embed bonito para mostrar la base
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

        # Mostramos los requisitos del siguiente nivel si existe
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

        # Creamos los botones interactivos
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

            # ¡CORRECCIÓN AQUÍ! Agregado 'ephemeral=not exito'
            await btn_interact.response.send_message(mensaje, ephemeral=not exito)

            # Si mejoró con éxito, desactivamos los botones para que vuelva a usar el comando
            if exito:
                for item in self.children:
                    item.disabled = True
                await btn_interact.message.edit(view=self)

        view = RefugioView()

        # Desactivamos el botón de mejorar si está al nivel máximo
        if nivel + 1 not in SHELTER_LEVELS:
            view.children[1].disabled = True
            view.children[1].label = "Nivel Máximo"

        await interaction.response.send_message(embed=embed, view=view)

    # Comando para reiniciar el perfil.
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


async def setup(bot):
    await bot.add_cog(Survivors(bot))
