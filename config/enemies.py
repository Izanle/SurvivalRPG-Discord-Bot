# Configuración de Enemigos (Fase 8)

ENEMIES = {
    "Rata Mutante": {
        "emoji": "🐀",
        "hp": 30,
        "daño": (3, 8),  # Daño aleatorio entre 3 y 8
        "loot_overos": (1, 6),  # Cuántos Overos deja al morir
        "loot_item": None,
        "efecto_probabilidad": 0,
        "color": 0x8B4513,  # Marrón
    },
    "Saqueador": {
        "emoji": "🥷",
        "hp": 65,
        "daño": (8, 15),
        "loot_overos": (10, 25),
        "loot_item": "Venda",  # Objeto que puede dejar caer
        "efecto_probabilidad": 0,
        "color": 0xFF0000,  # Rojo
    },
    "Infectado": {
        "emoji": "🧟",
        "hp": 100,
        "daño": (12, 22),
        "loot_overos": (5, 15),
        "loot_item": None,
        "efecto_probabilidad": 0.3,  # 30% de probabilidad de infectarte
        "efecto": "Infectado",
        "color": 0x2F4F4F,  # Gris oscuro verdoso
    },
}
