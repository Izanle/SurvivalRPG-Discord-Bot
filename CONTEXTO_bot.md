# Contexto del proyecto

## Proyecto
Bot Discord RPG de supervivencia hecho en Python.

## Estructura

cogs/
- general.py
- survivors.py

config/
- items.py
- effects.py
- events.py
- status.py

data/
- database.py

utils/
- users.py


# Reglas importantes

- No cambiar la estructura de ITEMS.
- Trabajar paso por paso.
- No rehacer sistemas existentes.
- Mantener compatibilidad con código actual.
- La duración de efectos funciona por exploraciones, no tiempo real.


# Sistemas terminados

## Inventario

Funciona con SQLite.

Permite:
- objetos acumulables
- objetos únicos
- cantidades


## ITEMS

Cada objeto tiene:

descripcion
descripcion_larga
tipo
categoria
usable
acumulable
rareza
valor
cura
vida
emoji
efecto_uso
duracion
mensaje_uso
encontrable


## Comandos

/Perfil
- muestra superviviente y estados.

/Explorar
- genera eventos.
- aplica daño.
- entrega objetos.
- aplica efectos.

/Usar
- menú desplegable.
- usa objetos del inventario.

/Objeto
- comando administrativo.
- agrega objetos.
/Reload
- recarga módulos sin reiniciar.


# Punto actual

Se está trabajando en integrar efectos de objetos.

Primer objeto:
☕ Café instantáneo

Tiene:

efecto_uso:
"energia"

duracion:
2 exploraciones


Lógica planeada:

Si el jugador tiene energía:
- 50% de probabilidad de evitar daños pequeños.
- daños mayores siguen ocurriendo.


Código pendiente:

En survivors.py, dentro de /explorar:

Después de seleccionar:

evento = random.choices(
    EVENTS,
    weights=[evento["chance"] for evento in EVENTS],
    k=1
)[0]

se empieza a interpretar efectos activos.


Último paso pendiente:

Encontrar la parte donde:
- se aplica evento["damage"]
- se aplica evento["effect"]
- se envía el mensaje final

para conectar energía.
