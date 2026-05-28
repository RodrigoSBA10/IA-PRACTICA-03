from mundo import WumpusWorld
from agente import AgenteLogico
from config import TURNOS_MAXIMOS


mundo = WumpusWorld()
agente = AgenteLogico(mundo)

for turno in range(1, TURNOS_MAXIMOS + 1):
    print(f"*** MOVIMIENTO {turno} ***")

    if turno % 3 == 0:
        mundo.mover_wumpus()
        agente.posible_wumpus.clear()
        agente.peligros.clear()
        agente.seguras = set(agente.visitados)

        for pos in agente.kb:
            if agente.kb[pos]['p_wumpus'] == 'p':
                agente.kb[pos]['p_wumpus'] = 'u'

        print("Los Wumpus se han movido...")

    if turno % 4 == 0:
        nuevo_pozo = mundo.agregar_pozo_aleatorio()

        if nuevo_pozo:
            agente.peligros.clear()

            agente.seguras.discard(nuevo_pozo)
            agente.peligros.add(nuevo_pozo)

            agente.kb[nuevo_pozo]['p_pozo'] = 'p'

            for pos in agente.kb:
                if agente.kb[pos]['p_pozo'] == 'p' and pos != nuevo_pozo:
                    agente.kb[pos]['p_pozo'] = 'u'

            print(f"Ha aparecido un nuevo pozo en {nuevo_pozo}")

    mundo.imprimir_tablero(agente.pos_actual)

    r, c = agente.pos_actual
    percepcion = mundo.obtener_percepcion(r, c)

    agente.integrar_percepcion(r, c, percepcion)
    agente.mostrar_mundo_agente()

    if percepcion['oro']:
        print("¡VICTORIA! El agente ha encontrado el Oro.")
        break

    proxima = agente.planificar_siguiente_paso()

    if proxima:
        agente.pos_actual = proxima
        agente.camino.append(list(proxima))
    else:
        print("RESULTADO: El agente no encuentra más caminos seguros. Fin de la simulación.")
        break