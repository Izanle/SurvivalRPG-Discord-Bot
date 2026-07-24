# Eventos disponibles durante la exploración.
# - Los eventos SIN la clave "lugares" son GLOBALES y pueden ocurrir en cualquier sitio.
# - Los eventos CON "lugares": ["Nombre"] son EXCLUSIVOS de esa zona específica.
# - El sistema soporta la clave "items": [{"item": "Nombre", "chance": %, "cantidad": (min, max)}] para drops múltiples y aleatorios.

EVENTS = [
    # ==========================================
    # 🌍 EVENTOS GLOBALES (Cualquier lugar)
    # ==========================================
    {
        "mensaje": "🌫️ No encuentras nada interesante entre la densa niebla.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": None,
        "chance": 35,
        "damage": 0,
    },
    {
        "mensaje": "🐺 Una criatura salvaje sale de entre las sombras y logra herirte antes de escapar.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": "Herida grave",
        "chance": 8,
        "damage": 10,
    },
    {
        "mensaje": "🦴 Encuentras un pequeño montón de Overos oculto entre los escombros del suelo.",
        "overos": (5, 20),
        "item": None,
        "items": [],
        "effect": None,
        "chance": 15,
        "damage": 0,
    },
    {
        "mensaje": "🐀 Una rata mutada salió disparada entre la basura y te hizo pegar un buen susto.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": None,
        "chance": 7,
    },
    {
        "mensaje": "🚪 Intentaste forzar una puerta oxidada a patadas y terminaste cortándote con la estructura.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": "Rasguño",
        "chance": 5,
        "damage": 6,
    },
    {
        "mensaje": "🌧️ La lluvia ácida limpió el aire. Aunque quema un poco, hoy todo parece un poco más tranquilo.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": None,
        "chance": 6,
        "damage": 2,
    },
    {
        "mensaje": "🎒 Divisaste una mochila olvidada bajo unos bloques de concreto caídos.",
        "overos": 0,
        "item": None,
        "items": [
            {"item": "Botella de agua", "chance": 80, "cantidad": (1, 2)},
            {"item": "Barra energética", "chance": 40, "cantidad": (1, 1)},
        ],
        "effect": None,
        "chance": 8,
        "damage": 0,
    },
    {
        "mensaje": "👤 Viste a otro superviviente a la distancia. Ambos levantaron sus armas y decidieron ignorarse lentamente.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": None,
        "chance": 5,
        "damage": 0,
    },
    {
        "mensaje": "💀 Un cadáver fresco aún conservaba algunas pertenencias útiles en sus bolsillos.",
        "overos": (6, 14),
        "item": None,
        "items": [
            {"item": "Venda", "chance": 50, "cantidad": (1, 1)},
            {"item": "Chatarra", "chance": 60, "cantidad": (1, 2)},
        ],
        "effect": None,
        "chance": 6,
        "damage": 0,
    },
    {
        "mensaje": "⚠️ Pisaste un clavo oxidado que atravesó la suela de tu zapato.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": "Cortadura leve",
        "chance": 4,
        "damage": 7,
    },
    {
        "mensaje": "😐 Caminaste en círculos durante horas... no ocurrió absolutamente nada en este sector.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": None,
        "chance": 10,
        "damage": 0,
    },
    # ==========================================
    # 🏥 HOSPITAL
    # ==========================================
    {
        "mensaje": "🏥 Registraste los gabinetes metálicos de la sala de emergencias. Quedaban medicinas.",
        "overos": 0,
        "item": None,
        "items": [
            {"item": "Analgésicos", "chance": 80, "cantidad": (1, 2)},
            {"item": "Alcohol medicinal", "chance": 60, "cantidad": (1, 1)},
        ],
        "effect": None,
        "chance": 20,
        "damage": 0,
        "lugares": ["Hospital"],
    },
    {
        "mensaje": "🏥 Un botiquín colgado en la pared de la sala de trauma seguía completamente sellado.",
        "overos": 0,
        "item": None,
        "items": [
            {"item": "Botiquín", "chance": 100, "cantidad": (1, 1)},
            {"item": "Venda", "chance": 70, "cantidad": (1, 2)},
        ],
        "effect": None,
        "chance": 10,
        "damage": 0,
        "lugares": ["Hospital"],
    },
    {
        "mensaje": "💉 Te pinchaste accidentalmente con una jeringa usada al rebuscar entre los desechos médicos.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": "Infectado",
        "chance": 15,
        "damage": 5,
        "lugares": ["Hospital"],
    },
    # ==========================================
    # 🛒 SUPERMERCADO
    # ==========================================
    {
        "mensaje": "🛒 Aunque las góndolas principales están vacías, encontraste provisiones en el almacén trasero.",
        "overos": 0,
        "item": None,
        "items": [
            {"item": "Comida enlatada", "chance": 90, "cantidad": (1, 3)},
            {"item": "Botella de agua", "chance": 70, "cantidad": (1, 2)},
        ],
        "effect": None,
        "chance": 20,
        "damage": 0,
        "lugares": ["Supermercado"],
    },
    {
        "mensaje": "🛒 Registraste la zona de cajas y cafetería del supermercado.",
        "overos": (10, 25),
        "item": None,
        "items": [
            {"item": "Chocolate", "chance": 60, "cantidad": (1, 2)},
            {"item": "Bebida isotónica", "chance": 50, "cantidad": (1, 1)},
            {"item": "Café instantáneo", "chance": 40, "cantidad": (1, 1)},
        ],
        "effect": None,
        "chance": 15,
        "damage": 0,
        "lugares": ["Supermercado"],
    },
    # ==========================================
    # ⛽ GASOLINERA
    # ==========================================
    {
        "mensaje": "⛽ Lograste drenar el tanque de un camión cisterna abandonado en la parte posterior.",
        "overos": 0,
        "item": None,
        "items": [
            {"item": "Gasolina", "chance": 100, "cantidad": (1, 2)},
            {"item": "Chatarra", "chance": 50, "cantidad": (1, 2)},
        ],
        "effect": None,
        "chance": 20,
        "damage": 0,
        "lugares": ["Gasolinera"],
    },
    {
        "mensaje": "⛽ En los estantes del mostrador de servicio hallaste artículos mecánicos útiles.",
        "overos": (5, 15),
        "item": None,
        "items": [
            {"item": "Pilas", "chance": 70, "cantidad": (1, 2)},
            {"item": "Encendedor", "chance": 50, "cantidad": (1, 1)},
        ],
        "effect": None,
        "chance": 15,
        "damage": 0,
        "lugares": ["Gasolinera"],
    },
    # ==========================================
    # 🌲 BOSQUE
    # ==========================================
    {
        "mensaje": "🌲 Inspeccionaste los restos de un antiguo campamento de cazadores oculto entre la arboleda.",
        "overos": 0,
        "item": None,
        "items": [
            {"item": "Cuerda", "chance": 80, "cantidad": (1, 2)},
            {"item": "Navaja", "chance": 40, "cantidad": (1, 1)},
        ],
        "effect": None,
        "chance": 15,
        "damage": 0,
        "lugares": ["Bosque"],
    },
    {
        "mensaje": "🌲 Te atacó un enjambre de avispas salvajes al golpear sin querer un tronco hueco.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": "Intoxicado",
        "chance": 10,
        "damage": 8,
        "lugares": ["Bosque"],
    },
    # ==========================================
    # 🏫 ESCUELA
    # ==========================================
    {
        "mensaje": "🏫 Entraste al vestuario del gimnasio escolar y forzaste los casilleros metálicos.",
        "overos": 0,
        "item": None,
        "items": [
            {"item": "Bate de béisbol", "chance": 60, "cantidad": (1, 1)},
            {"item": "Chatarra", "chance": 80, "cantidad": (1, 3)},
        ],
        "effect": None,
        "chance": 20,
        "damage": 0,
        "lugares": ["School", "Escuela"],
    },
    {
        "mensaje": "📚 Registraste la vieja biblioteca. Todo estaba destrozado, pero en la enfermería cercana quedaba algo.",
        "overos": (4, 12),
        "item": None,
        "items": [
            {"item": "Venda", "chance": 70, "cantidad": (1, 1)},
            {"item": "Barra energética", "chance": 50, "cantidad": (1, 2)},
        ],
        "effect": None,
        "chance": 15,
        "damage": 0,
        "lugares": ["School", "Escuela"],
    },
    # ==========================================
    # 🏦 BANCO
    # ==========================================
    {
        "mensaje": "🏦 Conseguiste abrir un compartimiento dañado de las cajas de seguridad del mostrador.",
        "overos": (40, 90),  # Gran cantidad de Overos por ser un banco
        "item": None,
        "items": [{"item": "Llave oxidada", "chance": 30, "cantidad": (1, 1)}],
        "effect": None,
        "chance": 15,
        "damage": 0,
        "lugares": ["Banco"],
    },
    {
        "mensaje": "🏦 Una vieja trampa de seguridad de la bóveda se activó, liberando un gas químico punzante.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": "Intoxicado",
        "chance": 12,
        "damage": 12,
        "lugares": ["Banco"],
    },
    # ==========================================
    # 🚓 COMISARÍA
    # ==========================================
    {
        "mensaje": "🚓 Lograste vulnerar la cerradura de la armería del precinto. Estaba casi vacía, pero no del todo.",
        "overos": 0,
        "item": None,
        "items": [
            {"item": "Pistola 9mm", "chance": 40, "cantidad": (1, 1)},
            {"item": "Munición 9mm", "chance": 90, "cantidad": (1, 2)},
        ],
        "effect": None,
        "chance": 15,
        "damage": 0,
        "lugares": ["Comisaría"],
    },
    {
        "mensaje": "🚓 Revisaste el maletero de una patrulla destruida en el estacionamiento policial.",
        "overos": (10, 20),
        "item": None,
        "items": [
            {"item": "Navaja", "chance": 50, "cantidad": (1, 1)},
            {"item": "Pilas", "chance": 60, "cantidad": (1, 2)},
            {"item": "Chatarra", "chance": 70, "cantidad": (2, 4)},
        ],
        "effect": None,
        "chance": 20,
        "damage": 0,
        "lugares": ["Comisaría"],
    },
    {
        "mensaje": "🚓👖 Exploraste entre los casilleros de los oficiales, y encontraste un traje hecho en jean.",
        "overos": (20, 40),
        "item": None,
        "items": [
            {"item": "Traje de jean", "chance": 60, "cantidad": (1, 1)},
            {"item": "Chatarra", "chance": 25, "cantidad": (1, 1)},
        ],
        "effect": None,
        "chance": 40,
        "damage": 0,
        "lugares": ["Comisaría"],
    },
    # ==========================================
    # 🚇 METRO
    # ==========================================
    {
        "mensaje": "🚇 Inspeccionaste los vagones oscuros atascados en los túneles subterráneos.",
        "overos": (5, 15),
        "item": None,
        "items": [
            {"item": "Linterna", "chance": 60, "cantidad": (1, 1)},
            {"item": "Pilas", "chance": 70, "cantidad": (1, 1)},
            {"item": "Cuerda", "chance": 50, "cantidad": (1, 1)},
        ],
        "effect": None,
        "chance": 20,
        "damage": 0,
        "lugares": ["Metro"],
    },
    {
        "mensaje": "🚇 Un derrumbe menor en el túnel te arrojó escombros encima mientras avanzabas a ciegas.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": "Sangrando",
        "chance": 15,
        "damage": 10,
        "lugares": ["Metro"],
    },
    # ==========================================
    # 🎖️ REFUGIO MILITAR
    # ==========================================
    {
        "mensaje": "📦 Forzaste un cajón de suministros tácticos dentro del búnker principal.",
        "overos": 0,
        "item": None,
        "items": [
            {"item": "Ración militar", "chance": 90, "cantidad": (1, 2)},
            {"item": "Botiquín", "chance": 40, "cantidad": (1, 1)},
            {"item": "Munición 9mm", "chance": 70, "cantidad": (1, 3)},
        ],
        "effect": None,
        "chance": 20,
        "damage": 0,
        "lugares": ["Refugio militar"],
    },
    {
        "mensaje": "🎖️ Encontraste una caja militar blindada semiabierta.",
        "overos": (20, 40),
        "item": None,
        "items": [
            {"item": "Suero", "chance": 40, "cantidad": (1, 1)},
            {"item": "Cóctel molotov", "chance": 30, "cantidad": (1, 1)},
        ],
        "effect": None,
        "chance": 15,
        "damage": 0,
        "lugares": ["Refugio militar"],
    },
    {
        "mensaje": "💥 Activaste accidentalmente una mina antipersona defectuosa enterrada en el perímetro.",
        "overos": 0,
        "item": None,
        "items": [],
        "effect": "Herida grave",
        "chance": 10,
        "damage": 18,
        "lugares": ["Refugio militar"],
    },
]
