import pygame
import sys
from mundo import WumpusWorld
from AgenteAleatorio import AgenteAleatorio
from config import *


mundo = WumpusWorld()
agente = AgenteAleatorio(mundo)

# 'A' = Agente, 'W' = Wumpus, 'O' = Oro, 'P' = Pozo, '?' = Desconocido, 'WP' = Wumpus + Pozo
# La posicion del agente al iniciar el juego es (0, 0)
r,c = agente.pos_actual
#Representación visual del mundo real y el conocimiento del agente
mundo_real = mundo.obtener_matriz_visual(pos_agente=(r, c))
#Representacion del conocimiento del agente, inicialmente desconocido
conocimiento_agente = agente.convertir_mundo_agente_a_matriz()

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla alto y ancho
WIDTH = 1250
HEIGHT = 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mundo de Wumpus")
clock = pygame.time.Clock()

# Fuentes y Colores
fuente_game_over = pygame.font.SysFont("Arial", 60)
color_rojo = (255, 0, 0)
color_fondo = (0, 0, 0)

# Colores
COLOR_BG = (15, 15, 15)          
COLOR_FRAME = (240, 240, 240)  
COLOR_TEXT = (255, 255, 255)   

# Colores de los elementos del juego
COLOR_AGENT = (50, 180, 255)     # Celeste / Azul claro (A)
COLOR_WUMPUS = (255, 70, 70)     # Rojo (W)
COLOR_GOLD = (255, 215, 0)       # Dorado / Amarillo (O)
COLOR_PIT = (160, 80, 255)       # Morado / Portal (P)
COLOR_EFFECT = (100, 240, 100)   # Verde para Hedor/Brisa (H)
COLOR_UNKNOWN = (0, 128,0)       # verde  para las casillas ocultas (?)
COLOR_PWUMPUS = (255, 165, 0)      # Naranja para Wumpus + Pozo (WP)

# Configuración de Fuentes
#Tam para el titulo
font_title = pygame.font.SysFont("Courier", 18, bold=True)
#Tam de la fuente del tablero 
font_cell = pygame.font.SysFont("Courier", 22, bold=True)


# Dimensiones de las cuadrículas del tablero de mundo real y conocimiento del agente
GRID_SIZE = TAMANIO_MUNDO 
CELL_SIZE = 30

#control del juego
turno_actual = 0
juego_terminado = False
victoria = False
#Tiempo en lo que se va a mover
DELAY_MOVIMIENTO = 2000  # 2 segundos entre movimientos
ultimo_movimiento = pygame.time.get_ticks()  # Tiempo del último movimiento

#Dibujar celdas del tablero 
def draw_grid_cells(start_x, start_y, grid_data):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            element = grid_data[row][col]
            if not element:
                continue
            # Asignar color según el elemento
            if element == "A":
                color = COLOR_AGENT
            elif element == "W":
                color = COLOR_WUMPUS
            elif element == "O":
                color = COLOR_GOLD
            elif element == "P":
                color = COLOR_PIT
            elif element == "WP":
                color = COLOR_PWUMPUS
            elif element == "?":
                color = COLOR_UNKNOWN
            else:
                color = COLOR_TEXT

            # Renderizar y centrar el texto en la celda
            text_surf = font_cell.render(element, True, color)
            text_rect = text_surf.get_rect(center=(
                start_x + col * CELL_SIZE + CELL_SIZE // 2,
                start_y + row * CELL_SIZE + CELL_SIZE // 2
            ))
            screen.blit(text_surf, text_rect)
# Dibujar la interfaz
def draw_interface():
    # Dibujar el marco del juego el rectangulo
    outer_rect = pygame.Rect(40, 40, 500, 300)
    pygame.draw.rect(screen, COLOR_FRAME, outer_rect, 2)
    # Centro real del rectángulo
    center_x = outer_rect.x + outer_rect.width // 2
    # Línea divisoria central del rectángulo para separar mundo real y conocimiento del agente
    pygame.draw.line(
    screen,
    COLOR_FRAME,
    (center_x, outer_rect.y),
    (center_x, outer_rect.y + outer_rect.height),2)

# Línea horizontal de títulos
    pygame.draw.line(
    screen,
    COLOR_FRAME,
    (outer_rect.x, outer_rect.y + 55),
    (outer_rect.x + outer_rect.width, outer_rect.y + 55),
    2
    ) 
    # Títulos
    title_real = font_title.render("MUNDO REAL", True, COLOR_TEXT)
    title_agent = font_title.render("CONOCIMIENTO AGENTE", True, COLOR_TEXT)
    # Cada sección mide 300 px
    section_width = outer_rect.width // 2
    screen.blit(
        title_real,
        (
            outer_rect.x +
            (section_width - title_real.get_width()) // 2,
            60
        )
    )

    screen.blit(
        title_agent,
        (
            center_x +
            (section_width - title_agent.get_width()) // 2,
            60
        )
    )

    # Tamaño total de la cuadrícula
    grid_w_h = GRID_SIZE * CELL_SIZE
    # Centrar cuadrícula izquierda
    left_grid_x = outer_rect.x + (section_width - grid_w_h) // 2
    # Centrar cuadrícula derecha
    right_grid_x = center_x + (section_width - grid_w_h) // 2
    grid_y = 110
    # Dibujar cuadrículas para mundo real y conocimiento del agente
    for start_x in [left_grid_x, right_grid_x]:
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(
                screen,
                COLOR_FRAME,
                (start_x + i * CELL_SIZE, grid_y),
                (start_x + i * CELL_SIZE, grid_y + grid_w_h),
                1
            )
            pygame.draw.line(
                screen,
                COLOR_FRAME,
                (start_x, grid_y + i * CELL_SIZE),
                (start_x + grid_w_h, grid_y + i * CELL_SIZE),
                1
            )
    # Contenido
    draw_grid_cells(left_grid_x, grid_y, mundo_real)
    draw_grid_cells(right_grid_x, grid_y, conocimiento_agente)# Bucle principal de la aplicación, termina al cerrar la ventan


#Actualizar el mundo y el conocimiento del agente en cada turno
def actualizar_mundo_y_conocimiento():
    global turno_actual
    global juego_terminado
    global mundo_real
    global conocimiento_agente
    global victoria

    if juego_terminado:
        return
    if turno_actual > TURNOS_MAXIMOS:
        juego_terminado = True
        return

    print(f"\n*** MOVIMIENTO {turno_actual} ***")

    if turno_actual % 3 == 0:

        mundo.mover_wumpus()

        print("Los Wumpus se han movido...")

    if turno_actual % 4 == 0:

        nuevo_pozo = (mundo.agregar_pozo_aleatorio())
        if nuevo_pozo:
            print(f"Nuevo pozo en {nuevo_pozo}")
    r, c = agente.pos_actual

    percepcion = (mundo.obtener_percepcion(r,c))

    agente.integrar_percepcion(r,c,percepcion)
    if percepcion["oro"]:
        print("¡VICTORIA!")
        juego_terminado = True
        victoria = True
        return
    if percepcion["pozo"]:
        print("El agente cayó en un pozo")
        juego_terminado = True
        victoria = False
        return
    proxima = (agente.planificar_siguiente_paso())

    if proxima:
        agente.pos_actual = proxima
        agente.camino.append(list(proxima))
    else:
        print("No hay movimientos posibles")
        juego_terminado = True
        return

    r, c = agente.pos_actual
    #Acrutalizar el mundo real y el conocimiento del agente
    mundo_real = (mundo.obtener_matriz_visual(pos_agente=(r, c)))
    conocimiento_agente = (agente.convertir_mundo_agente_a_matriz())
    agente.mostrar_mundo_agente()
    #Aumentar el turno actual
    turno_actual += 1
    
#Mostrar el mensaje de victoria o juego perdido 
def Mensaje(cadena, color_rojo):
    texto = fuente_game_over.render(
        cadena,
        True,
        color_rojo
    )
    rect = texto.get_rect(
        center=(WIDTH//2, HEIGHT//2)
    )
    screen.blit(texto, rect)


# ==================================================
# MAIN
# ==================================================

def main():
    global ultimo_movimiento
    global juego_terminado
    global victoria

    running = True

    while running:
        screen.fill(COLOR_BG)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        tiempo_actual = pygame.time.get_ticks()

        if tiempo_actual - ultimo_movimiento >= DELAY_MOVIMIENTO:
            actualizar_mundo_y_conocimiento()
            ultimo_movimiento = tiempo_actual

        draw_interface()

        if juego_terminado and victoria == False:
            Mensaje("GAME OVER", color_rojo)
        if victoria:
            Mensaje("¡VICTORIA!", (0, 255, 0))  # Verde para victoria
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

    sys.exit()

if __name__ == "__main__":
    main()