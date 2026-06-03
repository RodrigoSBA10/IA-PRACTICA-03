# Importa random para tomar decisiones aleatorias
import random

# Importa las constantes del archivo config.py
from config import *

from puntuaciones import *


# Clase del agente que se mueve de forma aleatoria
class AgenteAleatorio:

    # Constructor del agente
    def __init__(self, mundo):

        # Guarda una referencia al mundo
        self.mundo = mundo

        # Tamaño del tablero
        self.size = TAMANIO_MUNDO

        # Posición inicial del agente
        self.pos_actual = (0, 0)

        # Casillas visitadas por el agente
        self.visitados = set()

        # Camino recorrido por el agente
        self.camino = [[0, 0]]

        # Posibles posiciones donde podría estar un Wumpus
        self.posibles_wumpus = set()

        # Cantidad de Wumpus restantes
        self.wumpus_restantes = CANTIDAD_WUMPUS

        # Cantidad de flechas disponibles
        self.flechas = CANTIDAD_WUMPUS

        # Puntuación del agente
        self.puntuacion = 0

    # Método para recibir la percepción de la casilla actual
    def integrar_percepcion(self, r, c, perc):

        # Marca la casilla actual como visitada
        self.visitados.add((r, c))

        # Obtiene las casillas adyacentes
        adjacentes = self.mundo.get_adjacentes(r, c)

        # Si hay hedor, puede haber un Wumpus en alguna casilla cercana
        if perc['hedor']:

            # Recorre las casillas adyacentes
            for nr, nc in adjacentes:

                # Si la casilla no ha sido visitada, se agrega como posible Wumpus
                if (nr, nc) not in self.visitados:
                    self.posibles_wumpus.add((nr, nc))

        # Si hay posibles Wumpus y aún tiene flechas, dispara aleatoriamente
        if (
            self.wumpus_restantes > 0
            and self.flechas > 0
            and len(self.posibles_wumpus) > 0
        ):

            # Escoge una posible posición del Wumpus al azar
            w_pos = random.choice(list(self.posibles_wumpus))

            # Muestra la posición a la que va a disparar
            print(f"Posible Wumpus en {w_pos}. Disparando flecha...")

            self.puntuacion += PUNTOS_DISPARO
            # Intenta disparar en esa posición
            if self.mundo.disparar(*w_pos):

                self.puntuacion += PUNTOS_MATAR_WUMPUS

                # Resta una flecha
                self.flechas -= 1

                # Resta un Wumpus vivo
                self.wumpus_restantes -= 1

                # Muestra mensaje de éxito
                print("Wumpus muerto")

                # Limpia la lista de posibles Wumpus
                self.posibles_wumpus.clear()

            else:

                # Resta una flecha aunque falle
                self.flechas -= 1

                # Muestra mensaje de fallo
                print("El Wumpus sigue vivo, fallaste el disparo")

                # Quita esa posición porque ya se comprobó que no estaba ahí
                self.posibles_wumpus.discard(w_pos)

        # Muestra las percepciones recibidas por el agente
        print(
            f"Percepciones en {(r, c)}: "
            f"{'Brisa ' if perc['brisa'] else ''}"
            f"{'Hedor ' if perc['hedor'] else ''}"
            f"{'Resplandor' if perc['resplandor'] else ''}"
        )

    # Método para decidir el siguiente movimiento
    def planificar_siguiente_paso(self):

        # Obtiene las casillas adyacentes a la posición actual
        adyacentes = self.mundo.get_adjacentes(*self.pos_actual)

        # Filtra las casillas que aún no ha visitado
        no_visitadas = [
            p for p in adyacentes
            if p not in self.visitados
        ]

        # Si hay casillas no visitadas, escoge una al azar
        if no_visitadas:
            return random.choice(no_visitadas)

        # Si todas ya fueron visitadas, escoge cualquier casilla adyacente
        if adyacentes:
            return random.choice(adyacentes)

        # Si no hay movimientos posibles, regresa None
        return None

    # Método para mostrar el conocimiento del agente
    def mostrar_mundo_agente(self):

        # Título del mapa interno del agente
        print("\n=== CONOCIMIENTO DEL AGENTE ALEATORIO ===\n")

        # Recorre las filas de arriba hacia abajo
        for r in reversed(range(self.size)):

            # Recorre las columnas
            for c in range(self.size):

                # Si es la posición actual del agente
                if (r, c) == self.pos_actual:
                    print(" A ", end="")

                # Si la casilla ya fue visitada
                elif (r, c) in self.visitados:
                    print(" V ", end="")

                # Si no sabe nada de la casilla
                else:
                    print(" ? ", end="")

            # Salto de línea al terminar cada fila
            print()