from configuracion.config import *
from configuracion.puntuaciones import *

# Función principal para actualizar el estado del agente y del mundo en cada turno
def actualizar_agente(
    agente_actual,
    mundo_actual,
    mundo_real_ref,
    conocimiento_ref,
    estado_juego,
    mostrar_mensaje
):
    # Verificar si el juego ya ha terminado antes de realizar cualquier acción
    if estado_juego.juego_terminado:
        # Retornar el estado actual sin realizar cambios
        return mundo_real_ref, conocimiento_ref
    # Verificar si se ha alcanzado el límite máximo de turnos
    if estado_juego.turno_actual > TURNOS_MAXIMOS:
        print("RESULTADO: Se alcanzó el límite máximo de turnos.")
        estado_juego.sin_caminos = True
        estado_juego.juego_terminado = True
        return mundo_real_ref, conocimiento_ref

    print(f"\n*** MOVIMIENTO {estado_juego.turno_actual} ***")

    agente_actual.puntuacion += PUNTOS_MOVIMIENTO

    # Mover el Wumpus cada FRECUENCIA_MOVIMIENTO_WUMPUS
    if estado_juego.turno_actual % FRECUENCIA_MOVIMIENTO_WUMPUS == 0:
        mundo_actual.mover_wumpus()

        if hasattr(agente_actual, "reiniciar_por_movimiento_wumpus"):
            agente_actual.reiniciar_por_movimiento_wumpus()

        print("Los Wumpus se han movido...")
    # Agregar un nuevo pozo cada FRECUENCIA_NUEVO_POZO
    if estado_juego.turno_actual % FRECUENCIA_NUEVO_POZO == 0:
        nuevo_pozo = mundo_actual.agregar_pozo_aleatorio(
            agente_actual.pos_actual
        )
        # Si se agregó un nuevo pozo, eliminarlo de las listas de seguros y visitados del agente
        if nuevo_pozo:
            if hasattr(agente_actual, "seguras"):
                agente_actual.seguras.discard(nuevo_pozo)
                agente_actual.visitados.discard(nuevo_pozo)
            #if hasattr(agente_actual, "reiniciar_por_nuevo_pozo"):
                #agente_actual.reiniciar_por_nuevo_pozo()

            print("Ha aparecido un nuevo pozo")
    # Imprimir el tablero del mundo real con la posición actual del agente
    mundo_actual.imprimir_tablero(agente_actual.pos_actual)
    # Obtener la percepción del agente en su posición actual
    r, c = agente_actual.pos_actual
    mundo_real_ref = mundo_actual.obtener_matriz_visual(pos_agente=(r, c))
    percepcion = mundo_actual.obtener_percepcion(r, c)
    # Verificar si el agente ha caído en un pozo o ha sido devorado por el Wumpus
    if percepcion["pozo"]:
        agente_actual.puntuacion += PUNTOS_CAER_POZO
        print("El agente cayó en un pozo.")
        estado_juego.juego_terminado = True
        return mundo_real_ref, conocimiento_ref

    if percepcion["wumpus"]:
        agente_actual.puntuacion += PUNTOS_MORIR
        print("El agente fue devorado por el Wumpus.")
        estado_juego.agente_devorado = True
        estado_juego.juego_terminado = True
        return mundo_real_ref, conocimiento_ref
    # Integrar la percepción actual del agente en su conocimiento del mundo y mostrar el mundo desde la
    # perspectiva del agente
    agente_actual.integrar_percepcion(r, c, percepcion)
    agente_actual.mostrar_mundo_agente()
    # Actualizar la referencia al conocimiento del agente después de integrar la nueva percepción
    conocimiento_ref = agente_actual.mostrar_mundo_matriz()
    # Verificar si el agente ha eliminado a algún Wumpus y actualizar el estado del juego en consecuencia
    if hasattr(agente_actual, "wumpus_restantes"):
        if agente_actual.wumpus_restantes == 1 and not estado_juego.wumpus_muerto_uno:
            estado_juego.wumpus_muerto_uno = True
            mostrar_mensaje("Wumpus muerto, queda 1")

        if agente_actual.wumpus_restantes == 0 and not estado_juego.wumpus_muerto_dos:
            estado_juego.wumpus_muerto_dos = True
            mostrar_mensaje("Wumpus eliminados")
    # Verificar si el agente ha encontrado el oro y actualizar el estado del juego en consecuencia
    if percepcion["oro"]:
        agente_actual.puntuacion += PUNTOS_ORO
        print("¡VICTORIA! El agente ha encontrado el Oro.")
        conocimiento_ref = agente_actual.mostrar_mundo_matriz()
        estado_juego.victoria = True
        estado_juego.juego_terminado = True
        return mundo_real_ref, conocimiento_ref
    # Planificar el siguiente movimiento del agente utilizando su función de planificación y actualizar su posición
    proxima = agente_actual.planificar_siguiente_paso()

    # Si la función de planificación devuelve None, significa que el agente no encuentra más caminos seguros
    # para avanzar, lo que indica que el juego ha terminado sin victoria.
    if proxima is not None:
        if not isinstance(proxima, tuple):
            print("ERROR: proxima no es una posicion valida")
            estado_juego.juego_terminado = True
            return mundo_real_ref, conocimiento_ref

        agente_actual.pos_actual = proxima

        if hasattr(agente_actual, "camino"):
            proxima_lista = list(proxima)

            if agente_actual.camino[-1] != proxima_lista:
                agente_actual.camino.append(proxima_lista)

        r, c = agente_actual.pos_actual
        mundo_real_ref = mundo_actual.obtener_matriz_visual(pos_agente=(r, c))
        conocimiento_ref = agente_actual.mostrar_mundo_matriz()

    else:
        print("RESULTADO: El agente no encuentra más caminos seguros.")
        estado_juego.sin_caminos = True
        estado_juego.juego_terminado = True

    estado_juego.turno_actual += 1

    return mundo_real_ref, conocimiento_ref