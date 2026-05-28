class AgenteLogico:

    def __init__(self, mundo, size=6):

        self.mundo = mundo

        self.size = size

        self.pos_actual = (0, 0)

        self.visitados = set()

        # Casillas seguras conocidas
        self.seguras = set([(0, 0)])

        # Estado del Wumpus
        self.wumpus_vivo = True

        # Posibles posiciones del Wumpus
        self.posible_wumpus = set()

        # Posibles peligros
        self.peligros = set()

        # Base de conocimiento
        self.kb = {
            (r, c): {
                'p_pozo': 'u',
                'p_wumpus': 'u'
            }
            for r in range(size)
            for c in range(size)
        }

        # Camino recorrido
        self.camino = [[0, 0]]

    def integrar_percepcion(self, r, c, perc):

        self.visitados.add((r, c))
        self.seguras.add((r, c))

        self.kb[(r, c)]['p_pozo'] = 's'
        self.kb[(r, c)]['p_wumpus'] = 's'

        adjacentes = self.mundo.get_adjacentes(r, c)

        # Sin percepciones => adyacentes seguros
        if not perc['brisa'] and not perc['hedor']:

            for nr, nc in adjacentes:

                self.seguras.add((nr, nc))

                self.kb[(nr, nc)]['p_pozo'] = 's'
                self.kb[(nr, nc)]['p_wumpus'] = 's'

                self.peligros.discard((nr, nc))
                self.posible_wumpus.discard((nr, nc))

        # Posibles pozos
        if perc['brisa']:

            for nr, nc in adjacentes:

                if (nr, nc) not in self.visitados:

                    self.peligros.add((nr, nc))

                    if self.kb[(nr, nc)]['p_pozo'] != 's':
                        self.kb[(nr, nc)]['p_pozo'] = 'p'

        # Posibles Wumpus
        if perc['hedor']:

            for nr, nc in adjacentes:

                if (nr, nc) not in self.visitados:

                    self.peligros.add((nr, nc))
                    self.posible_wumpus.add((nr, nc))

                    if self.kb[(nr, nc)]['p_wumpus'] != 's':
                        self.kb[(nr, nc)]['p_wumpus'] = 'p'

        # Intentar eliminar Wumpus
        if self.wumpus_vivo and len(self.posible_wumpus) == 1:

            w_pos = list(self.posible_wumpus)[0]

            print(f"¡Wumpus identificado en {w_pos}! Disparando flecha...")

            if self.mundo.disparar(*w_pos):

                print("¡Wumpus eliminado!")

                self.wumpus_vivo = False

                self.posible_wumpus.clear()

                for nr, nc in self.mundo.get_adjacentes(*w_pos):
                    self.seguras.add((nr, nc))

            else:
                print("¡Fallo! El Wumpus sigue vivo.")

        print(
            f"Percepciones en {(r, c)}: "
            f"{'Brisa ' if perc['brisa'] else ''}"
            f"{'Hedor ' if perc['hedor'] else ''}"
            f"{'Resplandor' if perc['resplandor'] else ''}"
        )

    def planificar_siguiente_paso(self):

        opciones = [
            p for p in self.seguras
            if p not in self.visitados
        ]

        if opciones:

            for opt in opciones:

                if opt in self.mundo.get_adjacentes(*self.pos_actual):
                    return opt

            return opciones[0]

        # Backtracking
        if len(self.camino) > 1:

            print("Utilizando backtracking")

            self.camino.pop()

            return tuple(self.camino[-1])

        return None

    def mostrar_mundo_agente(self):

        print("\n=== CONOCIMIENTO DEL AGENTE ===\n")

        for r in reversed(range(self.size)):

            for c in range(self.size):

                if (r, c) == self.pos_actual:
                    print(" A ", end="")

                elif self.kb[(r, c)]['p_pozo'] == 'p':
                    print(" P ", end="")

                elif self.kb[(r, c)]['p_wumpus'] == 'p':
                    print(" W ", end="")

                elif (r, c) in self.seguras:
                    print(" S ", end="")

                else:
                    print(" ? ", end="")

            print()