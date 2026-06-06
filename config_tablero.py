#Configuracion del tablero 


#Dimenciones del tablero 
WIDTH = 1250
HEIGHT = 700
#Colores del teblero 
# Colores para el fondo y el texto
color_rojo = (255, 0, 0)
color_verde = (0, 103,79)
color_fondo = (112, 110, 110)
COLOR_BG = (15, 15, 15)          
COLOR_FRAME = (37, 37, 37)  
COLOR_TEXT = (255, 255, 255)
COLOR_SIN = (240,100,50)   
COLOR_MAR = (139,0,0)
COLOR_AZUL = (65,105,225)

# Colores de los elementos del juego
COLOR_AGENT = (7, 7, 56)    # Celeste / Azul claro (A)
COLOR_WUMPUS = (255, 70, 70)     # Rojo (W)
COLOR_GOLD = (255, 215, 0)       # Dorado / Amarillo (O)
COLOR_PIT = (17, 17, 132)       # Morado / Portal (P)
COLOR_EFFECT = (100, 240, 100)   # Verde para Hedor/Brisa (H)
COLOR_UNKNOWN = (6,64,43)       # verde  para las casillas ocultas (?)
COLOR_PWUMPUS = (255, 165, 0)      # Naranja para Wumpus + Pozo (WP)
COLOR_PA = (53, 56, 57)             # Magenta para Agente + Pozo (AP)
COLOR_VISITADO = (37, 37, 37)

# Dimensiones de las cuadrículas del tablero de mundo real y conocimiento del agente
CELL_SIZE = 30

#Tiempo de actualizacion por movimiento
DELAY_MOVIMIENTO = 1000  # 1 segundos entre movimientos

#Configuracion del juego 
TURNO_ACTUAL = 1
JUEGO_TERMINADO = False
VICTORIA = False
SIN_CAMINOS = False
AGENTE_DEBORADO = False

#Tamanio del rectangulo
RECT_ALEATORIO = (40, 40, 500, 300)
RECT_LOGICO = (700, 40, 500, 300)
RECT_ASTAR = (350, 360, 500, 300)

#Verificar si wumpus esta vivo o muerto
WUMPUS_MUERTO_UNO = False
WUMPUS_MUERTO_DOS = False

 






