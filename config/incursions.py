# Configuración de Incursiones / Exploración Profunda (Fase Avanzada)

INCURSIONS = {
    "Hospital": {
        "titulo": "🏥 Incursión: Hospital Abandonado",
        "color": 0x3498DB,
        "nodos": {
            "inicio": {
                "descripcion": "Estás en el frío vestíbulo principal. A la izquierda está la antigua recepción. A la derecha, ves una ambulancia destrozada en el patio interior. Al fondo, una puerta doble con cerradura magnética conduce a la Farmacia.",
                "opciones": [
                    {
                        "label": "Revisar recepción",
                        "siguiente": "recepcion",
                        "emoji": "📋",
                        "un_solo_uso": True,  # Desaparecerá después de usarse
                    },
                    {
                        "label": "Entrar a la Farmacia",
                        "siguiente": "farmacia",
                        "emoji": "💳",
                        "requiere_item": "Tarjeta de acceso",  # Bloqueado si no tienes la tarjeta
                    },
                    {
                        "label": "Revisar ambulancia",
                        "siguiente_azar": [  # 70% de botín, 30% de peligro
                            {"nodo": "ambulancia_loot", "probabilidad": 70},
                            {"nodo": "ambulancia_trampa", "probabilidad": 30},
                        ],
                        "emoji": "🚑",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Abandonar el hospital",
                        "siguiente": "salir",
                        "emoji": "🏃",
                    },
                ],
            },
            "recepcion": {
                "descripcion": "Fuerzas los cajones oxidados de la recepción. Encuentras algunos útiles médicos.",
                "loot": {"item": "Venda", "cantidad": 1},
                "overos": (10, 20),
                "opciones": [
                    {
                        "label": "Volver al vestíbulo",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "farmacia": {
                "descripcion": "¡La tarjeta funciona! La puerta se abre revelando el paraíso de la medicina... aunque gran parte está caducada, te llevas lo mejor.",
                "loot": {"item": "Botiquín", "cantidad": 1},
                "overos": (50, 100),
                "opciones": [
                    {
                        "label": "Salir al vestíbulo",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "ambulancia_loot": {
                "descripcion": "Abres las puertas traseras de la ambulancia. ¡Tuviste suerte! Había un maletín paramédico intacto.",
                "loot": {"item": "Analgésicos", "cantidad": 2},
                "opciones": [
                    {
                        "label": "Regresar al inicio",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "ambulancia_trampa": {
                "descripcion": "¡Pésima idea! Al intentar abrir la ambulancia, se dispara una vieja alarma atrayendo monstruos. ¡Prepárate para luchar!",
                "damage": 10,
                "tipo": "combate",  # Genera los botones de luchar/huir
                "enemigo": "Infectado",
            },
            "salir": {
                "tipo": "fin",
                "descripcion": "La atmósfera es demasiado densa. Tomas tus cosas y sales corriendo del hospital antes de que algo te encuentre.",
            },
        },
    }
}
