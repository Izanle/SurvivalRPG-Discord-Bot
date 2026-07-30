import random

from datetime import datetime

# Configuración del Mundo y Clima (Fase 10)

WEATHER_TYPES = {
    "Despejado": {
        "emoji": "☀️",
        "desc": "Un día tranquilo. Ideal para explorar el páramo sin muchas preocupaciones.",
        "peligro": 0,
        "loot_bonus": 0,
    },
    "Niebla densa": {
        "emoji": "🌫️",
        "desc": "Cuesta ver a dos metros de distancia. Es fácil tropezar con enemigos o perderse.",
        "peligro": 10,
        "loot_bonus": 5,
    },
    "Tormenta eléctrica": {
        "emoji": "⛈️",
        "desc": "Rayos y truenos ensordecedores. Los monstruos están más agresivos.",
        "peligro": 15,
        "loot_bonus": 10,
    },
    "Lluvia ácida": {
        "emoji": "🌧️",
        "desc": "El agua quema la piel y daña el equipo. Muy peligroso estar afuera.",
        "peligro": 25,
        "loot_bonus": 20,
    },
}


def get_current_weather():
    """
    Simula el clima actual basándose en la hora.
    Retorna: (nombre_clima, datos_clima, es_dia)
    """
    hora_actual = datetime.now().hour
    es_dia = 6 <= hora_actual < 19  # De 6:00 AM a 6:59 PM es de día

    # Seleccionamos un clima al azar de forma "pseudo-constante"
    # Usando el día del año y la hora actual como semilla para que todos los jugadores
    # tengan el mismo clima durante la misma hora.
    seed_clima = datetime.now().timetuple().tm_yday + hora_actual
    random.seed(seed_clima)

    nombre_clima = random.choice(list(WEATHER_TYPES.keys()))

    # Reseteamos la semilla aleatoria para que no afecte a otros sistemas del juego (como drops o daño)
    random.seed()

    return nombre_clima, WEATHER_TYPES[nombre_clima], es_dia
