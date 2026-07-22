# Misiones disponibles en el tablón de anuncios (Fase 9).
# Ahora soportan múltiples objetos de recompensa gracias a la clave "recompensa_items".

QUESTS = {
    "recoleccion_chatarra": {
        "titulo": "Mecánico del Refugio",
        "descripcion": "El generador principal está fallando. Necesitamos que salgas al páramo y recolectes chatarra para las reparaciones.",
        "emoji": "⚙️",
        "tipo": "recoleccion",
        "target": "Chatarra",  # Objeto a recolectar
        "required": 10,  # Cantidad necesaria
        "recompensa_overos": 150,
        "recompensa_item": None,
        "recompensa_items": [
            {"item": "Linterna", "cantidad": 1},
            {"item": "Pilas", "cantidad": 2},
        ],
    },
    "caceria_ratas": {
        "titulo": "Control de Plagas",
        "descripcion": "Las ratas mutantes están mordiendo los cables del perímetro. Sal ahí fuera y reduce su número antes de que nos quedemos a oscuras.",
        "emoji": "🐀",
        "tipo": "caceria",
        "target": "Rata Mutante",  # Enemigo a derrotar
        "required": 5,  # Cantidad a derrotar
        "recompensa_overos": 100,
        "recompensa_item": None,
        "recompensa_items": [
            {"item": "Comida enlatada", "cantidad": 2},
            {"item": "Botella de agua", "cantidad": 2},
        ],
    },
    "buscar_medicina": {
        "titulo": "Suministros de Emergencia",
        "descripcion": "La enfermería del refugio está colapsada. Necesitamos vendas limpias urgente para tratar a los heridos.",
        "emoji": "💊",
        "tipo": "recoleccion",
        "target": "Venda",
        "required": 5,
        "recompensa_overos": 120,
        "recompensa_item": None,
        "recompensa_items": [
            {"item": "Botiquín", "cantidad": 1},
            {"item": "Analgésicos", "cantidad": 2},
            {"item": "Alcohol medicinal", "cantidad": 1},
        ],
    },
    "limpieza_comisaria": {
        "titulo": "Limpieza del Precinto",
        "descripcion": "Los infectados han tomado la antigua comisaría. Despeja la zona para que podamos acceder a su armería de forma segura.",
        "emoji": "🚓",
        "tipo": "caceria",
        "target": "Infectado",
        "required": 3,
        "recompensa_overos": 300,
        "recompensa_item": None,
        "recompensa_items": [
            {"item": "Pistola 9mm", "cantidad": 1},
            {"item": "Munición 9mm", "cantidad": 3},
        ],
    },
    "caceria_saqueadores": {
        "titulo": "Defensa del Territorio",
        "descripcion": "Un grupo de saqueadores está merodeando demasiado cerca de nuestras rutas comerciales. Dales una lección que no olviden.",
        "emoji": "🥷",
        "tipo": "caceria",
        "target": "Saqueador",
        "required": 4,
        "recompensa_overos": 350,
        "recompensa_item": None,
        "recompensa_items": [
            {"item": "Bate de béisbol", "cantidad": 1},
            {"item": "Ración militar", "cantidad": 2},
            {"item": "Chatarra", "cantidad": 4},
        ],
    },
}
