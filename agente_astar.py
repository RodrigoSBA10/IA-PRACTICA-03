# Importa heapq para usar una cola de prioridad en el algoritmo A*
import heapq

# Importa las constantes del archivo config.py
from config import *


# Clase del agente basado en el algoritmo A*
class AgenteAStar:

    # Constructor del agente
    def __init__(self, mundo):

        # Guarda una referencia al mundo
        self.mundo = mundo

        # Tamaño del tablero
        self.size = TAMANIO_MUNDO

        # Posición inicial del agente
        self.pos_actual = (0, 0)

        # Casillas visitadas
        self.visitados = set()

        # Casillas que el agente considera seguras
        self.seguras = set([(0, 0)])

        # Casillas que el agente considera peligrosas
        self.peligros = set()

        # Camino recorrido por el agente
        self.camino = [[0, 0]]

        # Posición del oro si llega a detectarlo
        self.objetivo_oro = None

        # Puntuación del agente
        self.puntuacion = 0

    # Método para integrar la percepción de la casilla actual
    def integrar_percepcion(self, r, c, perc):

        # Marca la casilla actual como visitada
        self.visitados.add((r, c))

        # Marca la casilla actual como segura
        self.seguras.add((r, c))

        # Obtiene las casillas adyacentes
        adyacentes = self.mundo.get_adjacentes(r, c)

        # Si encuentra oro, guarda esa posición como objetivo
        if perc['oro']:
            self.objetivo_oro = (r, c)

        # Si no hay brisa ni hedor, las casillas cercanas se consideran seguras
        if not perc['brisa'] and not perc['hedor']:

            # Recorre las casillas adyacentes
            for nr, nc in adyacentes:

                # Marca la casilla como segura
                self.seguras.add((nr, nc))

                # Si estaba marcada como peligrosa, la elimina
                self.peligros.discard((nr, nc))

        # Si hay brisa o hedor, puede haber peligro alrededor
        if perc['brisa'] or perc['hedor']:

            # Recorre las casillas adyacentes
            for nr, nc in adyacentes:

                # Solo marca como peligro las casillas no visitadas
                if (nr, nc) not in self.visitados:

                    # Agrega la casilla como peligrosa
                    self.peligros.add((nr, nc))

        # Muestra las percepciones recibidas
        print(
            f"Percepciones en {(r, c)}: "
            f"{'Brisa ' if perc['brisa'] else ''}"
            f"{'Hedor ' if perc['hedor'] else ''}"
            f"{'Resplandor' if perc['resplandor'] else ''}"
        )

    # Heurística de Manhattan para medir distancia entre dos casillas
    def heuristica(self, actual, objetivo):

        # Calcula distancia vertical + horizontal
        return abs(actual[0] - objetivo[0]) + abs(actual[1] - objetivo[1])

    # Método que busca un camino usando A*
    def buscar_camino_astar(self, inicio, objetivo):

        # Cola de prioridad donde se guardan los nodos por evaluar
        cola = []

        # Inserta la posición inicial con prioridad 0
        heapq.heappush(cola, (0, inicio))

        # Diccionario para reconstruir el camino
        came_from = {}

        # Costo acumulado para llegar a cada posición
        costo = {inicio: 0}

        # Mientras existan posiciones por evaluar
        while cola:

            # Extrae la posición con menor prioridad
            _, actual = heapq.heappop(cola)

            # Si llegó al objetivo, reconstruye y devuelve el camino
            if actual == objetivo:
                return self.reconstruir_camino(came_from, actual)

            # Recorre los vecinos de la posición actual
            for vecino in self.mundo.get_adjacentes(*actual):

                # Evita pasar por casillas peligrosas
                if vecino in self.peligros:
                    continue

                # Calcula el nuevo costo
                nuevo_costo = costo[actual] + 1

                # Si el vecino no tiene costo o encontramos un camino mejor
                if vecino not in costo or nuevo_costo < costo[vecino]:

                    # Actualiza el costo del vecino
                    costo[vecino] = nuevo_costo

                    # Calcula la prioridad con costo + heurística
                    prioridad = nuevo_costo + self.heuristica(vecino, objetivo)

                    # Agrega el vecino a la cola de prioridad
                    heapq.heappush(cola, (prioridad, vecino))

                    # Guarda de dónde vino para reconstruir el camino
                    came_from[vecino] = actual

        # Si no encontró camino, devuelve None
        return None

    # Método para reconstruir el camino encontrado por A*
    def reconstruir_camino(self, came_from, actual):

        # Inicializa el camino con el objetivo
        camino = [actual]

        # Retrocede desde el objetivo hasta el inicio
        while actual in came_from:

            # Obtiene la posición anterior
            actual = came_from[actual]

            # Agrega la posición al camino
            camino.append(actual)

        # Invierte el camino para que vaya del inicio al objetivo
        camino.reverse()

        # Devuelve el camino completo
        return camino

    # Método para elegir el siguiente paso del agente
    def planificar_siguiente_paso(self):

        # Busca casillas seguras que aún no hayan sido visitadas
        opciones = [
            pos for pos in self.seguras
            if pos not in self.visitados
        ]

        # Guarda el mejor camino encontrado
        mejor_camino = None

        # Evalúa cada posible casilla segura como objetivo
        for objetivo in opciones:

            # Busca un camino con A* hacia ese objetivo
            camino = self.buscar_camino_astar(self.pos_actual, objetivo)

            # Si existe camino y tiene más de una posición
            if camino and len(camino) > 1:

                # Si es el primer camino o es más corto que el anterior
                if mejor_camino is None or len(camino) < len(mejor_camino):
                    # Guarda este camino como el mejor
                    mejor_camino = camino

        # Si encontró un camino seguro válido
        if mejor_camino:
            return mejor_camino[1]

        # Si no encontró camino seguro, intenta riesgo controlado
        adyacentes = self.mundo.get_adjacentes(*self.pos_actual)

        opciones_riesgo = [
            pos for pos in adyacentes
            if pos not in self.visitados
               and pos not in self.peligros
        ]

        # Si hay alguna opción no visitada y no marcada como peligrosa, avanza
        if opciones_riesgo:
            print("A* no encontró camino seguro. Tomando riesgo controlado.")
            return opciones_riesgo[0]

        # Si no hay camino seguro ni riesgo aceptable, termina
        return None

    # Método para mostrar el conocimiento interno del agente
    def mostrar_mundo_agente(self):

        # Título del mapa interno
        print("\n=== CONOCIMIENTO DEL AGENTE A* ===\n")

        # Recorre filas de arriba hacia abajo
        for r in reversed(range(self.size)):

            # Recorre columnas
            for c in range(self.size):

                # Guarda la posición actual del recorrido
                pos = (r, c)

                # Si es la posición del agente
                if pos == self.pos_actual:
                    print(" A ", end="")

                # Si el agente cree que hay peligro
                elif pos in self.peligros:
                    print(" P ", end="")

                # Si el agente cree que es segura
                elif pos in self.seguras:
                    print(" S ", end="")

                # Si no sabe nada de la casilla
                else:
                    print(" ? ", end="")

            # Salto de línea al terminar la fila
            print()
    
    def mostrar_mundo_matriz(self):
        matriz = []

        for r in reversed(range(self.size)):
            fila = []

            for c in range(self.size):

                pos = (r, c)

                if pos == self.pos_actual:
                    fila.append("A")

                elif pos in self.peligros:
                    fila.append("P")

                elif pos in self.seguras:
                    fila.append("S")

                else:
                    fila.append("?")

            matriz.append(fila)

        return matriz
