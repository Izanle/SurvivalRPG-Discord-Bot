import random
import hashlib
from config.quests import QUESTS
from data.database import get_connection
from datetime import datetime, timedelta
from config.effects import SURVIVOR_EFFECTS
from config.items import ITEMS
from config.recipes import RECIPES
from config.shop import SHOP_ITEMS, CATEGORIAS_NO_VENDIBLES, PORCENTAJE_VENTA
from config.shelter import SHELTER_LEVELS


# función principal que muestra el effect del superviviente normal
def get_or_create_survivor(discord_id, name):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM survivors WHERE discord_id = ?", (discord_id,))

    survivor = cursor.fetchone()

    if survivor:
        cursor.execute(
            """
            UPDATE survivors
            SET name = ?
            WHERE discord_id = ?
            """,
            (name, discord_id),
        )

    else:
        cursor.execute(
            """
            INSERT INTO survivors (discord_id, name)
            VALUES (?, ?)
            """,
            (discord_id, name),
        )

    connection.commit()

    cursor.execute("SELECT * FROM survivors WHERE discord_id = ?", (discord_id,))

    survivor = cursor.fetchone()

    connection.close()

    return survivor


# Comprueba si el usuario ya tiene un perfil creado.
def has_survivor(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM survivors
        WHERE discord_id = ?
        """,
        (discord_id,),
    )

    exists = cursor.fetchone() is not None

    connection.close()

    return exists


# Cambia el effect de un superviviente usando su ID de Discord.
def update_status(discord_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE survivors
        SET status = ?
        WHERE discord_id = ?
        """,
        (status, discord_id),
    )

    connection.commit()
    connection.close()


# Agrega Overos a un superviviente.
def add_overos(discord_id, amount):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE survivors
        SET overos = overos + ?
        WHERE discord_id = ?
        """,
        (amount, discord_id),
    )

    connection.commit()
    connection.close()


# Añade un efecto al superviviente.
def add_effect(discord_id, effect):
    connection = get_connection()
    cursor = connection.cursor()

    # Buscamos el ID interno del superviviente.
    cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))

    survivor = cursor.fetchone()

    if survivor is None:
        connection.close()
        return

    effect_data = SURVIVOR_EFFECTS.get(effect)

    if effect_data is None:
        connection.close()
        return

    cursor.execute(
        """
        SELECT effect
        FROM survivor_effects
        WHERE survivor_id = ?
        """,
        (survivor["id"],),
    )

    current_effects = cursor.fetchall()

    for current in current_effects:

        current_data = SURVIVOR_EFFECTS.get(current["effect"])

        if current_data is None:
            continue

        # Si es el mismo tipo de efecto, permitimos reemplazarlo
        # solo si el nuevo es más grave.
        if current_data["tipo"] == effect_data["tipo"]:

            if effect_data["gravedad"] > current_data["gravedad"]:

                cursor.execute(
                    """
                    DELETE FROM survivor_effects
                    WHERE survivor_id = ?
                    AND effect = ?
                    """,
                    (survivor["id"], current["effect"]),
                )

                break

            else:
                connection.close()
                return

    # Evitamos duplicar el mismo efecto.
    cursor.execute(
        """
        SELECT *
        FROM survivor_effects
        WHERE survivor_id = ?
        AND effect = ?
        """,
        (survivor["id"], effect),
    )

    if cursor.fetchone() is None:
        cursor.execute(
            """
            INSERT INTO survivor_effects
            (survivor_id, effect, created_at, progress)
            VALUES (?, ?, ?, ?)
            """,
            (
                survivor["id"],
                effect,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                0,
            ),
        )

    connection.commit()
    connection.close()


# Elimina un efecto del superviviente.
def remove_effect(discord_id, effect):
    connection = get_connection()
    cursor = connection.cursor()

    # Buscamos el ID interno del superviviente.
    cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))

    survivor = cursor.fetchone()

    if survivor is None:
        connection.close()
        return

    # Eliminamos el efecto.
    cursor.execute(
        """
        DELETE FROM survivor_effects
        WHERE survivor_id = ?
        AND effect = ?
        """,
        (survivor["id"], effect),
    )

    connection.commit()
    connection.close()


# Devuelve todos los efectos del superviviente.
def get_effects(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    # Buscamos el ID interno del superviviente.
    cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))

    survivor = cursor.fetchone()

    if survivor is None:
        connection.close()
        return []

    # Obtenemos todos los efectos.
    cursor.execute(
        """
        SELECT effect, progress
        FROM survivor_effects
        WHERE survivor_id = ?
        """,
        (survivor["id"],),
    )

    effects = cursor.fetchall()

    connection.close()

    return effects


# Guarda la fecha y hora de la última exploración.
def update_last_explore(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    # Guardamos la fecha y hora actual.
    cursor.execute(
        """
        UPDATE survivors
        SET last_explore = ?
        WHERE discord_id = ?
        """,
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), discord_id),
    )

    connection.commit()
    connection.close()


# Obtiene la última exploración del superviviente.
def get_last_explore(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT last_explore
        FROM survivors
        WHERE discord_id = ?
        """,
        (discord_id,),
    )

    result = cursor.fetchone()

    connection.close()

    if result:
        return result["last_explore"]

    return None


# Revisa si algún efecto debe evolucionar.
def check_effects(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    # Buscamos los efectos actuales del jugador.
    cursor.execute(
        """
        SELECT id, effect, created_at
        FROM survivor_effects
        WHERE survivor_id = (
            SELECT id
            FROM survivors
            WHERE discord_id = ?
        )
        """,
        (discord_id,),
    )

    effects = cursor.fetchall()

    for effect in effects:

        data = SURVIVOR_EFFECTS.get(effect["effect"])

        if data is None:
            continue

        # Aquí después compararemos el tiempo.
        print("Revisando efecto:", effect["effect"])

    connection.close()


# Aumenta el progreso de todos los efectos del superviviente.
def increase_effect_progress(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE survivor_effects
        SET progress = progress + 1
        WHERE survivor_id = (
            SELECT id
            FROM survivors
            WHERE discord_id = ?
        )
        """,
        (discord_id,),
    )

    connection.commit()
    connection.close()


# Revisa si los efectos del superviviente deben evolucionar.
def update_effects(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, effect, progress
        FROM survivor_effects
        WHERE survivor_id = (
            SELECT id
            FROM survivors
            WHERE discord_id = ?
        )
        """,
        (discord_id,),
    )

    effects = cursor.fetchall()

    for effect in effects:

        data = SURVIVOR_EFFECTS.get(effect["effect"])

        if data is None:
            continue

        # Si el efecto no evoluciona, lo ignoramos.
        if data["evolucion"] is None:
            continue

        # ¿Ya alcanzó el número de exploraciones?
        if effect["progress"] >= data["exploraciones"]:

            cursor.execute(
                """
                UPDATE survivor_effects
                SET effect = ?, progress = 0
                WHERE id = ?
                """,
                (data["evolucion"], effect["id"]),
            )

    connection.commit()
    connection.close()


# Aplica las consecuencias de los efectos activos.
def apply_effect_damage(discord_id):

    effects = get_effects(discord_id)

    total_damage = 0

    for effect in effects:

        data = SURVIVOR_EFFECTS.get(effect["effect"])

        if data is None:
            continue

        total_damage += data["daño"]

    # Si el jugador tiene analgésicos activos, reducimos el daño
    # periódico causado por los efectos (heridas, enfermedades, etc).
    if total_damage > 0 and has_active_effect(discord_id, "reducir_dolor"):

        total_damage = round(total_damage * 0.5)

        print("💊 Analgésicos activos, daño periódico reducido a:", total_damage)

    if total_damage > 0:

        print("Daño por efectos:", total_damage)

    update_health(discord_id, -total_damage)

    return total_damage


# Vida del jugador
def get_health(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT health
        FROM survivors
        WHERE discord_id = ?
        """,
        (discord_id,),
    )

    result = cursor.fetchone()

    connection.close()

    if result:
        return result["health"]

    return 100


# Función para modificar la vida
def update_health(discord_id, amount):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE survivors
        SET health = MAX(0, MIN(100, health + ?))
        WHERE discord_id = ?
        """,
        (amount, discord_id),
    )

    cursor.execute(
        """
        SELECT health
        FROM survivors
        WHERE discord_id = ?
        """,
        (discord_id,),
    )

    health = cursor.fetchone()["health"]

    if health <= 0:
        cursor.execute(
            """
            UPDATE survivors
            SET status = ?
            WHERE discord_id = ?
            """,
            ("Muerto", discord_id),
        )

    connection.commit()
    connection.close()


# Reiniciar perfil de un usuario
def reset_survivor(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE survivors
        SET
            health = 100,
            overos = 0,
            status = 'Vivo',
            last_explore = NULL
        WHERE discord_id = ?
        """,
        (discord_id,),
    )

    cursor.execute(
        """
        DELETE FROM survivor_effects
        WHERE survivor_id = (
            SELECT id
            FROM survivors
            WHERE discord_id = ?
        )
        """,
        (discord_id,),
    )

    connection.commit()
    connection.close()


# Añade un objeto al inventario del superviviente.
def add_item(discord_id, item, quantity=1):

    # Normalizamos el nombre del objeto.
    for name in ITEMS:
        if name.lower() == item.lower():
            item = name
            break

    # Revisamos si el objeto puede acumularse.
    item_data = ITEMS.get(item)

    if item_data and not item_data.get("acumulable", True):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM survivors
            WHERE discord_id = ?
            """,
            (discord_id,),
        )

        survivor = cursor.fetchone()

        if survivor:

            cursor.execute(
                """
                SELECT quantity
                FROM inventory
                WHERE survivor_id = ?
                AND item = ?
                """,
                (survivor["id"], item),
            )

            existing = cursor.fetchone()

            if existing:

                connection.close()
                return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM survivors
        WHERE discord_id = ?
        """,
        (discord_id,),
    )

    survivor = cursor.fetchone()

    if survivor is None:
        connection.close()
        return

    print("Superviviente:", survivor)

    cursor.execute(
        """
        SELECT quantity
        FROM inventory
        WHERE survivor_id = ?
        AND item = ?
        """,
        (survivor["id"], item),
    )

    existing = cursor.fetchone()

    if existing:

        cursor.execute(
            """
            UPDATE inventory
            SET quantity = quantity + ?
            WHERE survivor_id = ?
            AND item = ?
            """,
            (quantity, survivor["id"], item),
        )

    else:

        cursor.execute(
            """
            INSERT INTO inventory
            (survivor_id, item, quantity)
            VALUES (?, ?, ?)
            """,
            (survivor["id"], item, quantity),
        )

        cursor.execute("""
         SELECT *
        FROM inventory
         """)

        print(cursor.fetchall())

    connection.commit()
    connection.close()


# Obtiene todos los objetos del inventario del superviviente.
def get_inventory(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM survivors
        WHERE discord_id = ?
        """,
        (discord_id,),
    )

    survivor = cursor.fetchone()

    if survivor is None:
        connection.close()
        return []

    cursor.execute(
        """
        SELECT item, quantity
        FROM inventory
        WHERE survivor_id = ?
        """,
        (survivor["id"],),
    )

    inventory = cursor.fetchall()

    connection.close()

    return inventory


# Quita una cantidad de un objeto del inventario.
def remove_item(discord_id, item, quantity=1):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM survivors
        WHERE discord_id = ?
        """,
        (discord_id,),
    )

    survivor = cursor.fetchone()

    if survivor is None:
        connection.close()
        return

    cursor.execute(
        """
        SELECT quantity
        FROM inventory
        WHERE survivor_id = ?
        AND item = ?
        """,
        (survivor["id"], item),
    )

    existing = cursor.fetchone()

    if existing is None:
        connection.close()
        return

    new_quantity = existing["quantity"] - quantity

    if new_quantity <= 0:

        cursor.execute(
            """
            DELETE FROM inventory
            WHERE survivor_id = ?
            AND item = ?
            """,
            (survivor["id"], item),
        )

    else:

        cursor.execute(
            """
            UPDATE inventory
            SET quantity = ?
            WHERE survivor_id = ?
            AND item = ?
            """,
            (new_quantity, survivor["id"], item),
        )

    connection.commit()
    connection.close()


# Resuelve un evento que puede tener condiciones según el inventario.
def resolve_event_condition(discord_id, evento):

    condiciones = evento.get("condiciones")

    if not condiciones:
        return evento, None

    for condicion in condiciones:

        item_requerido = condicion.get("item")

        if item_requerido and has_item(discord_id, item_requerido):

            # Partimos del evento base y sobreescribimos solo
            # los campos que la condición especifique.
            resultado = dict(evento)

            for clave, valor in condicion.items():

                if clave in ("item", "consume_item"):
                    continue

                resultado[clave] = valor

            item_consumido = item_requerido if condicion.get("consume_item") else None

            return resultado, item_consumido

    # Ninguna condición se cumplió.
    sin_condicion = evento.get("sin_condicion")

    if sin_condicion:

        resultado = dict(evento)

        for clave, valor in sin_condicion.items():
            resultado[clave] = valor

        return resultado, None

    return evento, None


# Comprueba si el superviviente tiene un objeto.
def has_item(discord_id, item):
    inventory = get_inventory(discord_id)

    for current in inventory:
        if current["item"] == item:
            return True

    return False


def use_item(discord_id, item):

    # Buscamos el objeto ignorando mayúsculas/minúsculas.
    item_name = None

    for name in ITEMS:
        if name.lower() == item.lower():
            item_name = name
            break

    if item_name is None:
        return False, "❌ Ese objeto no existe."

    data = ITEMS[item_name]

    if not data["usable"]:
        return False, "❌ Ese objeto no puede usarse."

    # Verificamos si el jugador tiene el objeto.
    if not has_item(discord_id, item_name):
        return False, f"❌ No tienes ningún {item_name}."

    # Aplicar efectos temporales del objeto.
    if data.get("efecto_uso") and data.get("duracion"):

        add_active_effect(discord_id, data["efecto_uso"], data["duracion"])

    mensajes = []

    usado = False

    # =========================
    # CURAR VIDA
    # =========================

    vida = data.get("vida", 0)

    if vida > 0:

        update_health(discord_id, vida)

        mensajes.append(f"❤️ Recuperaste {vida} puntos de vida.")

        usado = True

    # =========================
    # CURAR ESTADOS
    # =========================

    efectos_curados = []

    efectos = get_effects(discord_id)

    for effect in efectos:

        nombre = effect["effect"]

        if nombre in data.get("cura", []):

            remove_effect(discord_id, nombre)

            efectos_curados.append(nombre)

            usado = True

    if efectos_curados:

        mensajes.append("✨ Estados eliminados: " + ", ".join(efectos_curados))

    # =========================
    # EFECTOS ESPECIALES
    # =========================

    efecto_uso = data.get("efecto_uso")

    if efecto_uso:

        # Aquí después conectaremos
        # el sistema de buffs/debuffs.

        mensajes.append(f"🌟 Efecto aplicado: {efecto_uso}")

        usado = True

    # =========================
    # CONSUMIR OBJETO
    # =========================

    if usado:

        remove_item(discord_id, item_name, 1)

        mensaje_personalizado = data.get("mensaje_uso", f"✅ Has usado {item_name}.")

        return True, (
            f"{data.get('emoji', '📦')} "
            f"{mensaje_personalizado}\n\n" + "\n".join(mensajes)
        )

    return False, (f"❌ No puedes usar {item_name} ahora mismo.")


# Intenta crear un objeto combinando ingredientes del inventario.
def craft_item(discord_id, resultado):

    receta = RECIPES.get(resultado)

    if receta is None:
        return False, "❌ Esa receta no existe."

    inventario = get_inventory(discord_id)

    cantidades = {entrada["item"]: entrada["quantity"] for entrada in inventario}

    faltantes = []

    for ingrediente, cantidad_necesaria in receta["ingredientes"].items():

        disponible = cantidades.get(ingrediente, 0)

        if disponible < cantidad_necesaria:
            faltantes.append(f"{ingrediente} ({disponible}/{cantidad_necesaria})")

    if faltantes:
        return False, "❌ Te faltan materiales: " + ", ".join(faltantes)

    # Consumimos los ingredientes.
    for ingrediente, cantidad_necesaria in receta["ingredientes"].items():
        remove_item(discord_id, ingrediente, cantidad_necesaria)

    # Entregamos el resultado.
    add_item(discord_id, resultado)

    mensaje = receta.get("mensaje", f"✅ Has creado: {resultado}.")

    return True, mensaje


# Consulta rápida de los Overos actuales de un superviviente.
def get_overos(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT overos
        FROM survivors
        WHERE discord_id = ?
        """,
        (discord_id,),
    )

    result = cursor.fetchone()

    connection.close()

    if result:
        return result["overos"]

    return 0


# Compra un objeto de la tienda usando Overos.
def buy_item(discord_id, item, cantidad=1):

    if item not in SHOP_ITEMS:
        return False, "❌ Ese objeto no está disponible en la tienda."

    if cantidad <= 0:
        return False, "❌ La cantidad debe ser mayor a cero."

    data = ITEMS.get(item)

    if data is None:
        return False, "❌ Ese objeto no existe."

    costo_total = data["valor"] * cantidad

    overos_actuales = get_overos(discord_id)

    if overos_actuales < costo_total:
        return False, (
            f"❌ No tienes suficientes Overos. "
            f"Necesitas {costo_total} y tienes {overos_actuales}."
        )

    add_overos(discord_id, -costo_total)
    add_item(discord_id, item, cantidad)

    return True, (
        f"{data.get('emoji', '📦')} Has comprado {item} x{cantidad} "
        f"por **{costo_total} Overos**."
    )


# Vende un objeto del inventario a cambio de Overos.
def sell_item(discord_id, item, cantidad=1):

    # Normalizamos el nombre del objeto.
    item_name = None

    for name in ITEMS:
        if name.lower() == item.lower():
            item_name = name
            break

    if item_name is None:
        return False, "❌ Ese objeto no existe."

    data = ITEMS[item_name]

    if data.get("categoria") in CATEGORIAS_NO_VENDIBLES:
        return False, f"❌ No puedes vender {item_name}."

    if cantidad <= 0:
        return False, "❌ La cantidad debe ser mayor a cero."

    inventario = get_inventory(discord_id)

    cantidades = {entrada["item"]: entrada["quantity"] for entrada in inventario}

    disponible = cantidades.get(item_name, 0)

    if disponible < cantidad:
        return False, (
            f"❌ No tienes suficientes. Tienes {disponible} y "
            f"quieres vender {cantidad}."
        )

    pago = round(data["valor"] * PORCENTAJE_VENTA * cantidad)

    remove_item(discord_id, item_name, cantidad)
    add_overos(discord_id, pago)

    return True, (
        f"{data.get('emoji', '📦')} Has vendido {item_name} x{cantidad} "
        f"por **{pago} Overos**."
    )


# Limpia todo el inventario de un superviviente.
def clear_inventory(discord_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM inventory
        WHERE survivor_id = (
            SELECT id
            FROM survivors
            WHERE discord_id = ?
        )
        """,
        (discord_id,),
    )

    connection.commit()
    connection.close()


# Agregar estados al consumir items
def add_active_effect(discord_id, effect, duration):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM survivors
        WHERE discord_id = ?
        """,
        (discord_id,),
    )

    survivor = cursor.fetchone()

    if survivor is None:
        connection.close()
        return False

    survivor_id = survivor["id"]

    # Revisamos si ya tiene ese efecto
    cursor.execute(
        """
        SELECT id, duration
        FROM active_effects
        WHERE survivor_id = ?
        AND effect = ?
        """,
        (survivor_id, effect),
    )

    existing = cursor.fetchone()

    if existing:

        # Si ya existe, renovamos la duración
        cursor.execute(
            """
            UPDATE active_effects
            SET duration = ?
            WHERE id = ?
            """,
            (duration, existing["id"]),
        )

    else:

        cursor.execute(
            """
            INSERT INTO active_effects
            (survivor_id, effect, duration)
            VALUES (?, ?, ?)
            """,
            (survivor_id, effect, duration),
        )

    connection.commit()
    connection.close()

    return True


# Obtener efectos activos
def get_active_effects(discord_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT active_effects.effect,
               active_effects.duration
        FROM active_effects

        JOIN survivors
        ON survivors.id = active_effects.survivor_id

        WHERE survivors.discord_id = ?
        """,
        (discord_id,),
    )

    effects = cursor.fetchall()

    connection.close()

    return effects


# Consultar si tiene efecto
def has_active_effect(discord_id, effect_name):

    effects = get_active_effects(discord_id)

    for effect in effects:

        if effect["effect"] == effect_name:
            return True

    return False


# Reducir duración
def reduce_active_effects(discord_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT active_effects.id,
               active_effects.duration
        FROM active_effects

        JOIN survivors
        ON survivors.id = active_effects.survivor_id

        WHERE survivors.discord_id = ?
        """,
        (discord_id,),
    )

    effects = cursor.fetchall()

    for effect in effects:

        nueva_duracion = effect["duration"] - 1

        if nueva_duracion <= 0:

            cursor.execute(
                """
                DELETE FROM active_effects
                WHERE id = ?
                """,
                (effect["id"],),
            )

        else:

            cursor.execute(
                """
                UPDATE active_effects
                SET duration = ?
                WHERE id = ?
                """,
                (nueva_duracion, effect["id"]),
            )

    connection.commit()
    connection.close()


# ==========================================
# FUNCIONES DEL REFUGIO (FASE 6)
# ==========================================


# Obtiene el refugio del jugador, o crea uno nivel 1 si no tiene.
def get_or_create_shelter(discord_id):
    connection = get_connection()
    cursor = connection.cursor()

    # Primero, buscamos el ID interno del superviviente
    cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))
    survivor = cursor.fetchone()

    if survivor is None:
        connection.close()
        return None

    survivor_id = survivor["id"]

    # Buscamos su refugio
    cursor.execute("SELECT * FROM shelters WHERE survivor_id = ?", (survivor_id,))
    shelter = cursor.fetchone()

    # Si no tiene refugio, le creamos uno nivel 1 por defecto
    if not shelter:
        cursor.execute(
            "INSERT INTO shelters (survivor_id, level) VALUES (?, 1)", (survivor_id,)
        )
        connection.commit()
        cursor.execute("SELECT * FROM shelters WHERE survivor_id = ?", (survivor_id,))
        shelter = cursor.fetchone()

    connection.close()
    return shelter


# Intenta mejorar el refugio del jugador al siguiente nivel.
def upgrade_shelter(discord_id):
    shelter = get_or_create_shelter(discord_id)
    if not shelter:
        return False, "❌ No tienes un perfil de superviviente."

    nivel_actual = shelter["level"]
    nivel_siguiente = nivel_actual + 1

    # Revisamos si ya alcanzó el nivel máximo
    if nivel_siguiente not in SHELTER_LEVELS:
        return False, "❌ Tu refugio ya está al nivel máximo."

    datos_siguiente = SHELTER_LEVELS[nivel_siguiente]
    overos_requeridos = datos_siguiente["costo_overos"]
    items_requeridos = datos_siguiente["costo_items"]

    # 1. Comprobamos si tiene los Overos necesarios
    if get_overos(discord_id) < overos_requeridos:
        return False, f"❌ Necesitas {overos_requeridos} Overos para mejorar."

    # 2. Comprobamos si tiene los objetos necesarios
    inventario = get_inventory(discord_id)
    cantidades = {item["item"]: item["quantity"] for item in inventario}

    faltantes = []
    for item_req, cant_req in items_requeridos.items():
        if cantidades.get(item_req, 0) < cant_req:
            faltantes.append(f"{item_req} (x{cant_req})")

    if faltantes:
        return False, "❌ Faltan materiales: " + ", ".join(faltantes)

    # 3. Si tiene todo, cobramos los materiales y overos
    add_overos(discord_id, -overos_requeridos)
    for item_req, cant_req in items_requeridos.items():
        remove_item(discord_id, item_req, cant_req)

    # 4. Subimos de nivel el refugio en la base de datos
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE shelters SET level = ? WHERE id = ?", (nivel_siguiente, shelter["id"])
    )
    connection.commit()
    connection.close()

    return True, f"⛺ ¡Refugio mejorado a **{datos_siguiente['nombre']}**!"


# Permite al jugador dormir en el refugio para recuperar salud.
def rest_in_shelter(discord_id):
    shelter = get_or_create_shelter(discord_id)
    if not shelter:
        return False, "❌ No tienes un perfil."

    nivel_actual = shelter["level"]
    datos_refugio = SHELTER_LEVELS[nivel_actual]

    # Comprobamos si ya durmió hace poco (Cooldown)
    if shelter["last_rest"]:
        ultimo_descanso = datetime.strptime(shelter["last_rest"], "%Y-%m-%d %H:%M:%S")

        # ¡CORRECCIÓN AQUÍ! Cambiado 'horas' por 'hours'
        tiempo_necesario = timedelta(hours=datos_refugio["cooldown_horas"])

        if datetime.now() < ultimo_descanso + tiempo_necesario:
            restante = (ultimo_descanso + tiempo_necesario) - datetime.now()
            horas = restante.seconds // 3600
            minutos = (restante.seconds % 3600) // 60
            return (
                False,
                f"⏳ Debes esperar {horas}h {minutos}m para volver a descansar.",
            )

    # Si puede dormir, actualizamos la fecha de último descanso
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE shelters SET last_rest = ? WHERE id = ?",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), shelter["id"]),
    )
    connection.commit()
    connection.close()

    # Curamos al jugador según el nivel del refugio
    cura = datos_refugio["cura_descanso"]
    update_health(discord_id, cura)

    return (
        True,
        f"💤 Descansaste en tu refugio y recuperaste **{cura} puntos de vida**.",
    )


# ==========================================
# SISTEMA DE MISIONES (FASE 9)
# ==========================================


def get_active_quest(discord_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))
    survivor = cursor.fetchone()
    if not survivor:
        return None

    cursor.execute(
        "SELECT * FROM quests WHERE survivor_id = ? AND status = 'activa'",
        (survivor["id"],),
    )
    quest = cursor.fetchone()
    connection.close()
    return quest


def assign_random_quest(discord_id):
    if get_active_quest(discord_id):
        return False, "Ya tienes una misión activa."

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))
    survivor = cursor.fetchone()

    quest_id = random.choice(list(QUESTS.keys()))
    quest_data = QUESTS[quest_id]

    cursor.execute(
        """
        INSERT INTO quests (survivor_id, quest_id, target, progress, required)
        VALUES (?, ?, ?, 0, ?)
    """,
        (survivor["id"], quest_id, quest_data["target"], quest_data["required"]),
    )
    connection.commit()
    connection.close()
    return True, quest_id


def update_quest_progress(discord_id, quest_type, target, amount=1):
    quest = get_active_quest(discord_id)
    if not quest:
        return

    quest_data = QUESTS.get(quest["quest_id"])
    if not quest_data:
        return

    # Comparamos ignorando mayúsculas y espacios por si acaso
    tipo_mision = quest_data["tipo"].strip().lower()
    tipo_accion = quest_type.strip().lower()
    objetivo_mision = quest_data["target"].strip().lower()
    objetivo_accion = target.strip().lower()

    if tipo_mision == tipo_accion and objetivo_mision == objetivo_accion:
        connection = get_connection()
        cursor = connection.cursor()
        nuevo_progreso = min(quest["progress"] + amount, quest["required"])

        cursor.execute(
            """
            UPDATE quests 
            SET progress = ?
            WHERE id = ?
        """,
            (nuevo_progreso, quest["id"]),
        )
        connection.commit()
        connection.close()

        print(f"✅ Progreso de misión guardado: {nuevo_progreso}/{quest['required']}")
    else:
        # Esto aparecerá en tu consola si el jugador hace algo que no es su misión
        print(
            f"Info: Acción ({tipo_accion} - {objetivo_accion}) no coincide con misión ({tipo_mision} - {objetivo_mision})."
        )


def abandon_quest(discord_id):
    quest = get_active_quest(discord_id)
    if not quest:
        return False

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM quests WHERE id = ?", (quest["id"],))
    connection.commit()
    connection.close()
    return True


def claim_quest_reward(discord_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))
    survivor = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM quests WHERE survivor_id = ? AND status = 'activa'",
        (survivor["id"],),
    )
    quest = cursor.fetchone()

    if not quest:
        connection.close()
        return False, "No tienes misiones activas para reclamar."

    quest_data = QUESTS[quest["quest_id"]]

    # Comprobación según el tipo de misión
    if quest_data["tipo"] == "recoleccion":
        inventario = get_inventory(discord_id)
        cantidad_tiene = sum(
            i["quantity"] for i in inventario if i["item"] == quest_data["target"]
        )
        if cantidad_tiene < quest_data["required"]:
            connection.close()
            return (
                False,
                f"❌ No tienes suficientes {quest_data['target']} ({cantidad_tiene}/{quest_data['required']}).",
            )
        remove_item(discord_id, quest_data["target"], quest_data["required"])
    else:
        if quest["progress"] < quest["required"]:
            connection.close()
            return (
                False,
                f"❌ Aún no terminas la misión. Progreso: {quest['progress']}/{quest['required']}.",
            )

    # Si cumplió, damos recompensas y borramos la misión
    add_overos(discord_id, quest_data["recompensa_overos"])
    if quest_data["recompensa_item"]:
        add_item(discord_id, quest_data["recompensa_item"], 1)

    cursor.execute("DELETE FROM quests WHERE id = ?", (quest["id"],))
    connection.commit()
    connection.close()

    msg = f"✅ ¡Misión completada! Has ganado **{quest_data['recompensa_overos']} Overos**"
    if quest_data["recompensa_item"]:
        msg += f" y **{quest_data['recompensa_item']}**."

    # --- LOGROS: Revisamos si completó su logro de misiones ---
    logros_desbloqueados = update_stat(discord_id, "quests_completed")
    for logro in logros_desbloqueados:
        msg += (
            f"\n\n🏆 **¡LOGRO DESBLOQUEADO!** {logro['emoji']} **{logro['nombre']}**\n*{logro['descripcion']}*\n🎁 Recompensa: 🦴 {logro['recompensa_overos']}"
            + (f" y 📦 {logro['recompensa_item']}" if logro["recompensa_item"] else "")
        )

    return True, msg


# ==========================================
# SISTEMA DE LOGROS Y ESTADÍSTICAS (FASE 11)
# ==========================================


def get_or_create_stats(survivor_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM stats WHERE survivor_id = ?", (survivor_id,))
    stats = cursor.fetchone()
    if not stats:
        cursor.execute("INSERT INTO stats (survivor_id) VALUES (?)", (survivor_id,))
        connection.commit()
        cursor.execute("SELECT * FROM stats WHERE survivor_id = ?", (survivor_id,))
        stats = cursor.fetchone()
    connection.close()
    return stats


def check_achievements(discord_id):
    from config.achievements import ACHIEVEMENTS

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))
    survivor = cursor.fetchone()
    if not survivor:
        connection.close()
        return []

    survivor_id = survivor["id"]
    stats = get_or_create_stats(survivor_id)

    cursor.execute(
        "SELECT achievement_id FROM achievements WHERE survivor_id = ?", (survivor_id,)
    )
    unlocked = [row["achievement_id"] for row in cursor.fetchall()]

    new_unlocks = []

    for ach_id, ach_data in ACHIEVEMENTS.items():
        if ach_id in unlocked:
            continue

        req_type = ach_data["requisito"]["tipo"]
        req_amount = ach_data["requisito"]["cantidad"]

        if stats[req_type] >= req_amount:
            cursor.execute(
                "INSERT INTO achievements (survivor_id, achievement_id) VALUES (?, ?)",
                (survivor_id, ach_id),
            )
            cursor.execute(
                "UPDATE survivors SET overos = overos + ? WHERE id = ?",
                (ach_data["recompensa_overos"], survivor_id),
            )
            new_unlocks.append(ach_data)

    connection.commit()
    connection.close()

    # Damos los items de recompensa si los hay
    for ach in new_unlocks:
        if ach["recompensa_item"]:
            add_item(discord_id, ach["recompensa_item"], 1)

    return new_unlocks


def update_stat(discord_id, stat_name, amount=1):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))
    survivor = cursor.fetchone()
    if not survivor:
        connection.close()
        return []

    survivor_id = survivor["id"]
    get_or_create_stats(survivor_id)

    query = f"UPDATE stats SET {stat_name} = {stat_name} + ? WHERE survivor_id = ?"
    cursor.execute(query, (amount, survivor_id))
    connection.commit()
    connection.close()

    return check_achievements(discord_id)


def get_unlocked_achievements(discord_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))
    survivor = cursor.fetchone()
    if not survivor:
        connection.close()
        return []

    cursor.execute(
        "SELECT achievement_id, unlocked_at FROM achievements WHERE survivor_id = ?",
        (survivor["id"],),
    )
    achievements = cursor.fetchall()
    connection.close()
    return achievements


# ==========================================
# SISTEMA DE MUNDO DINÁMICO (FASE 10)
# ==========================================


def get_current_weather():
    from config.world import WEATHER_TYPES

    # Usamos la fecha y la hora actual para crear un clima que cambie cada hora
    # pero que sea exactamente el mismo para todos los jugadores a la vez.
    seed = datetime.now().strftime("%Y-%m-%d-%H")
    hash_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)

    weathers = list(WEATHER_TYPES.keys())
    clima_actual = weathers[hash_val % len(weathers)]

    # Determinamos si es de día o de noche según la hora del servidor
    hora = datetime.now().hour
    es_dia = 6 <= hora < 19  # De 6 AM a 6:59 PM es de día

    return clima_actual, WEATHER_TYPES[clima_actual], es_dia


# ==========================================
# SISTEMA DE NIVELES Y EXPERIENCIA (FASE 12)
# ==========================================


def add_xp(discord_id, cantidad_xp):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, level, xp FROM survivors WHERE discord_id = ?", (discord_id,)
    )
    survivor = cursor.fetchone()

    if not survivor:
        connection.close()
        return None

    s_id, nivel_actual, xp_actual = survivor["id"], survivor["level"], survivor["xp"]

    nueva_xp = xp_actual + cantidad_xp
    # Fórmula de experiencia requerida por nivel: Nivel * 100
    xp_necesaria = nivel_actual * 100

    subio_nivel = False
    nuevo_nivel = nivel_actual

    if nueva_xp >= xp_necesaria:
        nuevo_nivel += 1
        nueva_xp -= xp_necesaria
        subio_nivel = True

    cursor.execute(
        """
        UPDATE survivors 
        SET level = ?, xp = ?
        WHERE id = ?
    """,
        (nuevo_nivel, nueva_xp, s_id),
    )

    connection.commit()
    connection.close()

    if subio_nivel:
        return f"\n\n⭐ **¡Felicidades! Has subido al Nivel {nuevo_nivel}!** 🎉"
    return None


# ==========================================
# SISTEMA DE EQUIPAMIENTO
# ==========================================
# ==========================================
# SISTEMA DE EQUIPAMIENTO
# ==========================================


def get_equipped_gear(discord_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT arma_equipada, armadura_equipada FROM survivors WHERE discord_id = ?",
        (discord_id,),
    )
    gear = cursor.fetchone()
    connection.close()
    if gear:
        return gear["arma_equipada"], gear["armadura_equipada"]
    return None, None


def equip_item(discord_id, item_nombre):
    from config.equipment import EQUIPMENT

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM survivors WHERE discord_id = ?", (discord_id,))
    survivor = cursor.fetchone()

    if not survivor:
        connection.close()
        return False, "❌ No tienes un superviviente registrado."

    # Opción especial para desequipar (quedarse sin nada)
    if item_nombre == "desequipar_arma":
        cursor.execute(
            "UPDATE survivors SET arma_equipada = NULL WHERE id = ?", (survivor["id"],)
        )
        connection.commit()
        connection.close()
        return True, "🗡️ Has guardado tu arma. Ahora peleas con las manos vacías."

    if item_nombre == "desequipar_armadura":
        cursor.execute(
            "UPDATE survivors SET armadura_equipada = NULL WHERE id = ?",
            (survivor["id"],),
        )
        connection.commit()
        connection.close()
        return True, "🛡️ Te has quitado la armadura. Ahora vas sin protección corporal."

    eq_data = EQUIPMENT.get(item_nombre)
    if not eq_data:
        connection.close()
        return False, "❌ Este objeto no es equipable."

    # Verificamos que el jugador tenga el objeto en su inventario
    inv = get_inventory(discord_id)
    tiene_objeto = any(i["item"] == item_nombre and i["quantity"] > 0 for i in inv)
    if not tiene_objeto:
        connection.close()
        return False, "❌ No tienes este objeto en tu inventario."

    tipo = eq_data["tipo"]  # "arma" o "armadura"

    if tipo == "arma":
        cursor.execute(
            "UPDATE survivors SET arma_equipada = ? WHERE id = ?",
            (item_nombre, survivor["id"]),
        )
        msg = f"🗡️ Te has equipado el arma: **{item_nombre}**"
    else:
        cursor.execute(
            "UPDATE survivors SET armadura_equipada = ? WHERE id = ?",
            (item_nombre, survivor["id"]),
        )
        msg = f"🛡️ Te has equipado la protección: **{item_nombre}**"

    connection.commit()
    connection.close()
    return True, msg
