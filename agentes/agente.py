from configuracion.config import CANTIDAD_WUMPUS, TAMANIO_MUNDO
from configuracion.puntuaciones import *

# Agente lógico para el juego de Wumpus
class AgenteLogico:
    # Inicializa el agente con el mundo y su conocimiento inicial
    def __init__(self, mundo):
        # El agente mantiene una referencia al mundo, su tamaño, posición actual, y
        # conjuntos para rastrear casillas visitadas, seguras, posibles ubicaciones de Wumpus y pozos.
        self.mundo = mundo
        self.size = TAMANIO_MUNDO
        self.pos_actual = (0, 0)

        self.visitados = set()
        self.seguras = {(0, 0)}

        self.wumpus_restantes = CANTIDAD_WUMPUS

        self.posibles_wumpus = set()
        self.posibles_pozos = set()

        # La base de conocimiento del agente se representa como un diccionario que asigna a cada posición
        # un estado de conocimiento sobre la presencia de pozos y Wumpus.
        self.kb = {
            (r, c): {
                "p_pozo": "u",
                "p_wumpus": "u"
            }
            for r in range(self.size)
            for c in range(self.size)
        }
        # El camino que el agente ha seguido se almacena como una lista de posiciones.
        self.camino = [[0, 0]]
        # La puntuación del agente se inicializa en 0 y se actualizará a medida que el agente tome acciones y
        # reciba recompensas o penalizaciones.
        self.puntuacion = 0

    # Método para determinar si una posición es peligrosa, es decir, si podría contener un pozo o un Wumpus.
    def es_peligrosa(self, pos):
        return pos in self.posibles_pozos or pos in self.posibles_wumpus

    # Método para integrar las percepciones recibidas en la posición actual del agente y actualizar su conocimiento
    def integrar_percepcion(self, r, c, perc):
        # El agente marca la posición actual como visitada y segura, y actualiza su base de conocimiento para reflejar
        # que no hay pozo ni Wumpus en esa posición.
        self.visitados.add((r, c))
        self.seguras.add((r, c))

        self.kb[(r, c)]["p_pozo"] = "s"
        self.kb[(r, c)]["p_wumpus"] = "s"
        # Luego, el agente analiza las percepciones recibidas (brisa, hedor, resplandor) para inferir información
        # sobre las casillas adyacentes.
        adjacentes = self.mundo.get_adjacentes(r, c)
        # Si no hay brisa ni hedor, el agente puede inferir que todas las casillas adyacentes son seguras y
        # no contienen ni pozos ni Wumpus.
        if not perc["brisa"] and not perc["hedor"]:
            for nr, nc in adjacentes:
                pos = (nr, nc)

                self.seguras.add(pos)

                self.kb[pos]["p_pozo"] = "s"
                self.kb[pos]["p_wumpus"] = "s"

                self.posibles_pozos.discard(pos)
                self.posibles_wumpus.discard(pos)
        # Si hay hedor, el agente infiere que al menos una de las casillas adyacentes podría contener un Wumpus,
        # y actualiza su conocimiento en consecuencia.
        if perc["hedor"]:
            for nr, nc in adjacentes:
                pos = (nr, nc)

                if pos not in self.visitados:
                    self.posibles_wumpus.add(pos)
                    self.kb[pos]["p_wumpus"] = "p"
                    self.seguras.discard(pos)
        # Si hay brisa, el agente infiere que al menos una de las casillas adyacentes podría contener un pozo,
        # y actualiza su conocimiento en consecuencia.
        if perc["brisa"]:
            for nr, nc in adjacentes:
                pos = (nr, nc)

                if pos not in self.visitados:
                    self.posibles_pozos.add(pos)
                    self.kb[pos]["p_pozo"] = "p"
                    self.seguras.discard(pos)
        # Si hay wumpus restantes y las posibles casillas de un wumpus es 1, el agente identifica la ubicación del
        # wumpus y decide disparar una flecha para eliminarlo, actualizando su puntuación y conocimiento en consecuencia.
        if self.wumpus_restantes > 0 and len(self.posibles_wumpus) == 1:
            w_pos = list(self.posibles_wumpus)[0]

            print(f"¡Wumpus identificado en {w_pos}! Disparando flecha...")

            self.puntuacion += PUNTOS_DISPARO
            # El agente intenta disparar al Wumpus en la posición identificada. Si tiene éxito, actualiza su
            # puntuación, reduce el número de Wumpus restantes, y actualiza su conocimiento para reflejar que esa
            # casilla ahora es segura. Si falla, descarta esa posición como posible ubicación del Wumpus.
            if self.mundo.disparar(*w_pos):
                print("¡Wumpus eliminado!")

                self.puntuacion += PUNTOS_MATAR_WUMPUS
                self.wumpus_restantes -= 1

                self.posibles_wumpus.clear()

                self.seguras.add(w_pos)
                self.kb[w_pos]["p_wumpus"] = "s"
                self.kb[w_pos]["p_pozo"] = "s"

                self.posibles_pozos.discard(w_pos)

            else:
                print("¡Fallo! El Wumpus sigue vivo.")
                self.posibles_wumpus.discard(w_pos)

        print(
            f"Percepciones en {(r, c)}: "
            f"{'Brisa ' if perc['brisa'] else ''}"
            f"{'Hedor ' if perc['hedor'] else ''}"
            f"{'Resplandor' if perc['resplandor'] else ''}"
        )
    # Método para planificar el siguiente paso del agente basado en su conocimiento actual. El agente prioriza moverse
    #  a casillas seguras no visitadas, luego a casillas de riesgo controlado, y finalmente utiliza backtracking si no
    #  hay opciones seguras disponibles.
    def planificar_siguiente_paso(self):
        opciones = [
            p for p in self.seguras
            if isinstance(p, tuple)
            and len(p) == 2
            and p not in self.visitados
        ]

        if opciones:
            for opt in opciones:
                if opt in self.mundo.get_adjacentes(*self.pos_actual):
                    return opt

            return opciones[0]

        adyacentes = self.mundo.get_adjacentes(*self.pos_actual)

        opciones_riesgo = [
            pos for pos in adyacentes
            if pos not in self.visitados
            and not self.es_peligrosa(pos)
        ]

        if opciones_riesgo:
            print("No hay casillas seguras. Tomando una opción de riesgo controlado.")
            return opciones_riesgo[0]

        if len(self.camino) > 1:
            pos_actual = tuple(self.camino[-1])
            pos_anterior = tuple(self.camino[-2])

            print(f"Utilizando backtracking: {pos_actual} -> {pos_anterior}")

            self.camino.pop()

            return pos_anterior

        return None
    # Metodo para mostrar el conocimiento actual del agente sobre el mundo, indicando su posición actual, las casillas
    # que considera seguras, y las posibles ubicaciones de pozos y Wumpus.
    def mostrar_mundo_agente(self):
        print("\n=== CONOCIMIENTO DEL AGENTE ===\n")

        for r in reversed(range(self.size)):
            for c in range(self.size):
                pos = (r, c)

                if pos == self.pos_actual:
                    print(" A ", end="")

                elif self.kb[pos]["p_wumpus"] == "p" and self.kb[pos]["p_pozo"] == "p":
                    print("WP ", end="")

                elif self.kb[pos]["p_pozo"] == "p":
                    print(" P ", end="")

                elif self.kb[pos]["p_wumpus"] == "p":
                    print(" W ", end="")

                elif pos in self.seguras:
                    print(" S ", end="")

                else:
                    print(" ? ", end="")

            print()

    # Método para mostrar el mundo en formato de matriz, indicando la posición actual del agente, las casillas
    #  visitadas, seguras, y las posibles ubicaciones de pozos y Wumpus.
    def mostrar_mundo_matriz(self):
        matriz = []

        for r in reversed(range(self.size)):
            fila = []

            for c in range(self.size):
                pos = (r, c)

                if pos == self.pos_actual:
                    fila.append("A")

                elif self.kb[pos]["p_wumpus"] == "p" and self.kb[pos]["p_pozo"] == "p":
                    fila.append("WP")

                elif self.kb[pos]["p_pozo"] == "p":
                    fila.append("P")

                elif self.kb[pos]["p_wumpus"] == "p":
                    fila.append("W")

                elif pos in self.visitados:
                    fila.append("V")

                elif pos in self.seguras:
                    fila.append("S")

                else:
                    fila.append("?")

            matriz.append(fila)

        return matriz
    # Método para reiniciar el conocimiento del agente sobre las posibles ubicaciones de Wumpus después de moverse a
    #  una nueva posición, manteniendo solo la información sobre la posición actual como segura y visitada.
    def reiniciar_por_movimiento_wumpus(self):
        self.posibles_wumpus.clear()
        self.seguras = {self.pos_actual}
        self.visitados = {self.pos_actual}

        for pos in self.kb:
            if self.kb[pos]["p_wumpus"] == "p":
                self.kb[pos]["p_wumpus"] = "u"
    # Método para reiniciar completamente el conocimiento del agente sobre el mundo después de moverse a una nueva
    #  posición,manteniendo solo la información sobre la posición actual como segura y visitada, y
    #  descartando cualquier información previa sobre pozos y Wumpus.
    def reiniciar_por_nuevo_pozo(self):
        self.visitados = {self.pos_actual}
        self.seguras = {self.pos_actual}
        self.camino = [list(self.pos_actual)]

