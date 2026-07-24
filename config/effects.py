SURVIVOR_EFFECTS = {
    "Rasguño": {
        "tipo": "herida",
        "gravedad": 1,
        "evolucion": "Cortadura leve",
        "exploraciones": 5,
        "daño": 1,
    },
    "Cortadura leve": {
        "tipo": "herida",
        "gravedad": 2,
        "evolucion": "Herida grave",
        "exploraciones": 8,
        "daño": 2,
    },
    "Herida grave": {
        "tipo": "herida",
        "gravedad": 3,
        "evolucion": "Infectado",
        "exploraciones": 10,
        "daño": 10,
    },
    "Infectado": {
        "tipo": "enfermedad",
        "gravedad": 4,
        "evolucion": None,
        "exploraciones": None,
        "daño": 7,
    },
    "Intoxicado": {
        "tipo": "enfermedad",
        "gravedad": 2,
        "evolucion": None,
        "exploraciones": None,
        "daño": 2,
    },
    "Sangrando": {
        "tipo": "herida",
        "gravedad": 2,
        "evolucion": "Herida grave",
        "exploraciones": 4,
        "daño": 4,
    },
}
