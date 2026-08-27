import discord
from discord.ext import commands
from config.items import ITEMS
from config.shop import SHOP_ITEMS

from utils.users import has_survivor, get_overos, get_inventory, buy_item, sell_item


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


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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


async def setup(bot):
    await bot.add_cog(Shop(bot))
