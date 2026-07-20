# Configuración de Logros (Fase 11)

ACHIEVEMENTS = {
    "trotamundos_1": {
        "nombre": "Trotamundos Novato",
        "descripcion": "Realiza tus primeras 10 exploraciones en el páramo.",
        "emoji": "🚶",
        "requisito": {"tipo": "explorations", "cantidad": 10},
        "recompensa_overos": 100,
        "recompensa_item": None,
        "color": 0x3498DB,  # Azul
    },
    "cazador_1": {
        "nombre": "Primera Sangre",
        "descripcion": "Derrota a tu primer enemigo en combate.",
        "emoji": "💀",
        "requisito": {"tipo": "enemies_defeated", "cantidad": 1},
        "recompensa_overos": 50,
        "recompensa_item": "Venda",
        "color": 0xE74C3C,  # Rojo
    },
    "mercenario_1": {
        "nombre": "Mercenario Local",
        "descripcion": "Completa 3 misiones del tablón de anuncios.",
        "emoji": "📜",
        "requisito": {"tipo": "quests_completed", "cantidad": 3},
        "recompensa_overos": 150,
        "recompensa_item": None,
        "color": 0xF1C40F,  # Amarillo
    },
}
