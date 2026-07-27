# ☣️ SurvivalRPG Discord Bot

Un bot de supervivencia RPG en texto para Discord desarrollado en **Python** utilizando **discord.py**. Sumérgete en un mundo postapocalíptico desolado, explora zonas peligrosas, gestiona recursos, enfrentate a enemigos y construye tu refugio para sobrevivir.

---

## 🚀 Características Principales

### 👤 1. Perfil de Superviviente
* **Estadísticas Dinámicas:** Gestión de vida (HP), nivel, experiencia (XP), estado de salud (Vivo/Muerto) y moneda del juego (**Overos**).
* **Sistema de Equipo:** Tragaluces dedicados para **Arma** y **Armadura**, afectando directamente al daño causado y a la reducción del daño recibido en combate.
* **Estados y Efectos:** Sistema de infecciones, hemorragias o bonificadores temporales (como analgésicos o analépticos) que evolucionan con el tiempo.

### 🗺️ 2. Exploración Profunda e Incursiones (9 Zonas)
* **Motor Narrativo Interactivo:** Sistema de exploración por nodos interactivos mediante botones en tiempo real.
* **Zonas Temáticas Personalizadas:**
  * 🏥 **Hospital:** Enfocado en botiquines, vendas y suministros médicos.
  * 🛒 **Supermercado:** Alimentos enlatados, agua y recursos básicos.
  * ⛽ **Gasolinera:** Combustibles, trapos y materiales pesados.
  * 🌲 **Bosque:** Madera, hierbas e ingredientes naturales.
  * 🏫 **Escuela:** Materiales de crafteo, mochila y utensilios.
  * 🏛️ **Comisaría:** Armamento policial, municiones y chalecos.
  * 🚇 **Metro:** Túneles subterráneos oscuros con peligro de emboscada.
  * 🏦 **Banco Central:** Bóvedas blindadas con gran botín de Overos y cerraduras.
  * 🎖️ **Refugio Militar:** Zona de alto nivel con torretas defensivas, botín militar y alto riesgo.
* **Mecánicas de Incursión:** Nodos de azar (loot vs. trampas), botones de un solo uso, requerimiento de llaves u objetos específicos para abrir zonas secretas.

### ⚔️ 3. Combate e Incursiones
* **Sistema de Combate en Tiempo Real:** Enfréntate a Saqueadores, Infectados, Torretas y más.
* **Acciones Tácticas:** Atacar con armas equipadas/consumibles, curarse en mitad del combate o intentar huir.
* **Cálculo Realista de Daño:** El daño de ataque se incrementa según el arma equipada, y el daño recibido disminuye con la armadura.

### 🎒 4. Inventario, Crafteo y Economía
* **Inventario Paginado:** Vista interactiva de inventario organizada por páginas con emojis.
* **Sistema de Recetas y Crafteo:** Combina ingredientes del inventario para fabricar vendas, herramientas o equipo avanzado.
* **Mercado y Tienda (Overos):** Sistema de compra y venta de recursos con porcentaje de reventa ajustado.

### ⛺ 5. Refugios (Shelters)
* **Construcción y Mejoras:** Sube de nivel tu refugio usando materiales e Overos.
* **Descanso e Higiene:** Descansa en tu base para recuperar vida con tiempos de espera (cooldowns) basados en el nivel del refugio.

### 📜 6. Misiones, Logros y Clima Dinámico
* **Sistema de Misiones:** Misiones aleatorias de cacería, recolección o exploración con recompensas al completarlas.
* **Logros Desbloqueables:** Sistema de estadísticas globales (enemigos derrotados, zonas exploradas, etc.) que otorgan recompensas únicas.
* **Clima Dinámico:** Ciclo de día/noche y clima sincronizado globalmente que cambia cada hora.

---

## 🛠️ Arquitectura del Proyecto

```text
SurvivalRPG/
├── cogs/                  # Módulos de comandos de Discord (Cogs)
│   ├── admin.py           # Comandos de administración y eventos
│   ├── cntrl.py           # Control e interacciones
│   ├── general.py         # Comandos generales
│   └── survivors.py       # Lógica principal del juego e incursiones
├── config/                # Archivos de configuración y diccionarios de datos
│   ├── achievements.py    # Definición de logros
│   ├── effects.py         # Efectos y estados
│   ├── enemies.py         # Enemigos y estadísticas
│   ├── equipment.py       # Armas y armaduras
│   ├── events.py          # Eventos de exploración
│   ├── incursions.py       # Mapa de nodos para las 9 zonas de incursión
│   ├── items.py           # Objetos e ítems
│   ├── locations.py       # Definición de zonas
│   ├── quests.py          # Sistema de misiones
│   ├── recipes.py         # Recetas de crafteo
│   ├── shelter.py         # Niveles de refugio
│   ├── shop.py            # Artículos de la tienda
│   └── world.py           # Clima y tiempo
├── data/                  # Almacenamiento de base de datos
│   ├── database.py        # Conexión e inicialización de SQLite
│   └── bot.db             # Archivo local de base de datos
├── utils/                 # Funciones auxiliares y consultas a la BD
│   └── users.py           # Gestión de usuarios, inventario y estados
├── .env                   # Variables de entorno (TOKEN de Discord)
├── main.py                # Punto de entrada y carga del bot
└── requirements.txt       # Dependencias de Python
