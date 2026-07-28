# Recetas de crafting (Fase 4).
# Cada receta indica qué objetos (y cuántos) se necesitan
# para crear el objeto resultado.

RECIPES = {
    # ==========================================
    # OBJETOS CONSUMBILES/DE EXPLORACIÓN
    # ==========================================
    "Vendaje estéril": {
        "ingredientes": {
            "Venda": 2,
            "Alcohol medicinal": 1,
        },
        "mensaje": "Combinas las vendas con alcohol medicinal y creas un vendaje estéril.",
    },
    "Linterna cargada": {
        "ingredientes": {
            "Linterna": 1,
            "Pilas": 1,
        },
        "mensaje": "Cargas la linterna con pilas nuevas. Ahora dura mucho más tiempo encendida.",
    },
    "Venda": {
        "ingredientes": {
            "Trapos": 1,
            "Alcohol medicinal": 1,
        },
        "mensaje": "Combinas las vendas con alcohol medicinal y creas un vendaje estéril.",
    },
    "Cuero": {
        "ingredientes": {
            "Tanino": 1,
            "Cuero crudo": 1,
        },
        "mensaje": "Combinas ambos materiales y entre arcadas, logras conseguir un cuero utilizable.",
    },
    "Aluminio": {
        "ingredientes": {
            "Ácido fosfórico": 1,
            "Aluminio contaminado": 1,
        },
        "mensaje": "Limpias el trozo de aluminio sumergiéndolo en el ácido, burbujea intensamente y se siente un olor penetrante. Obtienes aluminio limpio.",
    },
    # ==========================================
    # MATERIALES
    # ==========================================
    "Cuero": {
        "ingredientes": {
            "Tanino": 1,
            "Cuero crudo": 1,
        },
        "mensaje": "Combinas ambos materiales y entre arcadas, logras conseguir un cuero utilizable.",
    },
    "Aluminio": {
        "ingredientes": {
            "Ácido fosfórico": 1,
            "Aluminio contaminado": 1,
        },
        "mensaje": "Limpias el trozo de aluminio sumergiéndolo en el ácido, burbujea intensamente y se siente un olor penetrante. Obtienes aluminio limpio.",
    },
    # ==========================================
    # OBJETOS DE COMBATE
    # ==========================================
    "Cóctel molotov": {
        "ingredientes": {
            "Gasolina": 1,
            "Botella de agua": 1,
            "Cuerda": 1,
        },
        "mensaje": "Llenas la botella con gasolina y usas la cuerda como mecha. ¡Tienes un explosivo improvisado listo para el combate!",
    },
    "Cuchillo de caza": {
        "ingredientes": {
            "Navaja": 1,
            "Chatarra": 1,
        },
        "mensaje": "Combinas las vendas con alcohol medicinal y creas un vendaje estéril.",
    },
    "Armadura de cuero": {
        "ingredientes": {"Cuero": 10, "Cuerda": 5, "Pegamento industrial": 1},
        "mensaje": "Utilizas los pedazos de cuero, un poco de cuerda y el pegamento industrial para armar un atuendo de cuero",
    },
    "Bate con clavos": {
        "ingredientes": {
            "Bate de béisbol": 1,
            "Chatarra": 1,
        },
        "mensaje": "Clavas un montón de puntillas oxidadas y afiladas alrededor del bate, ahora tienes un bate con clavos.",
    },
    "Bate de aluminio": {
        "ingredientes": {
            "Bate de béisbol": 1,
            "Chatarra": 1,
            "Aluminio": 4,
            "Pegamento industrial": 1,
        },
        "mensaje": "Rodeas el bate con una fina capa de aluminio, agregando unas pequeñas protuberancias de chatarra para que de golpes más contundentes. Ahora tienes un bate de aluminio.",
    },
}
