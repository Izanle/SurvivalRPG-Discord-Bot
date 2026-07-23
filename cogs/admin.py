# Todos los comandos administrativos del servidor.

import discord
from discord.ext import commands
from utils.users import reset_survivor
from utils.users import clear_inventory
from utils.users import add_item
from config.items import ITEMS
from utils.users import add_effect


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


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando para reiniciar al usuario
    @discord.app_commands.command(
        name="reset", description="Reinicia tu superviviente (solo desarrollo)."
    )
    async def reset(self, interaction: discord.Interaction):  # noqa: F811
        if interaction.user.id != 1414035229286596719:
            return
        reset_survivor(str(interaction.user.id))
        await interaction.response.send_message("✅ Superviviente reiniciado.")

    # Comando administrativo para limpiar el inventario
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

    # Comando administrativo para agregar objetos
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

    # Comando administrativo para agregar efectos
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

    # Comando para revivir
    @discord.app_commands.command(
        name="revivir",
        description="[ADMIN] Revive a un jugador muerto como por arte de magia.",
    )
    @discord.app_commands.describe(
        usuario="El jugador al que quieres revivir (déjalo en blanco para revivirte a ti mismo)"
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def revivir(
        self, interaction: discord.Interaction, usuario: discord.Member = None
    ):
        # Si no seleccionas a nadie, te revives a ti mismo por defecto
        target = usuario or interaction.user
        discord_id = str(target.id)

        from utils.users import has_survivor, update_status, update_health

        if not has_survivor(discord_id):
            return await interaction.response.send_message(
                "❌ Ese usuario no tiene un perfil creado.", ephemeral=True
            )

        # Le cambiamos el estado a Sano y le curamos 100 puntos de vida de golpe
        update_status(discord_id, "Vivo")
        update_health(discord_id, 100)

        await interaction.response.send_message(
            f"👼 ¡Un milagro en el páramo! **{target.display_name}** ha resucitado con la salud al máximo."
        )


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
