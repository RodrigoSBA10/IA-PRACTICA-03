# Importa la clase que representa el mundo del Wumpus
from mundo import WumpusWorld

# Importa el agente lógico
from agente import AgenteLogico

# Importa el agente aleatorio
from AgenteAleatorio import AgenteAleatorio

# Importa el agente que usa A*
from agente_astar import AgenteAStar

# Importa las constantes de configuración
from config import *

# Importa las constantes de puntuación
from puntuaciones import *


# Crea una instancia del mundo
mundo = WumpusWorld()

# Selecciona el agente a probar

# Agente basado en lógica e inferencia
agente = AgenteLogico(mundo)

# Agente que se mueve aleatoriamente
# agente = AgenteAleatorio(mundo)

# Agente que utiliza A*
#agente = AgenteAStar(mundo)


# Ciclo principal de la simulación
for turno in range(1, TURNOS_MAXIMOS + 1):

    # Muestra el número de movimiento actual
    print(f"*** MOVIMIENTO {turno} ***")

    # Resta puntos por cada movimiento realizado
    agente.puntuacion += PUNTOS_MOVIMIENTO

    # Verifica si en este turno deben moverse los Wumpus
    if turno % FRECUENCIA_MOVIMIENTO_WUMPUS == 0:

        # Mueve los Wumpus dentro del mundo
        mundo.mover_wumpus()

        # Si el agente lógico tiene posibles posiciones de Wumpus, las limpia
        if hasattr(agente, "posible_wumpus"):
            agente.posibles_wumpus.clear()

        # Si otro agente usa posibles posiciones de Wumpus, también las limpia
        if hasattr(agente, "posibles_wumpus"):
            agente.posibles_wumpus.clear()

        # Si el agente tiene base de conocimiento
        if hasattr(agente, "kb"):

            # Recorre todas las posiciones de la base de conocimiento
            for pos in agente.kb:

                # Si alguna posición estaba marcada como posible Wumpus
                if agente.kb[pos]["p_wumpus"] == "p":

                    # La regresa a desconocida porque el Wumpus se movió
                    agente.kb[pos]["p_wumpus"] = "u"

        # Informa que los Wumpus cambiaron de posición
        print("Los Wumpus se han movido...")

    # Verifica si en este turno debe aparecer un pozo nuevo
    if turno % FRECUENCIA_NUEVO_POZO == 0:

        # Agrega un pozo aleatorio, evitando la posición actual del agente
        nuevo_pozo = mundo.agregar_pozo_aleatorio(agente.pos_actual)

        # Si realmente se creó un pozo nuevo
        if nuevo_pozo:

            # Si el agente maneja un conjunto de peligros
            if hasattr(agente, "peligros"):

                # Agrega el nuevo pozo como peligro conocido
                agente.peligros.add(nuevo_pozo)

            # Si el agente maneja casillas seguras
            if hasattr(agente, "seguras"):

                # Elimina esa casilla de seguras por si antes lo era
                agente.seguras.discard(nuevo_pozo)

            # Si el agente tiene base de conocimiento
            if hasattr(agente, "kb"):

                # Marca el nuevo pozo como posible pozo en la KB
                agente.kb[nuevo_pozo]["p_pozo"] = "p"

            # Informa dónde apareció el nuevo pozo
            print(f"Ha aparecido un nuevo pozo en {nuevo_pozo}")

    # Muestra el tablero real del mundo
    mundo.imprimir_tablero(agente.pos_actual)

    # Obtiene la fila y columna actual del agente
    r, c = agente.pos_actual

    # Obtiene la percepción de la casilla actual
    percepcion = mundo.obtener_percepcion(r, c)

    # El agente procesa la percepción recibida
    agente.integrar_percepcion(r, c, percepcion)

    # Muestra el conocimiento interno del agente
    agente.mostrar_mundo_agente()

    # Verifica si el agente cayó en un pozo
    if percepcion["pozo"]:

        # Aplica penalización por caer en un pozo
        agente.puntuacion += PUNTOS_CAER_POZO

        # Muestra mensaje de derrota
        print("El agente cayó en un pozo.")

        # Termina la simulación
        break

    # Verifica si el agente fue devorado por un Wumpus
    if percepcion["wumpus"]:

        # Aplica penalización por morir
        agente.puntuacion += PUNTOS_MORIR

        # Muestra mensaje de derrota
        print("El agente fue devorado por el Wumpus.")

        # Termina la simulación
        break

    # Verifica si el agente encontró el oro
    if percepcion["oro"]:

        # Aplica recompensa por encontrar el oro
        agente.puntuacion += PUNTOS_ORO

        # Muestra mensaje de victoria
        print("¡VICTORIA! El agente ha encontrado el Oro.")

        # Termina la simulación
        break

    # El agente calcula su siguiente movimiento
    proxima = agente.planificar_siguiente_paso()

    # Si el agente encontró una próxima casilla
    if proxima:

        # Actualiza la posición actual del agente
        agente.pos_actual = proxima

        # Si el agente tiene historial de camino
        if hasattr(agente, "camino"):

            # Agrega la nueva posición al camino recorrido
            agente.camino.append(list(proxima))

    # Si no encontró movimiento posible
    else:

        # Informa que el agente ya no puede avanzar
        print("RESULTADO: El agente no encuentra más caminos seguros.")

        # Termina la simulación
        break


# Muestra la puntuación final del agente
print(f"\nPuntuación final: {agente.puntuacion}")