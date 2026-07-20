# Configuración de NPCs (Fase 7)
import random

NPCS = {
    "El Mercader Errante": {
        "emoji": "🎒",
        "descripcion": "Un viajero misterioso con una mochila que parece infinita.",
        "saludo": "Tengo cosas que no verás en la tienda normal. Si tienes los Overos, claro...",
        "color": 0x8B4513,  # Marrón
    },
    "La Doctora": {
        "emoji": "👩‍⚕️",
        "descripcion": "Una médica que instaló un pequeño campamento de primeros auxilios.",
        "saludo": "Déjame ver esas heridas. Te costará algo de suministros, pero te dejaré como nuevo.",
        "color": 0xFFFFFF,  # Blanco
    },
    "El Informante": {
        "emoji": "🕵️",
        "descripcion": "Alguien que siempre está en las sombras, observando y escuchando.",
        "saludo": "La información es poder, amigo. ¿Quieres saber qué ocurre en la ciudad? Te costará.",
        "color": 0x2F4F4F,  # Gris oscuro
    },
}

RUMORES = [
    "Dicen que si exploras el Hospital con la moral alta, encuentras mejores medicinas.",
    "No te fíes de los ruidos en el Metro. Nunca estás solo ahí abajo.",
    "Combinar una botella de agua y alcohol medicinal crea algo explosivo... ten cuidado.",
    "Si te muerde algo en el Bosque, búscate un antídoto rápido o la infección te consumirá.",
    "El Mercader siempre tiene algo especial, pero cobra caro.",
]
