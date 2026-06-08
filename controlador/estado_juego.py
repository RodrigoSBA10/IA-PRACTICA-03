# Clase para mantener el estado del juego
class EstadoJuego:
    # Inicializa el estado del juego
    def __init__(self):
        self.turno_actual = 1
        self.juego_terminado = False
        self.victoria = False
        self.sin_caminos = False
        self.agente_devorado = False
        self.wumpus_muerto_uno = False
        self.wumpus_muerto_dos = False
    # Reinicia el estado del juego a su estado inicial
    def reiniciar(self):
        self.turno_actual = 1
        self.juego_terminado = False
        self.victoria = False
        self.sin_caminos = False
        self.agente_devorado = False
        self.wumpus_muerto_uno = False
        self.wumpus_muerto_dos = False