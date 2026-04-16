import random


class WumpusWorld:
    def __init__(self, size=6):
        self.size = size
        self.grid = [[{'brisa': False, 'hedor': False, 'resplandor': False,
                       'pozo': False, 'wumpus': False, 'oro': False}
                      for _ in range(size)] for _ in range(size)]
        self._generar_mundo()

    def _generar_mundo(self):
        posiciones = [(r, c) for r in range(self.size) for c in range(self.size) if (r, c) != (0, 0)]
        for r, c in posiciones:
            if random.random() < 0.15: self.grid[r][c]['pozo'] = True

        w_pos = random.choice(posiciones)
        self.grid[w_pos[0]][w_pos[1]]['wumpus'] = True
        o_pos = random.choice(posiciones)
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
        """Imprime el estado real del mundo y la posición del agente."""
        print("\n--- ESTADO DEL MUNDO ---")
        for r in range(self.size - 1, -1, -1):  # Invertir para que (0,0) sea abajo-izq
            fila = "|"
            for c in range(self.size):
                char = ""
                if (r, c) == pos_agente: char += "A"  # Agente
                if self.grid[r][c]['wumpus']: char += "W"
                if self.grid[r][c]['pozo']: char += "P"
                if self.grid[r][c]['oro']: char += "G"

                # Relleno para mantener alineación
                fila += char.center(4) + "|"
            print(fila)
            print("-" * (self.size * 6))
        print("Leyenda: A=Agente, W=Wumpus, P=Pozo, G=Oro\n")

    def obtener_percepcion(self, r, c):
        return self.grid[r][c]

    def disparar(self, r, c):
        if self.grid[r][c]['wumpus']:
            self.grid[r][c]['wumpus'] = False
            # Actualizar percepciones
            for nr, nc in self.get_adjacentes(r, c):
                self.grid[nr][nc]['hedor'] = False
            return True
        return False


class AgenteLogico:
    def __init__(self, size=6):
        self.size = size
        self.pos_actual = (0, 0)
        self.visitados = set()
        self.seguras = set([(0, 0)])
        self.wumpus_vivo = True
        self.posible_wumpus = set()
        self.peligros = set()
        self.kb = {(r, c): {'p_pozo': 'u', 'p_wumpus': 'u'} # 'u': desconocido, 's': seguro, 'p': peligroso
                   for r in range(size) for c in range(size)}

    def integrar_percepcion(self, r, c, perc):
        self.visitados.add((r, c))
        self.seguras.add((r, c))
        adjacentes = mundo.get_adjacentes(r, c)

        # Lógica de inferencia
        if not perc['brisa'] and not perc['hedor']:
            for nr, nc in adjacentes:
                self.seguras.add((nr, nc))

                if (nr, nc) in self.peligros:
                    self.peligros.remove((nr, nc))
                if (nr, nc) in self.posible_wumpus:
                    self.posible_wumpus.remove((nr, nc))

        if perc['brisa'] and not perc['hedor']:
            for nr, nc in adjacentes:
                if (nr, nc) not in self.visitados:
                    self.peligros.add((nr, nc))

        if perc['hedor'] and not perc['brisa']:
            for nr, nc in adjacentes:
                if (nr, nc) not in self.visitados:
                    self.peligros.add((nr, nc))
                    self.posible_wumpus.add((nr, nc))

        if perc['brisa'] and perc ['hedor']:
            for nr, nc in adjacentes:
                if (nr, nc) not in self.visitados:
                    self.peligros.add((nr, nc))
                    self.posible_wumpus.add((nr, nc))

        if self.wumpus_vivo and len(self.posible_wumpus) == 1:
            print(f"¡Wumpus identificado en {list(self.posible_wumpus)[0]}! Disparando flecha...")
            w_pos = list(self.posible_wumpus)[0]
            if mundo.disparar(*w_pos):
                print("¡Wumpus eliminado!")
                self.wumpus_vivo = False
                self.posible_wumpus.clear()
                if not perc['brisa'] and not perc['hedor']:
                    for nr, nc in mundo.get_adjacentes(*w_pos):
                        self.seguras.add((nr, nc))
                else:
                    for nr, nc in mundo.get_adjacentes(*w_pos):
                        self.peligros.add((nr, nc))
            else:
                print("¡Fallo! El Wumpus sigue vivo.")

        print(
            f"Percepciones en {r, c}: {'Brisa ' if perc['brisa'] else ''}{'Hedor ' if perc['hedor'] else ''}{'Resplandor' if perc['resplandor'] else ''}")

    def planificar_siguiente_paso(self):
        opciones = [p for p in self.seguras if p not in self.visitados]
        if opciones:
            # Intentar ir a una adyacente primero
            for opt in opciones:
                if opt in mundo.get_adjacentes(*self.pos_actual):
                    return opt
            return opciones[0]
        return None


# --- Simulación Principal ---
mundo = WumpusWorld()
agente = AgenteLogico()

for turno in range(1, 30):
    print(f"*** MOVIMIENTO {turno} ***")
    mundo.imprimir_tablero(agente.pos_actual)

    r, c = agente.pos_actual
    percepcion = mundo.obtener_percepcion(r, c)

    agente.integrar_percepcion(r, c, percepcion)

    if percepcion['oro']:
        print("¡VICTORIA! El agente ha encontrado el Oro.")
        break

    proxima = agente.planificar_siguiente_paso()

    if proxima:
        agente.pos_actual = proxima
    else:
        print("RESULTADO: El agente no encuentra más caminos seguros. Fin de la simulación.")
        break