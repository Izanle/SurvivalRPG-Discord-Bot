# Configuración de Misiones (Fase 9)

QUESTS = {
    "caceria_ratas": {
        "tipo": "caceria",
        "titulo": "Plaga de Ratas",
        "descripcion": "Las ratas mutantes están arruinando los suministros. Elimina a 3 de ellas.",
        "target": "Rata Mutante",
        "required": 3,
        "recompensa_overos": 50,
        "recompensa_item": "Analgésicos",
        "emoji": "🐀",
    },
    "caceria_saqueadores": {
        "tipo": "caceria",
        "titulo": "Limpiando las Calles",
        "descripcion": "Un grupo de saqueadores está merodeando cerca. Dales una lección.",
        "target": "Saqueador",
        "required": 2,
        "recompensa_overos": 120,
        "recompensa_item": "Comida enlatada",
        "emoji": "🥷",
    },
    "recoleccion_agua": {
        "tipo": "recoleccion",
        "titulo": "Sed Inagotable",
        "descripcion": "La Doctora necesita agua limpia para los heridos. Consigue 2 botellas de agua.",
        "target": "Botella de agua",
        "required": 2,
        "recompensa_overos": 80,
        "recompensa_item": "Vendaje estéril",
        "emoji": "💧",
    },
    "exploracion_hospital": {
        "tipo": "exploracion",
        "titulo": "Búsqueda Médica",
        "descripcion": "Necesitamos saber si el viejo Hospital aún tiene recursos médicos. Explóralo 3 veces.",
        "target": "Hospital",
        "required": 3,
        "recompensa_overos": 100,
        "recompensa_item": "Botiquín",
        "emoji": "🏥",
    },
}
