import random
class AgenteAleatorio:
    def __init__(self, mundo, size=6):
        self.mundo = mundo
        self.size = size
        self.pos_actual = (0, 0)
        self.visitados = set()
        #Ver si el wuampus esta vivo
        self.wumpus_vivo = True
        #Camino recorrido
        self.camino = [[0,0]]
        #posibles wumpus
        self.posibles_wumpus = set()
        #Como es aleatorio se le dara una cantidad de flechas 
        self.flehas = 2
         

    #Intregar la percepsion pero sin reglas de inferencia
    def integrar_percepcion(self, r, c, perc):
        self.visitados.add((r,c))
        adjacentes = self.mundo.get_adjacentes(r, c)
        #Regla de inferencia para matar al wumpus
        if perc['hedor']:
            for nr, nc in adjacentes:
                if (nr, nc) not in self.visitados:
                    self.posibles_wumpus.add((nr, nc))
        #Intentar matar al wumpus 
        if self.wumpus_vivo and self.flehas > 0 and len(self.posibles_wumpus) > 0:
            #Al no tener reglas se dispara la flecha de manera aleatoria
            w_pos = random.choice(list(self.posibles_wumpus))
            print(f"Posible wumpus en {w_pos} Disparando flecha...")
            if self.mundo.disparar(*w_pos):
                self.flehas -= 1
                print("Wumpus muerto")
                self.wumpus_vivo = False
                self.posibles_wumpus.clear
            else:
                self.flehas -= 1
                print("Wumpus sigue vivo fallaste el disparo")
                self.posibles_wumpus.discard(w_pos)
                  
        print(
            f"Percepciones en {(r, c)}: "
            f"{'Brisa ' if perc['brisa'] else ''}"
            f"{'Hedor ' if perc['hedor'] else ''}"
            f"{'Resplandor' if perc['resplandor'] else ''}"
        )
    
    def planificar_movimiento(self):
        adyacentes = self.mundo.get_adjacentes(*self.pos_actual)
        no_visitadas = [
            p for p in adyacentes
            if p not in self.visitados
        ]
        #Evita que de vueltas 
        if no_visitadas:
            return random.choice(no_visitadas)
        return random.choice(adyacentes)
    

    #Mostrar el mundo del agente aleatorio
    def mostrar_mundo(self):
        print("\n=== CONOCIMIENTO DEL AGENTE ALEATORIO ===\n")
        for r in reversed(range(self.size)):
            for c in range(self.size):
                if (r,c) == self.pos_actual:
                    print(" A ", end="")
                elif (r, c) in self.visitados:
                    print(" V ", end="")
                else:
                    print(" ? ", end="")
            print()
