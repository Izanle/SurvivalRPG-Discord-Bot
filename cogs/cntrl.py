import discord
from discord.ext import commands
from discord import app_commands
import psutil
import os


class ControlCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="cntrl",
        description="Muestra el consumo actual de RAM y CPU del bot de supervivencia.",
    )
    async def cntrl(self, interaction: discord.Interaction):
        # Obtenemos el proceso actual del bot usando su PID
        proceso = psutil.Process(os.getpid())

        # Consumo de memoria RAM en Megabytes (MB)
        memoria_info = proceso.memory_info()
        memoria_mb = memoria_info.rss / 1024 / 1024

        # Porcentaje de uso de CPU (intervalo de 0.1 para una lectura rápida)
        cpu_uso = proceso.cpu_percent(interval=0.1)

        # Información general del sistema
        ram_sistema = psutil.virtual_memory()

        embed = discord.Embed(
            title="🖥️ Panel de Control - Recursos del Bot",
            description="Estado actual del rendimiento del servidor y del proceso.",
            color=0x2F4F4F,
        )

        embed.add_field(
            name="📊 Proceso del Bot",
            value=f"• **RAM Usada:** `{memoria_mb:.2f} MB`\n• **CPU Usada:** `{cpu_uso}%`",
            inline=False,
        )

        embed.add_field(
            name="🌍 Sistema Global",
            value=f"• **RAM Total del Servidor:** `{ram_sistema.percent}%`\n• **Estado:** `Operativo y Estable`",
            inline=False,
        )

        embed.set_footer(text="Survival RPG • Monitoreo de Red")

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ControlCog(bot))
