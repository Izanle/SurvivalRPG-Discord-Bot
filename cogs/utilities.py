import discord
from discord.ext import commands

from utils.users import (
    get_inventory,
    has_survivor,
    get_equipped_gear,
    equip_item,
    use_item,
    craft_item,
)

from config.items import ITEMS
from config.recipes import RECIPES


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        pagina_actual = 0

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


async def setup(bot):
    await bot.add_cog(Utilities(bot))
