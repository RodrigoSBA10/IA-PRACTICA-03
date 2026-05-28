import random

class WumpusWorld:
    def __init__(self, size=6):
        self.size = size
        # Cada celda es un diccionario con las propiedades del mundo
        self.grid = [[{'brisa': False, 'hedor': False, 'resplandor': False,
                       'pozo': False, 'wumpus': False, 'oro': False}
                      for _ in range(size)] for _ in range(size)]
        self._generar_mundo()

    def _generar_mundo(self):
        posiciones = [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if (r, c) != (0, 0)
        ]

        posiciones_disponibles = posiciones.copy()

        # Generar pozos
        for r, c in posiciones:
            if random.random() < 0.15:
                self.grid[r][c]['pozo'] = True

        # Generar múltiples Wumpus
        cantidad_wumpus = 2

        for _ in range(cantidad_wumpus):
            w_pos = random.choice(posiciones_disponibles)
            posiciones_disponibles.remove(w_pos)

            self.grid[w_pos[0]][w_pos[1]]['wumpus'] = True

        # Evitar que el oro aparezca sobre un Wumpus o pozo
        posiciones_para_oro = [
            (r, c)
            for r, c in posiciones_disponibles
            if not self.grid[r][c]['pozo']
        ]

        o_pos = random.choice(posiciones_para_oro)
        self.grid[o_pos[0]][o_pos[1]]['oro'] = True
        self.grid[o_pos[0]][o_pos[1]]['resplandor'] = True

        self._set_percepciones()

    def _set_percepciones(self):
        for r in range(self.size):
            for c in range(self.size):
                adj = self.get_adjacentes(r, c)
                if self.grid[r][c]['pozo']:
                    for nr, nc in adj: self.grid[nr][nc]['brisa'] = True
                if self.grid[r][c]['wumpus']:
                    for nr, nc in adj: self.grid[nr][nc]['hedor'] = True

    def get_adjacentes(self, r, c):
        res = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size: res.append((nr, nc))
        return res

    def imprimir_tablero(self, pos_agente):

        print("\n--- ESTADO DEL MUNDO ---")
        for r in range(self.size - 1, -1, -1):  # Invertir para que (0,0) sea abajo-izq
            fila = "|"
            for c in range(self.size):
                char = ""
                if (r, c) == pos_agente: char += "A"  # Agente
                if self.grid[r][c]['wumpus']: char += "W"
                if self.grid[r][c]['pozo']: char += "P"
                if self.grid[r][c]['oro']: char += "G"

                fila += char.center(4) + "|"
            print(fila)
            print("-" * (self.size * 6))
        print("Leyenda: A=Agente, W=Wumpus, P=Pozo, G=Oro\n")

    def obtener_percepcion(self, r, c):
        return self.grid[r][c]

    def disparar(self, r, c):
        if self.grid[r][c]['wumpus']:
            self.grid[r][c]['wumpus'] = False

            self.limpiar_percepciones()
            self._set_percepciones()

            return True

        return False

    def limpiar_percepciones(self):
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c]['brisa'] = False
                self.grid[r][c]['hedor'] = False

    def mover_wumpus(self):

        posiciones_wumpus = []

        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c]['wumpus']:
                    posiciones_wumpus.append((r, c))

        for r, c in posiciones_wumpus:

            posibles = [
                (nr, nc)
                for nr, nc in self.get_adjacentes(r, c)
                if not self.grid[nr][nc]['pozo']
                   and not self.grid[nr][nc]['oro']
                   and (nr, nc) != (0, 0)
                   and not self.grid[nr][nc]['wumpus']
            ]

            if posibles:
                nueva_pos = random.choice(posibles)

                self.grid[r][c]['wumpus'] = False
                self.grid[nueva_pos[0]][nueva_pos[1]]['wumpus'] = True

        self.limpiar_percepciones()
        self._set_percepciones()

    def agregar_pozo_aleatorio(self):
        posiciones_validas = [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if (r, c) != (0, 0)
               and not self.grid[r][c]['pozo']
               and not self.grid[r][c]['wumpus']
               and not self.grid[r][c]['oro']
        ]

        if posiciones_validas:
            p_pos = random.choice(posiciones_validas)
            self.grid[p_pos[0]][p_pos[1]]['pozo'] = True

            self.limpiar_percepciones()
            self._set_percepciones()

            return p_pos

        return None
