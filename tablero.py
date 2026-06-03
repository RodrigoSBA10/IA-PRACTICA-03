import pygame
import sys
from mundo import WumpusWorld
from AgenteAleatorio import AgenteAleatorio
from agente import AgenteLogico
from agente_astar import AgenteAStar
from config import *

#Mundo para los 3 agentes
mundo = WumpusWorld()
#Agente aleatorio
agente = AgenteAleatorio(mundo)
#Agente lógico
agente_logico = AgenteLogico(mundo)
#Agente A*
agente_astar = AgenteAStar(mundo)

# Agente aleatorio
# La posicion del agente al iniciar el juego es (0, 0)
r,c = agente.pos_actual
#Representación visual del mundo real y el conocimiento del agente
mundo_real = mundo.obtener_matriz_visual(pos_agente=(r, c))
#Representacion del conocimiento del agente, inicialmente desconocido
conocimiento_agente = agente.convertir_mundo_agente_a_matriz()

#Agente lógico
# La posicion del agente lógico al iniciar el juego es (0, 0)
r_logico, c_logico = agente_logico.pos_actual
#Representación visual del mundo real para el agente lógico
mundo_real_logico = mundo.obtener_matriz_visual(pos_agente=(r_logico, c_logico))
#Representacion del conocimiento del agente lógico, inicialmente desconocido
conocimiento_agente_logico = agente_logico.convertir_mundo_agente_a_matriz()


#Agente astar 
# La posicion del agente astar al iniciar el juego es (0, 0)
r_astar, c_astar = agente_astar.pos_actual
mundo_real_astar = mundo.obtener_matriz_visual(pos_agente=(r_astar, c_astar))
conocimiento_agente_astar = agente_astar.mostrar_mundo_matriz()


# Inicializar Pygame
pygame.init()

# Configuración de la pantalla alto y ancho
WIDTH = 1250
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mundo de Wumpus")
clock = pygame.time.Clock()

# Fuente de mensaje de victoria o derrota
fuente_game_over = pygame.font.SysFont("Arial", 60)
#Tam para el titulo
font_title = pygame.font.SysFont("Courier", 18, bold=True)
#Tam de la fuente del tablero 
font_cell = pygame.font.SysFont("Courier", 22, bold=True)


# Colores para el fondo y el texto
color_rojo = (255, 0, 0)
color_verde = (0, 103,79)
color_fondo = (106, 137, 167)
COLOR_BG = (15, 15, 15)          
COLOR_FRAME = (37, 37, 37)  
COLOR_TEXT = (255, 255, 255)   

# Colores de los elementos del juego
COLOR_AGENT = (7, 7, 56)    # Celeste / Azul claro (A)
COLOR_WUMPUS = (255, 70, 70)     # Rojo (W)
COLOR_GOLD = (255, 215, 0)       # Dorado / Amarillo (O)
COLOR_PIT = (17, 17, 132)       # Morado / Portal (P)
COLOR_EFFECT = (100, 240, 100)   # Verde para Hedor/Brisa (H)
COLOR_UNKNOWN = (46, 111,64)       # verde  para las casillas ocultas (?)
COLOR_PWUMPUS = (255, 165, 0)      # Naranja para Wumpus + Pozo (WP)
COLOR_PA = (53, 56, 57)             # Magenta para Agente + Pozo (AP)

# Dimensiones de las cuadrículas del tablero de mundo real y conocimiento del agente
GRID_SIZE = TAMANIO_MUNDO 
CELL_SIZE = 30

#control del juego
turno_actual = 0
#Cuando el juego termina, ya sea por victoria o derrota, se detiene el ciclo principal y se muestra el mensaje correspondiente
juego_terminado = False
#Si el jugador gana
victoria = False


#Tiempo en lo que se va a mover
DELAY_MOVIMIENTO = 2000  # 2 segundos entre movimientos
ultimo_movimiento = pygame.time.get_ticks()  # Tiempo del último movimiento

#Dibujar celdas del tablero 
def draw_grid_cells(start_x, start_y, grid_data):
    #Dibuja la matriz del juego de 6x6, asignando un color a cada elemento y centrando el texto en cada celda
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
            elif element == "AP":
                color = COLOR_PA
            else:
                color = COLOR_TEXT

            # Renderizar y centrar el texto en la celda
            text_surf = font_cell.render(element, True, color)
            text_rect = text_surf.get_rect(center=(
                start_x + col * CELL_SIZE + CELL_SIZE // 2,
                start_y + row * CELL_SIZE + CELL_SIZE // 2
            ))
            screen.blit(text_surf, text_rect)


# Dibujar la interfaz de agente Aleatorio 
# Dibujar la interfaz de los agentes
def draw_interface(rect_agente, mundo_real, conocimiento_agente):
    # Dibujar el marco del juego el rectangulo del agente
    pygame.draw.rect(screen, COLOR_FRAME, rect_agente, 2)

    # Centro real del rectángulo
    center_x = rect_agente.x + rect_agente.width // 2
    
    # Línea divisoria central del rectángulo para separar mundo real y conocimiento del agente
    pygame.draw.line(screen, COLOR_FRAME, (center_x, rect_agente.y), (center_x, rect_agente.y + rect_agente.height), 2)

    # Línea horizontal de títulos (Relativa a rect_agente.y)
    pygame.draw.line(screen, COLOR_FRAME, (rect_agente.x, rect_agente.y + 55), (rect_agente.x + rect_agente.width, rect_agente.y + 55), 2) 
    
    # Títulos
    title_real = font_title.render("MUNDO REAL", True, COLOR_FRAME)
    title_agent = font_title.render("CONOCIMIENTO AGENTE", True, COLOR_FRAME)
    
    # Cada sección mide 300 px
    section_width = rect_agente.width // 2
    
    # Centrar títulos en cada sección (¡CAMBIADO AHORA USAN rect_agente.y!)
    screen.blit(title_real, (rect_agente.x + (section_width - title_real.get_width()) // 2, rect_agente.y + 20))
    screen.blit(title_agent, (center_x + (section_width - title_agent.get_width()) // 2, rect_agente.y + 20))

    # Tamaño total de la cuadrícula
    grid_w_h = GRID_SIZE * CELL_SIZE
    # Centrar cuadrícula izquierda
    left_grid_x = rect_agente.x + (section_width - grid_w_h) // 2
    # Centrar cuadrícula derecha
    right_grid_x = center_x + (section_width - grid_w_h) // 2
    
    # Posición Y de la cuadrícula (¡CAMBIADO: Ahora es relativa al rectángulo del agente!)
    grid_y = rect_agente.y + 80
    
    # Dibujar cuadrículas para mundo real y conocimiento del agente
    for start_x in [left_grid_x, right_grid_x]:
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(screen, COLOR_FRAME, (start_x + i * CELL_SIZE, grid_y), (start_x + i * CELL_SIZE, grid_y + grid_w_h), 1)
            pygame.draw.line(screen, COLOR_FRAME, (start_x, grid_y + i * CELL_SIZE), (start_x + grid_w_h, grid_y + i * CELL_SIZE), 1)
            
    # Contenido
    draw_grid_cells(left_grid_x, grid_y, mundo_real)
    draw_grid_cells(right_grid_x, grid_y, conocimiento_agente)

"""
#Actualizar el mundo y el conocimiento del agente aleatorio en cada turno
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
        #Mover wumpus del mundo
        mundo.mover_wumpus()
        # Si otro agente usa posibles posiciones de Wumpus, también las limpia
        if hasattr(agente, "posibles_wumpus"):
            agente.posibles_wumpus.clear()

        # Si el agente tiene base de conocimiento
        if hasattr(agente, "kb"):

            # Recorre todas las posiciones de la base de conocimiento
            for pos in agente.kb:

                # Si alguna posición estaba marcada como posible Wumpus
                if agente.kb[pos]["p_wumpus"] == "p":

                    # La regresa a desconocida porque el Wumpus se movió
                    agente.kb[pos]["p_wumpus"] = "u"
        
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
    r_a, r_c = agente_astar.pos_actual
    #Acrutalizar el mundo real y el conocimiento del agente
    mundo_real = (mundo.obtener_matriz_visual(pos_agente=(r, c)))
    conocimiento_agente = (agente.convertir_mundo_agente_a_matriz())
    agente.mostrar_mundo_agente()

    #Actualiza el mundo de astar
    mundo_real_astar= (mundo.obtener_matriz_visual(pos_agente=(r_a, r_c)))
    #Aumentar el turno actual
    turno_actual += 1

"""

def actualizar_mundo_y_conocimiento():
    global turno_actual
    global juego_terminado
    global victoria
    global mundo_real_astar
    global conocimiento_agente_astar

    if juego_terminado:
        return

    if turno_actual >= TURNOS_MAXIMOS:
        juego_terminado = True
        return

    print(f"\n*** MOVIMIENTO {turno_actual + 1} ***")

    # Penalización por movimiento
    agente_astar.puntuacion += PUNTOS_MOVIMIENTO

    # Mover Wumpus
    if (turno_actual + 1) % FRECUENCIA_MOVIMIENTO_WUMPUS == 0:

        mundo.mover_wumpus()

        if hasattr(agente_astar, "posible_wumpus"):
            agente_astar.posible_wumpus.clear()

        if hasattr(agente_astar, "posibles_wumpus"):
            agente_astar.posibles_wumpus.clear()

        if hasattr(agente_astar, "kb"):

            for pos in agente_astar.kb:

                if agente_astar.kb[pos]["p_wumpus"] == "p":
                    agente_astar.kb[pos]["p_wumpus"] = "u"

        print("Los Wumpus se han movido...")

    # Crear pozo nuevo
    if (turno_actual + 1) % FRECUENCIA_NUEVO_POZO == 0:

        nuevo_pozo = mundo.agregar_pozo_aleatorio(
            agente_astar.pos_actual
        )

        if nuevo_pozo:

            if hasattr(agente_astar, "peligros"):
                agente_astar.peligros.add(nuevo_pozo)

            if hasattr(agente_astar, "seguras"):
                agente_astar.seguras.discard(nuevo_pozo)

            if hasattr(agente_astar, "kb"):
                agente_astar.kb[nuevo_pozo]["p_pozo"] = "p"

            print(f"Ha aparecido un nuevo pozo en {nuevo_pozo}")

    # Posición actual
    r, c = agente_astar.pos_actual

    # Percepción
    percepcion = mundo.obtener_percepcion(r, c)

    # Actualizar conocimiento
    agente_astar.integrar_percepcion(r, c, percepcion)

    # ¿Murió?
    if percepcion["pozo"]:

        agente_astar.puntuacion += PUNTOS_CAER_POZO

        print("El agente cayó en un pozo")

        juego_terminado = True
        victoria = False

    elif percepcion["wumpus"]:

        agente_astar.puntuacion += PUNTOS_MORIR

        print("El agente fue devorado por el Wumpus")

        juego_terminado = True
        victoria = False

    elif percepcion["oro"]:

        agente_astar.puntuacion += PUNTOS_ORO

        print("¡VICTORIA!")

        juego_terminado = True
        victoria = True

    else:

        # Buscar siguiente movimiento
        proxima = agente_astar.planificar_siguiente_paso()

        if proxima:

            agente_astar.pos_actual = proxima

            if hasattr(agente_astar, "camino"):
                agente_astar.camino.append(list(proxima))

        else:

            print("No hay movimientos posibles")

            juego_terminado = True
            victoria = False

    # Actualizar tablero visual
    r, c = agente_astar.pos_actual

    mundo_real_astar = mundo.obtener_matriz_visual(
        pos_agente=(r, c)
    )

    conocimiento_agente_astar = (
        agente_astar.convertir_mundo_agente_a_matriz()
    )

    # Siguiente turno
    turno_actual += 1
    agente_astar.mostrar_mundo_agente()


#Mostrar el mensaje de victoria o juego perdido 
def menssage(cadena, color_rojo):
    texto = fuente_game_over.render(
        cadena,
        True,
        color_rojo
    )
    rect = texto.get_rect(
        center=(WIDTH//2, HEIGHT//2)
    )
    screen.blit(texto, rect)



def main():
    global ultimo_movimiento
    global juego_terminado
    global victoria

    # Tamaño y posición del rectángulo para el agente aleatorio
    rect_agente_aleatorio = pygame.Rect(40, 40, 500, 300)
    # Tamaño y posición del rectángulo para el agente lógico
    rect_agente_logico = pygame.Rect(700, 40, 500, 300)
    # Tamaño y posición del rectángulo para el agente astar
    rect_agente_astar = pygame.Rect(350, 360, 500, 300) 

    running = True

    while running:
        #Color de fondo
        screen.fill(color_fondo)

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
        # Dibujar las 3 interfaces de los agentes
        draw_interface(rect_agente=rect_agente_aleatorio, mundo_real=mundo_real, conocimiento_agente=conocimiento_agente)
        draw_interface(rect_agente=rect_agente_logico, mundo_real=mundo_real_logico, conocimiento_agente=conocimiento_agente_logico)
        draw_interface(rect_agente=rect_agente_astar, mundo_real=mundo_real_astar, conocimiento_agente=conocimiento_agente_astar)
        
        if juego_terminado and victoria == False:
            menssage("¡GAME OVER!", color_rojo)
        if victoria:
            menssage("¡WINNER!", color_verde)  
        
        pygame.display.flip()
        
        clock.tick(60)

    pygame.quit()

    sys.exit()

if __name__ == "__main__":
    main()