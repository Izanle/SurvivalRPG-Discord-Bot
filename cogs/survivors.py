from config.events import EVENTS
from datetime import datetime, timedelta
import random

import discord
from discord.ext import commands

from config.items import ITEMS
from config.effects import SURVIVOR_EFFECTS
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

        for effect in effects:
            print(dict(effect))

        for effect in active_effects:
            print(dict(effect))

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

    # Primer comando de exploración.
    @discord.app_commands.command(
        name="explorar", description="Explora los alrededores en busca de algo..."
    )
    async def explorar(self, interaction: discord.Interaction):

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

        evento = random.choices(
            EVENTS, weights=[evento["chance"] for evento in EVENTS], k=1
        )[0]

        tiene_energia = has_active_effect(str(interaction.user.id), "energia")

        evitar_dano = False

        if tiene_energia and evento["damage"] > 0:

            if evento["damage"] <= 5:

                if random.random() <= 0.5:

                    evitar_dano = True

        if tiene_energia:
            print("⚡ El superviviente tiene energía activa")

        reduce_active_effects(str(interaction.user.id))

        # Empezamos el mensaje con el texto base del evento.
        mensaje = evento["mensaje"]

        # Obtenemos la cantidad de Overos del evento.
        if isinstance(evento["overos"], tuple):
            cantidad_overos = random.randint(evento["overos"][0], evento["overos"][1])
        else:
            cantidad_overos = evento["overos"]

        # Si el evento entrega Overos, los agregamos al jugador.
        if cantidad_overos > 0:
            add_overos(str(interaction.user.id), cantidad_overos)

        # Construimos el mensaje que verá el jugador.
        mensaje = evento["mensaje"]

        # Si encontró Overos, lo indicamos.
        if cantidad_overos > 0:
            mensaje += f"\n\n🦴 Has encontrado " f"**{cantidad_overos} Overos**."

        # Si el evento hace daño, sucede esto
        if evento["damage"] > 0:
            update_health(str(interaction.user.id), -evento["damage"])

        if evento["damage"] > 0:
            mensaje += f"\n\n❤️ Has perdido " f"**{evento['damage']}** puntos de vida."

        # Si el evento aplica un efecto, lo agregamos al jugador
        # y lo anotamos en el mensaje.
        if evento["effect"] is not None:
            add_effect(str(interaction.user.id), evento["effect"])
            mensaje += f"\n\n🧪 Nuevo efecto: **{evento['effect']}**"

        # Si el evento entrega un objeto, lo agregamos al inventario.
        if evento["item"] is not None:
            add_item(str(interaction.user.id), evento["item"])
            mensaje += f"\n\n🎒 Has encontrado: **{evento['item']}**."

        # Una sola respuesta, al final, con el mensaje completo.
        update_last_explore(str(interaction.user.id))

        await interaction.response.send_message(mensaje)

    # Comando para reiniciar el perfil.
    @discord.app_commands.command(
        name="reset", description="Reinicia tu superviviente (solo desarrollo)."
    )
    async def reset(self, interaction: discord.Interaction):

        # Solo tú puedes usarlo.
        if interaction.user.id != 1414035229286596719:
            await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando.", ephemeral=True
            )
            return

        reset_survivor(str(interaction.user.id))

        await interaction.response.send_message("✅ Superviviente reiniciado.")


async def setup(bot):
    await bot.add_cog(Survivors(bot))
