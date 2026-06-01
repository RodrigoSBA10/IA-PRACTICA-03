# Importa la librería random para generar posiciones y eventos aleatorios
import random

# Importa todas las constantes definidas en config.py
from config import *


# Clase que representa el mundo del Wumpus
class WumpusWorld:

    # Constructor de la clase
    def __init__(self):

        # Define el tamaño del mundo usando la constante del archivo config.py
        self.size = TAMANIO_MUNDO

        # Crea la matriz del mundo.
        # Cada celda es un diccionario con sus propiedades.
        self.grid = [
            [
                {
                    'brisa': False,       # Indica si hay brisa cerca de un pozo
                    'hedor': False,       # Indica si hay hedor cerca de un Wumpus
                    'resplandor': False,  # Indica si hay oro en la casilla
                    'pozo': False,        # Indica si la casilla contiene un pozo
                    'wumpus': False,      # Indica si la casilla contiene un Wumpus
                    'oro': False          # Indica si la casilla contiene oro
                }
                for _ in range(self.size)
            ]
            for _ in range(self.size)
        ]

        # Genera el contenido inicial del mundo
        self._generar_mundo()

    # Método encargado de generar pozos, Wumpus y oro
    def _generar_mundo(self):

        # Genera todas las posiciones del tablero excepto la casilla inicial (0,0)
        posiciones = [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if (r, c) != (0, 0)
        ]

        # Copia las posiciones disponibles para evitar repetir elementos importantes
        posiciones_disponibles = posiciones.copy()

        # Recorre todas las posiciones posibles
        for r, c in posiciones:

            # Coloca un pozo con cierta probabilidad
            if random.random() < PROBABILIDAD_POZO:
                self.grid[r][c]['pozo'] = True

        # Define cuántos Wumpus habrá en el mundo
        cantidad_wumpus = CANTIDAD_WUMPUS

        # Coloca la cantidad definida de Wumpus
        for _ in range(cantidad_wumpus):

            # Selecciona una posición aleatoria disponible
            w_pos = random.choice(posiciones_disponibles)

            # Elimina esa posición para que no se repita otro Wumpus ahí
            posiciones_disponibles.remove(w_pos)

            # Coloca un Wumpus en la posición seleccionada
            self.grid[w_pos[0]][w_pos[1]]['wumpus'] = True

        # Filtra posiciones donde puede aparecer el oro
        posiciones_para_oro = [
            (r, c)
            for r, c in posiciones_disponibles
            if not self.grid[r][c]['pozo']
        ]

        # Selecciona una posición válida para el oro
        o_pos = random.choice(posiciones_para_oro)

        # Coloca el oro en la posición seleccionada
        self.grid[o_pos[0]][o_pos[1]]['oro'] = True

        # Marca resplandor en la casilla donde está el oro
        self.grid[o_pos[0]][o_pos[1]]['resplandor'] = True

        # Genera las percepciones del mundo
        self._set_percepciones()

    # Método que asigna brisa y hedor alrededor de pozos y Wumpus
    def _set_percepciones(self):

        # Recorre todas las filas
        for r in range(self.size):

            # Recorre todas las columnas
            for c in range(self.size):

                # Obtiene las casillas adyacentes a la posición actual
                adj = self.get_adjacentes(r, c)

                # Si la casilla tiene pozo
                if self.grid[r][c]['pozo']:

                    # Coloca brisa en las casillas adyacentes
                    for nr, nc in adj:
                        self.grid[nr][nc]['brisa'] = True

                # Si la casilla tiene Wumpus
                if self.grid[r][c]['wumpus']:

                    # Coloca hedor en las casillas adyacentes
                    for nr, nc in adj:
                        self.grid[nr][nc]['hedor'] = True

    # Método que devuelve las posiciones adyacentes válidas
    def get_adjacentes(self, r, c):

        # Lista donde se guardarán las casillas vecinas
        res = []

        # Posibles movimientos: derecha, izquierda, abajo y arriba
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:

            # Calcula la nueva fila y columna
            nr, nc = r + dr, c + dc

            # Verifica que la posición esté dentro del tablero
            if 0 <= nr < self.size and 0 <= nc < self.size:

                # Agrega la posición válida a la lista
                res.append((nr, nc))

        # Devuelve las posiciones adyacentes válidas
        return res

    # Método para imprimir el estado real del mundo
    def imprimir_tablero(self, pos_agente):

        # Título del tablero
        print("\n--- ESTADO DEL MUNDO ---")

        # Recorre las filas de arriba hacia abajo para que (0,0) se vea abajo
        for r in range(self.size - 1, -1, -1):

            # Inicia la fila visual
            fila = "|"

            # Recorre cada columna
            for c in range(self.size):

                # Variable para guardar los símbolos de la celda
                char = ""

                # Si el agente está en esta casilla, se muestra A
                if (r, c) == pos_agente:
                    char += "A"

                # Si hay Wumpus, se muestra W
                if self.grid[r][c]['wumpus']:
                    char += "W"

                # Si hay pozo, se muestra P
                if self.grid[r][c]['pozo']:
                    char += "P"

                # Si hay oro, se muestra G
                if self.grid[r][c]['oro']:
                    char += "G"

                # Centra el contenido de la celda para mantener el formato
                fila += char.center(4) + "|"

            # Imprime la fila
            print(fila)

            # Imprime una línea separadora
            print("-" * (self.size * 6))

        # Imprime la leyenda
        print("Leyenda: A=Agente, W=Wumpus, P=Pozo, G=Oro\n")

    # Método que devuelve la percepción de una casilla
    def obtener_percepcion(self, r, c):

        # Devuelve el diccionario de la celda indicada
        return self.grid[r][c]

    # Método para disparar a una casilla
    def disparar(self, r, c):

        # Verifica si hay un Wumpus en la casilla indicada
        if self.grid[r][c]['wumpus']:

            # Elimina el Wumpus
            self.grid[r][c]['wumpus'] = False

            # Limpia percepciones anteriores
            self.limpiar_percepciones()

            # Recalcula percepciones considerando los Wumpus restantes
            self._set_percepciones()

            # Indica que el disparo fue exitoso
            return True

        # Si no había Wumpus, el disparo falla
        return False

    # Método que limpia brisas y hedores del tablero
    def limpiar_percepciones(self):

        # Recorre todas las filas
        for r in range(self.size):

            # Recorre todas las columnas
            for c in range(self.size):

                # Quita la brisa
                self.grid[r][c]['brisa'] = False

                # Quita el hedor
                self.grid[r][c]['hedor'] = False

    # Método para mover los Wumpus
    def mover_wumpus(self):

        # Lista para guardar las posiciones actuales de los Wumpus
        posiciones_wumpus = []

        # Recorre todas las filas
        for r in range(self.size):

            # Recorre todas las columnas
            for c in range(self.size):

                # Si encuentra un Wumpus, guarda su posición
                if self.grid[r][c]['wumpus']:
                    posiciones_wumpus.append((r, c))

        # Recorre cada Wumpus encontrado
        for r, c in posiciones_wumpus:

            # Calcula las posiciones válidas a donde puede moverse el Wumpus
            posibles = [
                (nr, nc)
                for nr, nc in self.get_adjacentes(r, c)
                if not self.grid[nr][nc]['pozo']
                and not self.grid[nr][nc]['oro']
                and (nr, nc) != (0, 0)
                and not self.grid[nr][nc]['wumpus']
            ]

            # Si hay posiciones posibles
            if posibles:

                # Elige una posición aleatoria
                nueva_pos = random.choice(posibles)

                # Quita el Wumpus de su posición actual
                self.grid[r][c]['wumpus'] = False

                # Coloca el Wumpus en la nueva posición
                self.grid[nueva_pos[0]][nueva_pos[1]]['wumpus'] = True

        # Limpia las percepciones anteriores
        self.limpiar_percepciones()

        # Recalcula las percepciones después del movimiento
        self._set_percepciones()

    # Método para agregar un pozo nuevo durante la simulación
    def agregar_pozo_aleatorio(self, pos_agente=None):

        # Busca posiciones válidas donde pueda aparecer un pozo nuevo
        posiciones_validas = [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if (r, c) != (0, 0)
            and (r, c) != pos_agente
            and not self.grid[r][c]['pozo']
            and not self.grid[r][c]['wumpus']
            and not self.grid[r][c]['oro']
        ]

        # Si existen posiciones válidas
        if posiciones_validas:

            # Escoge una posición aleatoria
            p_pos = random.choice(posiciones_validas)

            # Coloca el pozo en la posición seleccionada
            self.grid[p_pos[0]][p_pos[1]]['pozo'] = True

            # Limpia percepciones anteriores
            self.limpiar_percepciones()

            # Recalcula percepciones del mundo
            self._set_percepciones()

            # Devuelve la posición del nuevo pozo
            return p_pos

        # Si no hay posiciones válidas, no agrega nada
        return None