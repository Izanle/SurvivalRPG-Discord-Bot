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
                "items": [
                    {"item": "Venda", "cantidad": 2},
                    {"item": "Alcohol medicinal", "cantidad": 1},
                ],
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
                "items": [],
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
                "items": [],
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
    },
    "Comisaría": {
        "titulo": "🚓 Incursión: Comisaría de Policía",
        "color": 0x1E90FF,
        "nodos": {
            "inicio": {
                "descripcion": "Entras al vestíbulo de la comisaría. Los cristales blindados están destrozados. Hay sangre seca en el mostrador. Ves unas escaleras hacia las celdas, una puerta hacia las oficinas, y al fondo, la puerta de acero de la armería.",
                "opciones": [
                    {
                        "label": "Revisar oficinas",
                        "siguiente_azar": [
                            {"nodo": "oficinas_loot", "probabilidad": 60},
                            {"nodo": "oficinas_trampa", "probabilidad": 40},
                        ],
                        "emoji": "🗄️",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Bajar a las celdas",
                        "siguiente": "celdas",
                        "emoji": "⛓️",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Abrir Armería",
                        "siguiente": "armeria",
                        "emoji": "🗝️",
                        "requiere_item": "Llave oxidada",  # Requiere llave!
                        "un_solo_uso": True,
                    },
                    {"label": "Salir a la calle", "siguiente": "salir", "emoji": "🏃"},
                ],
            },
            "oficinas_loot": {
                "descripcion": "Rebuscas entre los escritorios de los detectives. Encuentras algunas cosas útiles confiscadas.",
                "loot": {"item": "Chatarra", "cantidad": 3},
                "overos": (15, 30),
                "opciones": [
                    {
                        "label": "Volver al vestíbulo",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "oficinas_trampa": {
                "descripcion": "¡Cuidado! Un Saqueador estaba escondido debajo de un escritorio y te embosca.",
                "damage": 5,
                "tipo": "combate",
                "enemigo": "Saqueador",
                "siguiente_exito": "inicio",
                "siguiente_huida": "inicio",
            },
            "celdas": {
                "descripcion": "El hedor aquí abajo es insoportable. Las puertas de las celdas están abiertas, pero encuentras el alijo secreto de un prisionero.",
                "items": [],
                "opciones": [
                    {
                        "label": "Subir al vestíbulo",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                        "un_solo_uso": True,
                    }
                ],
            },
            "armeria": {
                "descripcion": "¡La llave gira con un crujido! Entras a la armería. La mayoría de las armas se las llevaron, pero logras rescatar equipamiento de primera.",
                "items": [],
                "overos": (50, 100),
                "opciones": [
                    {
                        "label": "Salir al vestíbulo",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                        "un_solo_uso": True,
                    }
                ],
            },
            "salir": {
                "tipo": "fin",
                "descripcion": "El eco de tus propios pasos te pone los nervios de punta. Decides salir de la comisaría con vida.",
            },
        },
    },
    "Bosque": {
        "titulo": "🌲 Incursión: Bosque Oscuro",
        "color": 0x228B22,  # Verde bosque
        "nodos": {
            "inicio": {
                "descripcion": "Los árboles son tan altos que apenas dejan pasar la luz. El viento aúlla entre las ramas. Frente a ti ves un sendero cubierto de maleza, una vieja cabaña de guardabosques y los restos de lo que parece un campamento abandonado.",
                "opciones": [
                    {
                        "label": "Revisar campamento",
                        "siguiente_azar": [
                            {"nodo": "campamento_loot", "probabilidad": 70},
                            {"nodo": "campamento_trampa", "probabilidad": 30},
                        ],
                        "emoji": "⛺",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Entrar a la cabaña",
                        "siguiente": "cabana",
                        "emoji": "🛖",
                        "requiere_item": "Llave oxidada",  # Alguien cerró esto por una buena razón
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Explorar el sendero",
                        "siguiente": "sendero",
                        "emoji": "🛤️",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Volver a la ciudad",
                        "siguiente": "salir",
                        "emoji": "🏃",
                    },
                ],
            },
            "campamento_loot": {
                "descripcion": "Encuentras una mochila semienterrada bajo las hojas secas. ¡Alguien dejó provisiones antes de huir!",
                "items": [],
                "overos": (10, 20),
                "opciones": [
                    {"label": "Volver al claro", "siguiente": "inicio", "emoji": "🔙"}
                ],
            },
            "campamento_trampa": {
                "descripcion": "¡CRAC! Al acercarte a las tiendas, pisas una trampa para osos escondida en la maleza. El grito de dolor atrae a las criaturas del bosque...",
                "damage": 15,  # Trampa dolorosa
                "tipo": "combate",
                "enemigo": "Rata Mutante",  # Puedes cambiarlo a un Lobo u otro monstruo del bosque después
                "siguiente_exito": "inicio",
                "siguiente_huida": "inicio",
            },
            "cabana": {
                "descripcion": "Fuerzas la cerradura oxidada y entras. Adentro hay polvo, huesos y... ¡un alijo médico de supervivencia intacto!",
                "items": [],
                "overos": (30, 60),
                "opciones": [
                    {
                        "label": "Salir de la cabaña",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "sendero": {
                "descripcion": "Caminas por el sendero apartando ramas. Al final llegas a un arroyo seco y encuentras materiales útiles esparcidos en el barro.",
                "items": [],
                "opciones": [
                    {
                        "label": "Regresar al inicio",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "salir": {
                "tipo": "fin",
                "descripcion": "Sientes que algo te observa desde la espesura. Decides que es suficiente naturaleza por hoy y regresas a un lugar seguro.",
            },
        },
    },
    "Supermercado": {
        "titulo": "🛒 Incursión: Súper 'El Ofertas'",
        "color": 0xF39C12,  # Naranja/Amarillo
        "nodos": {
            "inicio": {
                "descripcion": "El aire está viciado y huele a podrido. Las estanterías están volcadas formando laberintos en la penumbra. Al fondo ves la oscura sección de congelados y una pesada puerta metálica que dice 'Solo Personal'.",
                "opciones": [
                    {
                        "label": "Revisar estanterías",
                        "siguiente_azar": [
                            {"nodo": "estanterias_loot", "probabilidad": 60},
                            {"nodo": "estanterias_trampa", "probabilidad": 40},
                        ],
                        "emoji": "🥫",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Abrir Almacén",
                        "siguiente": "almacen",
                        "emoji": "🔐",
                        "requiere_item": "Llave oxidada",  # ¡Premio gordo con llave!
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Explorar congelados",
                        "siguiente": "congelados",
                        "emoji": "❄️",
                        "un_solo_uso": True,
                    },
                    {"label": "Salir a la calle", "siguiente": "salir", "emoji": "🏃"},
                ],
            },
            "estanterias_loot": {
                "descripcion": "Rebuscas entre cajas vacías y basura. ¡Bingo! Encuentras provisiones que los primeros saqueadores pasaron por alto.",
                "items": [],
                "overos": (10, 20),
                "opciones": [
                    {
                        "label": "Volver a los pasillos",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "estanterias_trampa": {
                "descripcion": "¡CRASH! Al mover unas cajas, una montaña de carritos oxidados se derrumba haciendo un ruido ensordecedor... ¡Un Infectado hambriento sale de las sombras!",
                "tipo": "combate",
                "enemigo": "Infectado",
                "siguiente_exito": "inicio",
                "siguiente_huida": "inicio",
            },
            "almacen": {
                "descripcion": "Fuerzas la cerradura y la puerta cede. Adentro está casi intacto. Tomas todo lo que puedes cargar antes de que el olor te maree.",
                "items": [],
                "overos": (30, 80),
                "opciones": [
                    {
                        "label": "Salir de vuelta al pasillo",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "congelados": {
                "descripcion": "Entras a la sección de congeladores. Está oscuro y el suelo cubierto de un líquido viscoso. ¡Te resbalas y golpeas duro contra el cristal roto! Al menos encuentras algo de chatarra tirada.",
                "damage": 10,  # Daño por resbalón
                "items": [],
                "opciones": [
                    {
                        "label": "Levantarse y volver",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "salir": {
                "tipo": "fin",
                "descripcion": "El silencio absoluto de este lugar te está volviendo loco. Tomas tus cosas y sales rápidamente por las puertas automáticas rotas.",
            },
        },
    },
    "Metro": {
        "titulo": "🚇 Incursión: Metro Subterráneo",
        "color": 0x4B0082,  # Índigo oscuro / Morado
        "nodos": {
            "inicio": {
                "descripcion": "Desciendes por unas escaleras mecánicas detenidas. La oscuridad es casi total y el aire es gélido. Ves una vieja taquilla destrozada, una puerta de mantenimiento de acero, y la entrada a los túneles oscuros de las vías.",
                "opciones": [
                    {
                        "label": "Revisar la taquilla",
                        "siguiente": "taquilla",
                        "emoji": "🎫",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Abrir Cuarto de Mantenimiento",
                        "siguiente": "mantenimiento",
                        "emoji": "🔧",
                        "requiere_item": "Llave oxidada",  # Otro buen uso para la llave
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Adentrarse en los túneles",
                        "siguiente_azar": [
                            {
                                "nodo": "tuneles_loot",
                                "probabilidad": 40,
                            },  # 40% de éxito
                            {
                                "nodo": "tuneles_trampa",
                                "probabilidad": 60,
                            },  # 60% de peligro... ¡es el Metro!
                        ],
                        "emoji": "🚇",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Huir a la superficie",
                        "siguiente": "salir",
                        "emoji": "🏃",
                    },
                ],
            },
            "taquilla": {
                "descripcion": "Fuerzas la puerta de la taquilla con cuidado. Adentro encuentras chatarra esparcida y algunos suministros básicos olvidados.",
                "items": [],
                "overos": (15, 30),
                "opciones": [
                    {"label": "Volver al andén", "siguiente": "inicio", "emoji": "🔙"}
                ],
            },
            "mantenimiento": {
                "descripcion": "La llave gira con un fuerte chirrido. El cuarto está lleno de herramientas pesadas y suministros de emergencia. ¡Valió la pena!",
                "items": [],
                "overos": (40, 80),
                "opciones": [
                    {"label": "Volver al andén", "siguiente": "inicio", "emoji": "🔙"}
                ],
            },
            "tuneles_loot": {
                "descripcion": "Caminas a oscuras por las vías iluminando con tu linterna. Tropiezas con el cadáver de un explorador... parece que ya no necesitaba sus medicinas.",
                "items": [],
                "opciones": [
                    {
                        "label": "Regresar rápidamente",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "tuneles_trampa": {
                "descripcion": "¡Mala idea! En la oscuridad de los túneles pisas un charco de líquido tóxico y el ruido atrae a un enjambre de ojos brillantes... ¡Una bestia te ataca!",
                "damage": 10,  # Daño por toxicidad antes de pelear
                "tipo": "combate",
                "enemigo": "Rata Mutante",  # Los túneles son el hogar perfecto para las ratas
                "siguiente_exito": "inicio",
                "siguiente_huida": "inicio",
            },
            "salir": {
                "tipo": "fin",
                "descripcion": "La claustrofobia y el sonido del goteo incesante te vencen. Subes corriendo las escaleras hacia la bendita luz del día.",
            },
        },
    },
    "Gasolinera": {
        "titulo": "⛽ Incursión: Gasolinera Abandonada",
        "color": 0xE74C3C,  # Rojo/Anaranjado combustible
        "nodos": {
            "inicio": {
                "descripcion": "Las bombas de combustible están quemadas y oxidadas. Ves la pequeña tienda de conveniencia con cristales rotos, el tanque subterráneo destapado, y la oficina del gerente al fondo con una puerta reforzada.",
                "opciones": [
                    {
                        "label": "Registrar la tienda",
                        "siguiente_azar": [
                            {"nodo": "tienda_loot", "probabilidad": 70},
                            {"nodo": "tienda_trampa", "probabilidad": 30},
                        ],
                        "emoji": "🏪",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Abrir Oficina del Gerente",
                        "siguiente": "oficina",
                        "emoji": "🗝️",
                        "requiere_item": "Llave oxidada",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Inspeccionar depósitos",
                        "siguiente": "depositos",
                        "emoji": "🛢️",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Volver a la carretera",
                        "siguiente": "salir",
                        "emoji": "🏃",
                    },
                ],
            },
            "tienda_loot": {
                "descripcion": "Entre estantes caídos e insectos, encuentras materiales químicos y provisiones básicas.",
                "items": [
                    {"item": "Comida enlatada", "cantidad": 1},
                    {"item": "Chatarra", "cantidad": 2},
                ],
                "overos": (10, 25),
                "opciones": [
                    {
                        "label": "Volver a las bombas",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "tienda_trampa": {
                "descripcion": "¡Un Saqueador estaba usando la tienda de refugio! Te apunta directo al pecho al verte entrar.",
                "tipo": "combate",
                "enemigo": "Saqueador",
                "siguiente_exito": "inicio",
                "siguiente_huida": "inicio",
            },
            "oficina": {
                "descripcion": "Usas la llave para abrir la oficina. Encuentras alcohol de alto grado y componentes para fabricar explosivos de fortuna.",
                "items": [
                    {"item": "Alcohol medicinal", "cantidad": 2},
                    {"item": "Cóctel molotov", "cantidad": 1},
                ],
                "overos": (40, 80),
                "opciones": [
                    {
                        "label": "Salir a las bombas",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "depositos": {
                "descripcion": "Sifoneas con cuidado los restos de combustible del tanque subterráneo. Consigues bastante chatarra metálica y piezas útiles.",
                "items": [{"item": "Chatarra", "cantidad": 4}],
                "overos": (15, 30),
                "opciones": [
                    {
                        "label": "Regresar al frente",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "salir": {
                "tipo": "fin",
                "descripcion": "El olor a gasolina es sofocante e inflamable. Decides alejarte antes de que una chispa cause un desastre.",
            },
        },
    },
    "Escuela": {
        "titulo": "🏫 Incursión: Escuela Secundaria Abandonada",
        "color": 0xF1C40F,  # Amarillo autobús escolar
        "nodos": {
            "inicio": {
                "descripcion": "Los pasillos están llenos de pupitres rotos y casilleros oxidados. En las paredes hay dibujos espeluznantes. Ves la entrada a la cafetería, una fila de casilleros entreabiertos y la puerta de la enfermería al fondo.",
                "opciones": [
                    {
                        "label": "Revisar casilleros",
                        "siguiente_azar": [
                            {"nodo": "casilleros_loot", "probabilidad": 60},
                            {"nodo": "casilleros_trampa", "probabilidad": 40},
                        ],
                        "emoji": "🎒",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Entrar a la Cafetería",
                        "siguiente": "cafeteria",
                        "emoji": "🍕",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Abrir Enfermería",
                        "siguiente": "enfermeria",
                        "emoji": "⚕️",
                        "requiere_item": "Llave oxidada",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Huir por la ventana",
                        "siguiente": "salir",
                        "emoji": "🏃",
                    },
                ],
            },
            "casilleros_loot": {
                "descripcion": "Fuerzas un par de casilleros atascados. La mayoría tiene libros podridos, pero encuentras algunas cosas útiles escondidas por los estudiantes.",
                "items": [{"item": "Chatarra", "cantidad": 3}],
                "overos": (10, 20),
                "opciones": [
                    {"label": "Volver al pasillo", "siguiente": "inicio", "emoji": "🔙"}
                ],
            },
            "casilleros_trampa": {
                "descripcion": "¡Al intentar abrir un casillero trabado, un enjambre de ratas mutantes salta directo a tu cara!",
                "tipo": "combate",
                "enemigo": "Rata Mutante",
                "siguiente_exito": "inicio",
                "siguiente_huida": "inicio",
            },
            "cafeteria": {
                "descripcion": "El olor en la cafetería es insoportable. Sin embargo, en la despensa trasera de la cocina encuentras algunas latas que sobrevivieron al saqueo.",
                "items": [{"item": "Comida enlatada", "cantidad": 2}],
                "overos": (5, 15),
                "opciones": [
                    {"label": "Volver al pasillo", "siguiente": "inicio", "emoji": "🔙"}
                ],
            },
            "enfermeria": {
                "descripcion": "La llave abre la puerta de la enfermería. Adentro todo está curiosamente intacto. Alguien se atrincheró aquí y dejó atrás un valioso alijo médico.",
                "items": [
                    {"item": "Venda", "cantidad": 2},
                    {"item": "Analgésicos", "cantidad": 1},
                ],
                "overos": (20, 50),
                "opciones": [
                    {"label": "Volver al pasillo", "siguiente": "inicio", "emoji": "🔙"}
                ],
            },
            "salir": {
                "tipo": "fin",
                "descripcion": "Los ecos de risas infantiles que parecen venir de las aulas vacías te ponen la piel de gallina. Decides saltar por una ventana rota y alejarte de ahí.",
            },
        },
    },
    "Banco": {
        "titulo": "🏦 Incursión: Banco Central Abandonado",
        "color": 0x2ECC71,  # Verde dinero
        "nodos": {
            "inicio": {
                "descripcion": "El vestíbulo principal está cubierto de vidrios blindados rotos y fajos de billetes inútiles esparcidos por el suelo. Ves los mostradores de atención al cliente, unas oficinas ejecutivas al fondo y la imponente puerta circular de acero de la bóveda principal.",
                "opciones": [
                    {
                        "label": "Revisar mostradores",
                        "siguiente_azar": [
                            {"nodo": "mostradores_loot", "probabilidad": 60},
                            {"nodo": "mostradores_trampa", "probabilidad": 40},
                        ],
                        "emoji": "💵",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Explorar oficinas",
                        "siguiente": "oficinas",
                        "emoji": "🗄️",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Forzar Bóveda Principal",
                        "siguiente": "boveda",
                        "emoji": "🔐",
                        "requiere_item": "Llave oxidada",  # O la tarjeta/llave que prefieras
                        "un_solo_uso": True,
                    },
                    {"label": "Salir al exterior", "siguiente": "salir", "emoji": "🏃"},
                ],
            },
            "mostradores_loot": {
                "descripcion": "Consigues pasar al otro lado de las ventanillas blindadas y rebuscas entre las cajas registradoras. ¡Encuentras una bolsa con bastantes Overos y piezas esparcidas!",
                "items": [],
                "overos": (30, 70),
                "opciones": [
                    {
                        "label": "Volver al vestíbulo",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "mostradores_trampa": {
                "descripcion": "¡El sistema de seguridad de los mostradores aún conservaba energía! Al intentar abrir un cajón, salta un chispazo eléctrico que te sacude con fuerza.",
                "damage": 12,
                "items": [],
                "opciones": [
                    {
                        "label": "Recuperarte y volver",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "oficinas": {
                "descripcion": "Revisas los escritorios de los gerentes y altos directivos. Encuentras algunos objetos de valor personal que dejaron olvidados.",
                "items": [],
                "overos": (20, 50),
                "opciones": [
                    {
                        "label": "Volver al vestíbulo",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "boveda": {
                "descripcion": "Haces girar los pesados pernos blindados y la enorme puerta de la bóveda cede lentamente. ¡Adentro ha permanecido intacto durante años!",
                "items": [],
                "overos": (100, 250),  # ¡El granbotín de Overos!
                "opciones": [
                    {
                        "label": "Salir al vestíbulo",
                        "siguiente": "inicio",
                        "emoji": "🔙",
                    }
                ],
            },
            "salir": {
                "tipo": "fin",
                "descripcion": "Escuchas ecos metálicos resonando en las tuberías del edificio. Aseguras tus pertenencias y sales rápidamente antes de atraer a extraños.",
            },
        },
    },
    "Refugio militar": {
        "titulo": "🎖️ Incursión: Búnker Militar Alpha",
        "color": 0x4B5320,  # Verde militar oscuro
        "nodos": {
            "inicio": {
                "descripcion": "Atraviesas las pesadas puertas blindadas destrozadas. El interior es un laberinto de hormigón y acero. Las luces rojas de emergencia parpadean. Ves los barracones de los soldados a la izquierda, la sala de control de seguridad arriba, y una enorme compuerta táctica al fondo.",
                "opciones": [
                    {
                        "label": "Revisar barracones",
                        "siguiente_azar": [
                            {"nodo": "barracones_loot", "probabilidad": 50},
                            {
                                "nodo": "barracones_trampa",
                                "probabilidad": 50,
                            },  # ¡50% de peligro! Es zona de alto nivel
                        ],
                        "emoji": "🛏️",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Sala de seguridad",
                        "siguiente": "seguridad",
                        "emoji": "🖥️",
                        "un_solo_uso": True,
                    },
                    {
                        "label": "Abrir Compuerta Táctica",
                        "siguiente": "armeria_pesada",
                        "emoji": "☢️",
                        "requiere_item": "Llave oxidada",  # O "Tarjeta militar" cuando crees el objeto
                        "un_solo_uso": True,
                    },
                    {"label": "Evacuar la zona", "siguiente": "salir", "emoji": "🏃"},
                ],
            },
            "barracones_loot": {
                "descripcion": "Rebuscas entre las literas y taquillas militares. ¡Encuentras equipo de supervivencia de alta calidad!",
                "items": [],
                "overos": (40, 80),
                "opciones": [
                    {"label": "Volver al pasillo", "siguiente": "inicio", "emoji": "🔙"}
                ],
            },
            "barracones_trampa": {
                "descripcion": "¡Cuidado! Un sistema defensivo automatizado seguía activo. Una torreta estropeada te dispara y el ruido atrae a enemigos.",
                "damage": 20,  # Mucho daño
                "tipo": "combate",
                "enemigo": "Saqueador",  # Puedes cambiarlo a un enemigo más fuerte después
                "siguiente_exito": "inicio",
                "siguiente_huida": "inicio",
            },
            "seguridad": {
                "descripcion": "Logras entrar a la sala de control. Descargas datos de los servidores e interceptas algunos recursos confidenciales escondidos bajo las mesas.",
                "items": [],
                "overos": (30, 60),
                "opciones": [
                    {"label": "Bajar al pasillo", "siguiente": "inicio", "emoji": "🔙"}
                ],
            },
            "armeria_pesada": {
                "descripcion": "Los mecanismos hidráulicos de la compuerta se abren. El arsenal principal fue saqueado, pero los remanentes son un tesoro absoluto.",
                "items": [],
                "overos": (150, 400),  # El botín más alto del juego
                "opciones": [
                    {"label": "Volver al pasillo", "siguiente": "inicio", "emoji": "🔙"}
                ],
            },
            "salir": {
                "tipo": "fin",
                "descripcion": "El contador Geiger de tu reloj empieza a pitar débilmente. Las alarmas silenciosas y la tensión te superan. Decides evacuar de inmediato hacia la superficie.",
            },
        },
    },
}
