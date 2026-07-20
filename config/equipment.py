# Configuración de Armas y Armaduras (Sistema de Equipamiento)

EQUIPMENT = {
    # Armas (Aumentan el daño al atacar)
    "Cuchillo de caza": {
        "tipo": "arma",
        "bonus_dano": 10,
        "emoji": "🗡️",
        "descripcion": "Un cuchillo afilado y resistente. Letal a corta distancia.",
    },
    "Bate con clavos": {
        "tipo": "arma",
        "bonus_dano": 18,
        "emoji": "🏏",
        "descripcion": "Improvisado pero devastador contra los infectados.",
    },
    "Pistola de 9mm": {
        "tipo": "arma",
        "bonus_dano": 30,
        "emoji": "🔫",
        "descripcion": "Un arma de fuego fiable. Las balas valen oro.",
    },
    "Cóctel molotov": {
        "tipo": "arma",
        "bonus_dano": 25,
        "emoji": "🧨",
        "descripcion": "Explosivo casero para arrasar con los enemigos.",
    },
    # Armaduras / Protección (Reducen el daño recibido)
    "Traje de jean": {
        "tipo": "armadura",
        "reduccion_dano": 5,  # Reduce un 5% el daño recibido
        "emoji": "👖",
        "descripcion": "Ropa de mezclilla gruesa. Protege ligeramente de rasguños.",
    },
    "Armadura de cuero": {
        "tipo": "armadura",
        "reduccion_dano": 12,  # Reduce un 12% el daño recibido
        "emoji": "🧥",
        "descripcion": "Piezas de cuero endurecido unidas con correas.",
    },
    "Chaleco antibalas": {
        "tipo": "armadura",
        "reduccion_dano": 25,  # Reduce un 25% el daño recibido
        "emoji": "🦺",
        "descripcion": "Protección militar pesada. Absorbe impactos balísticos y golpes fuertes.",
    },
}
