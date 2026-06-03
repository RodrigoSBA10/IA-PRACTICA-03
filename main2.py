from mundo import WumpusWorld
from AgenteAleatorio import AgenteAleatorio
from config import TURNOS_MAXIMOS


mundo = WumpusWorld()
agente = AgenteAleatorio(mundo)


for turno in range(1, TURNOS_MAXIMOS + 1):
    print(f"*** MOVIMIENTO {turno} ***")

    if turno % 3 == 0:
        mundo.mover_wumpus()
        print("Los Wumpus se han movido...")

    if turno % 4 == 0:
        nuevo_pozo = mundo.agregar_pozo_aleatorio()

        if nuevo_pozo:
           print(f"Ha aparecido un nuevo pozo en {nuevo_pozo}")

    mundo.imprimir_tablero(agente.pos_actual)

    r, c = agente.pos_actual
    percepcion = mundo.obtener_percepcion(r, c)

    agente.integrar_percepcion(r, c, percepcion)
    agente.mostrar_mundo_agente()

    if percepcion['oro']:
        print("¡VICTORIA! El agente ha encontrado el Oro.")
        break
    if percepcion['pozo']:
        print("Perdiste caiste en la pozo")
        break
        
    #Mocimientos aleatorio 
    proxima = agente.planificar_siguiente_paso()
    if proxima:
        agente.pos_actual = proxima
        agente.camino.append(list(proxima))
    else:
        print("RESULTADO: El agente no encuentra más caminos seguros. Fin de la simulación.")
        break