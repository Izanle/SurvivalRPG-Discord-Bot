# Configuración de los niveles del refugio (Fase 6)
# Cada nivel mejora la curación y reduce el tiempo de espera (cooldown) para volver a dormir.

SHELTER_LEVELS = {
    1: {
        "nombre": "Cartones y mantas",
        "descripcion": "Un rincón apenas protegido del clima. Mejor que nada.",
        "costo_overos": 0,
        "costo_items": {},
        "cura_descanso": 15,
        "cooldown_horas": 12,
    },
    2: {
        "nombre": "Tienda improvisada",
        "descripcion": "Te protege de la lluvia y te permite descansar un poco mejor.",
        "costo_overos": 150,
        "costo_items": {"Cuerda": 2, "Venda": 1},  # Objetos requeridos para mejorar
        "cura_descanso": 35,
        "cooldown_horas": 10,
    },
    3: {
        "nombre": "Cabaña reforzada",
        "descripcion": "Un lugar verdaderamente seguro. Puedes relajarte por completo.",
        "costo_overos": 400,
        "costo_items": {"Pilas": 2, "Navaja": 1},
        "cura_descanso": 60,
        "cooldown_horas": 8,
    },
    4: {
        "nombre": "Búnker sellado",
        "descripcion": "La máxima seguridad. Un lujo inalcanzable del viejo mundo.",
        "costo_overos": 1000,
        "costo_items": {"Linterna": 1, "Alcohol medicinal": 3},
        "cura_descanso": 100,
        "cooldown_horas": 6,
    },
}
