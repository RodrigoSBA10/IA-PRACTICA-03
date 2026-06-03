# Importa la cantidad de Wumpus definida en config.py
from config import CANTIDAD_WUMPUS, TAMANIO_MUNDO

from puntuaciones import *


# Clase que representa al agente lógico
class AgenteLogico:

    # Constructor del agente
    def __init__(self, mundo):

        # Guarda una referencia al mundo
        self.mundo = mundo

        # Tamaño del tablero
        self.size = TAMANIO_MUNDO

        # Posición inicial del agente
        self.pos_actual = (0, 0)

        # Conjunto de casillas visitadas
        self.visitados = set()

        # Casillas que el agente considera seguras
        self.seguras = set([(0, 0)])

        # Cantidad de Wumpus que quedan vivos
        self.wumpus_restantes = CANTIDAD_WUMPUS

        # Posibles posiciones donde puede estar un Wumpus
        self.posible_wumpus = set()

        # Casillas que el agente considera peligrosas
        self.peligros = set()

        # Base de conocimiento del agente
        # 's' = seguro
        # 'p' = posible peligro
        # 'u' = desconocido
        self.kb = {
            (r, c): {
                'p_pozo': 'u',
                'p_wumpus': 'u'
            }
            for r in range(self.size)
            for c in range(self.size)
        }

        # Camino recorrido por el agente
        self.camino = [[0, 0]]

        # Puntuación del agente
        self.puntuacion = 0

    # Método para integrar la percepción actual del agente
    def integrar_percepcion(self, r, c, perc):

        # Marca la casilla actual como visitada
        self.visitados.add((r, c))

        # Marca la casilla actual como segura
        self.seguras.add((r, c))

        # Actualiza la base de conocimiento para la casilla actual
        self.kb[(r, c)]['p_pozo'] = 's'
        self.kb[(r, c)]['p_wumpus'] = 's'

        # Obtiene las casillas adyacentes a la posición actual
        adjacentes = self.mundo.get_adjacentes(r, c)

        # Si no hay brisa ni hedor, las casillas adyacentes son seguras
        if not perc['brisa'] and not perc['hedor']:

            # Recorre las casillas adyacentes
            for nr, nc in adjacentes:

                # Marca la casilla como segura
                self.seguras.add((nr, nc))

                # Actualiza la KB como segura
                self.kb[(nr, nc)]['p_pozo'] = 's'
                self.kb[(nr, nc)]['p_wumpus'] = 's'

                # Si estaba marcada como peligro, la elimina
                self.peligros.discard((nr, nc))

                # Si estaba marcada como posible Wumpus, la elimina
                self.posible_wumpus.discard((nr, nc))

        # Si hay brisa, entonces puede haber un pozo en alguna casilla adyacente
        if perc['brisa']:

            # Recorre las casillas adyacentes
            for nr, nc in adjacentes:

                # Solo marca como peligro si no ha sido visitada
                if (nr, nc) not in self.visitados:

                    # Agrega la casilla como peligrosa
                    self.peligros.add((nr, nc))

                    # Si no estaba marcada como segura, la marca como posible pozo
                    if self.kb[(nr, nc)]['p_pozo'] != 's':
                        self.kb[(nr, nc)]['p_pozo'] = 'p'

        # Si hay hedor, entonces puede haber un Wumpus en alguna casilla adyacente
        if perc['hedor']:

            # Recorre las casillas adyacentes
            for nr, nc in adjacentes:

                # Solo considera casillas no visitadas
                if (nr, nc) not in self.visitados:

                    # Agrega la casilla como peligrosa
                    self.peligros.add((nr, nc))

                    # La agrega como posible posición de Wumpus
                    self.posible_wumpus.add((nr, nc))

                    # Si no estaba marcada como segura, la marca como posible Wumpus
                    if self.kb[(nr, nc)]['p_wumpus'] != 's':
                        self.kb[(nr, nc)]['p_wumpus'] = 'p'

        # Si queda al menos un Wumpus y solo hay una posible posición, intenta disparar
        if self.wumpus_restantes > 0 and len(self.posible_wumpus) == 1:

            # Obtiene la única posición posible del Wumpus
            w_pos = list(self.posible_wumpus)[0]

            # Muestra mensaje de disparo
            print(f"¡Wumpus identificado en {w_pos}! Disparando flecha...")

            self.puntuacion += PUNTOS_DISPARO

            # Intenta disparar en esa posición
            if self.mundo.disparar(*w_pos):

                # Si acertó, muestra mensaje
                print("¡Wumpus eliminado!")

                self.puntuacion += PUNTOS_MATAR_WUMPUS

                # Reduce la cantidad de Wumpus restantes
                self.wumpus_restantes -= 1

                # Limpia las posiciones posibles de Wumpus
                self.posible_wumpus.clear()

                # Marca como seguras las casillas alrededor del Wumpus eliminado
                for nr, nc in self.mundo.get_adjacentes(*w_pos):
                    self.seguras.add((nr, nc))

            else:

                # Si falló, muestra mensaje
                print("¡Fallo! El Wumpus sigue vivo.")

        # Muestra las percepciones recibidas en la casilla actual
        print(
            f"Percepciones en {(r, c)}: "
            f"{'Brisa ' if perc['brisa'] else ''}"
            f"{'Hedor ' if perc['hedor'] else ''}"
            f"{'Resplandor' if perc['resplandor'] else ''}"
        )

    # Método que decide el siguiente movimiento del agente
    def planificar_siguiente_paso(self):

        # Busca casillas seguras que aún no hayan sido visitadas
        opciones = [
            p for p in self.seguras
            if p not in self.visitados
        ]

        # Si hay opciones seguras disponibles
        if opciones:

            # Primero intenta moverse a una casilla segura adyacente
            for opt in opciones:

                if opt in self.mundo.get_adjacentes(*self.pos_actual):
                    return opt

            # Si no hay una adyacente, regresa la primera opción segura
            return opciones[0]

        # Si no hay casillas seguras, intenta un riesgo controlado
        adyacentes = self.mundo.get_adjacentes(*self.pos_actual)

        opciones_riesgo = [
            pos for pos in adyacentes
            if pos not in self.visitados
               and pos not in self.peligros
        ]

        if opciones_riesgo:
            print("No hay casillas seguras. Tomando una opción de riesgo controlado.")
            return opciones_riesgo[0]

        # Si no hay opciones nuevas, usa backtracking
        if len(self.camino) > 1:
            print("Utilizando backtracking")

            self.camino.pop()

            return tuple(self.camino[-1])

        return None

    # Método para mostrar el conocimiento interno del agente
    def mostrar_mundo_agente(self):

        # Título del mapa del agente
        print("\n=== CONOCIMIENTO DEL AGENTE ===\n")

        # Recorre filas de arriba hacia abajo
        for r in reversed(range(self.size)):

            # Recorre columnas
            for c in range(self.size):

                # Si es la posición actual del agente
                if (r, c) == self.pos_actual:
                    print(" A ", end="")

                # Si la KB indica posible pozo
                elif self.kb[(r, c)]['p_pozo'] == 'p':
                    print(" P ", end="")

                # Si la KB indica posible Wumpus
                elif self.kb[(r, c)]['p_wumpus'] == 'p':
                    print(" W ", end="")

                # Si el agente considera la casilla segura
                elif (r, c) in self.seguras:
                    print(" S ", end="")

                # Si no sabe nada de la casilla
                else:
                    print(" ? ", end="")

            # Salto de línea al terminar cada fila
            print()