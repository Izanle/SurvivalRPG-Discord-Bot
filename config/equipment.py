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
    "Bate de béisbol": {
        "tipo": "arma",
        "descripcion": "Un bate de aluminio ideal para defenderse a corta distancia sin gastar balas.",
        "emoji": "🏏",
        "bonus_dano": 15,
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
    # La pistola del abismo es un arma especial que puede tener efectos negativos al usarla, pero su daño es muy alto
    "Pistola del Abismo": {
        "tipo": "arma",
        "bonus_dano": 50,
        "emoji": "🔫",
        "descripcion": "Esta arma no deberia existir",
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
    "Camisa de fuerza maldita": {
        "tipo": "armadura",
        "reduccion_dano": 40,  # Reduce un 40% el daño recibido
        "emoji": "🧥",
        "descripcion": "Una camisa de fuerza, pero se siente demasiado extraña.",
    },
}


# Nota de diseño: Si ya tienes armaduras creadas o planeas añadirlas en el futuro,
# puedes agregarlas aquí siguiendo este formato de ejemplo:
# "Chaleco táctico": {
#     "tipo": "armadura",
#     "descripcion": "Protección de kevlar que absorbe impactos corporales.",
#     "emoji": "🦺",
#     "reduccion_dano": 20,  # Esto reducirá un 20% el daño de los enemigos en /cazar
# }
#
# Formato para agregar una nueva arma equipable
#
#   "Pistola de 9mm": {
#        "tipo": "arma",
#        "bonus_dano": 30,
#        "emoji": "🔫",
#        "descripcion": "Un arma de fuego fiable. Las balas valen oro.",
#    },
#
