import pygame
import sys
from mundo import WumpusWorld
from AgenteAleatorio import AgenteAleatorio
from agente import AgenteLogico
from agente_astar import AgenteAStar
from config import *
from puntuaciones import *
from config_tablero import *

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
conocimiento_agente = agente.mostrar_mundo_matriz()

#Agente lógico
# La posicion del agente lógico al iniciar el juego es (0, 0)
r_logico, c_logico = agente_logico.pos_actual
#Representación visual del mundo real para el agente lógico
mundo_real_logico = mundo.obtener_matriz_visual(pos_agente=(r_logico, c_logico))
#Representacion del conocimiento del agente lógico, inicialmente desconocido
conocimiento_agente_logico = agente_logico.mostrar_mundo_matriz()


#Agente astar 
# La posicion del agente astar al iniciar el juego es (0, 0)
r_astar, c_astar = agente_astar.pos_actual
mundo_real_astar = mundo.obtener_matriz_visual(pos_agente=(r_astar, c_astar))
conocimiento_agente_astar = agente_astar.mostrar_mundo_matriz()


# Inicializar Pygame
pygame.init()

# Configuración de la pantalla alto y ancho
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mundo de Wumpus")
clock = pygame.time.Clock()

# Fuente de mensaje de victoria o derrota
fuente_game_over = pygame.font.SysFont("Arial", 60)
#Tam para el titulo
font_title = pygame.font.SysFont("Courier", 18, bold=True)
#Tam de la fuente del tablero 
font_cell = pygame.font.SysFont("Courier", 22, bold=True)
# Tiempo del último movimiento
ultimo_movimiento = pygame.time.get_ticks() 


#Dibujar celdas del tablero 
def draw_grid_cells(start_x, start_y, grid_data):
    #Dibuja la matriz del juego de 6x6, asignando un color a cada elemento y centrando el texto en cada celda
    for row in range(TAMANIO_MUNDO):
        for col in range(TAMANIO_MUNDO):
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
            elif element == "?":
                color = COLOR_UNKNOWN
            elif element == "V":
                color = COLOR_VISITADO
            elif element == "AP":
                color = COLOR_PA
            elif element == "S":
                color = COLOR_VISITADO
            else:
                color = COLOR_TEXT

            # Renderizar y centrar el texto en la celda
            text_surf = font_cell.render(element, True, color)
            text_rect = text_surf.get_rect(center=(
                start_x + col * CELL_SIZE + CELL_SIZE // 2,
                start_y + row * CELL_SIZE + CELL_SIZE // 2
            ))
            screen.blit(text_surf, text_rect)
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
    grid_w_h = TAMANIO_MUNDO * CELL_SIZE
    # Centrar cuadrícula izquierda
    left_grid_x = rect_agente.x + (section_width - grid_w_h) // 2
    # Centrar cuadrícula derecha
    right_grid_x = center_x + (section_width - grid_w_h) // 2
    
    # Posición Y de la cuadrícula (¡CAMBIADO: Ahora es relativa al rectángulo del agente!)
    grid_y = rect_agente.y + 80
    
    # Dibujar cuadrículas para mundo real y conocimiento del agente
    for start_x in [left_grid_x, right_grid_x]:
        for i in range(TAMANIO_MUNDO + 1):
            pygame.draw.line(screen, COLOR_FRAME, (start_x + i * CELL_SIZE, grid_y), (start_x + i * CELL_SIZE, grid_y + grid_w_h), 1)
            pygame.draw.line(screen, COLOR_FRAME, (start_x, grid_y + i * CELL_SIZE), (start_x + grid_w_h, grid_y + i * CELL_SIZE), 1)
            
    # Contenido
    draw_grid_cells(left_grid_x, grid_y, mundo_real)
    draw_grid_cells(right_grid_x, grid_y, conocimiento_agente)
     
def actualizar_agente(agente_actual, mundo_real_ref, conocimiento_ref):
    global JUEGO_TERMINADO
    global TURNO_ACTUAL
    global AGENTE_DEBORADO
    global VICTORIA
    global SIN_CAMINOS
    global WUMPUS_MUERTO_UNO
    global WUMPUS_MUERTO_DOS

    if JUEGO_TERMINADO:
        return mundo_real_ref, conocimiento_ref
    if TURNO_ACTUAL > TURNOS_MAXIMOS:
        JUEGO_TERMINADO = True
        return mundo_real_ref, conocimiento_ref
    print(f"\n*** MOVIMIENTO {TURNO_ACTUAL} ***")
    TURNO_ACTUAL += 1
    agente_actual.puntuacion += PUNTOS_MOVIMIENTO
    # Movimiento de Wumpus
    if TURNO_ACTUAL % FRECUENCIA_MOVIMIENTO_WUMPUS == 0:
        #Mover wumpus
        mundo.mover_wumpus()
        #Manejo de dos agentes
        # Si el agente lógico tiene posibles posiciones de Wumpus, las limpia
        if hasattr(agente_actual, "posible_wumpus"):
            agente_actual.posible_wumpus.clear()
        # Si otro agente usa posibles posiciones de Wumpus, también las limpia
        if hasattr(agente_actual, "posibles_wumpus"):
            agente_actual.posibles_wumpus.clear()
        # Si el agente tiene base de conocimiento
        if hasattr(agente_actual, "kb"):
            # Recorre todas las posiciones de la base de conocimiento
            for pos in agente_actual.kb:
                 # Si alguna posición estaba marcada como posible Wumpus
                if agente_actual.kb[pos]["p_wumpus"] == "p":
                    # La regresa a desconocida porque el Wumpus se movió
                    agente_actual.kb[pos]["p_wumpus"] = "u"
        print("Los Wumpus se han movido...")
    # Aparición de nuevo pozo
    if TURNO_ACTUAL % FRECUENCIA_NUEVO_POZO == 0:
        #Agregando un pozo aleatorio, evitantando la posicion del wumpus o agente  
        nuevo_pozo = mundo.agregar_pozo_aleatorio(agente_actual.pos_actual)
        if nuevo_pozo:
              # Si el agente maneja un conjunto de peligros
            if hasattr(agente_actual, "peligros"):
                # Agrega el nuevo pozo como peligro conocido
                agente_actual.peligros.add(nuevo_pozo)
            #Si el agente maneja caminos seguros
            if hasattr(agente_actual, "seguras"):
                #Remuevo el camino seguro
                agente_actual.seguras.discard(nuevo_pozo)
            if hasattr(agente_actual, "kb"):
                agente_actual.kb[nuevo_pozo]["p_pozo"] = "p"
             # Informa dónde apareció el nuevo pozo
            print(f"Ha aparecido un nuevo pozo en {nuevo_pozo}")
   
    # Muestra el tablero real del mundo
    mundo.imprimir_tablero(agente_actual.pos_actual)
    # Posición actual
    r, c = agente_actual.pos_actual
    #Actualizo el mundo real del agente
    mundo_real_ref = mundo.obtener_matriz_visual(pos_agente=(r, c))
    #Obtner la percepcion
    percepcion = mundo.obtener_percepcion(r, c)
    #Integrar la percepcion del agente
    agente_actual.integrar_percepcion(r,c,percepcion)
    #Mostar el mundo del agente
    agente_actual.mostrar_mundo_agente()
    #Actualizar el conocimiento del agente visualmemte
    conocimiento_ref = agente_actual.mostrar_mundo_matriz()
    
    #Verificar cuando el wumpus este muerto 
    if agente_actual.wumpus_restantes == 1 and WUMPUS_MUERTO_UNO == False:
        print("Wumpus muerto")
        WUMPUS_MUERTO_UNO = True
        draw_interface(pygame.Rect(RECT_ALEATORIO), mundo_real_ref, conocimiento_ref)
        draw_interface(pygame.Rect(RECT_ASTAR), mundo_real_ref, conocimiento_ref)
        draw_interface(pygame.Rect(RECT_LOGICO), mundo_real_ref, conocimiento_ref)
        menssage("Wumpus muerto, queda 1", COLOR_AZUL)
        #Pygame lo muestra en la pantalla
        pygame.display.flip()
        #Pausamos la ejecucion por dos segundos
        pygame.time.delay(2000)
    if agente_actual.wumpus_restantes == 0 and WUMPUS_MUERTO_DOS == False:
        print("Wumpus muerto")
        WUMPUS_MUERTO_DOS = True
        draw_interface(pygame.Rect(RECT_ALEATORIO), mundo_real_ref, conocimiento_ref)
        draw_interface(pygame.Rect(RECT_ASTAR), mundo_real_ref, conocimiento_ref)
        draw_interface(pygame.Rect(RECT_LOGICO), mundo_real_ref, conocimiento_ref)
        menssage("Wumpus eliminados", COLOR_AZUL)
        pygame.display.flip()
        pygame.time.delay(2000)
    # Verificar pozo
    if percepcion["pozo"]:
        agente_actual.puntuacion += PUNTOS_CAER_POZO
        print("El agente cayó en un pozo.")
        JUEGO_TERMINADO = True     
        return mundo_real_ref, conocimiento_ref
    # Verificar Wumpus
    if percepcion["wumpus"]:
        agente_actual.puntuacion += PUNTOS_MORIR
        print("El agente fue devorado por el Wumpus.")
        AGENTE_DEBORADO = True
        JUEGO_TERMINADO = True
        return mundo_real_ref, conocimiento_ref
    # Verificar oro
    if percepcion["oro"]:
        agente_actual.puntuacion += PUNTOS_ORO
        print("¡VICTORIA! El agente ha encontrado el Oro.")
        VICTORIA = True
        JUEGO_TERMINADO = True
        return mundo_real_ref, conocimiento_ref
    # Calcular siguiente movimiento
    proxima = agente_actual.planificar_siguiente_paso()

    if proxima:
        agente_actual.pos_actual = proxima
        if hasattr(agente_actual, "camino"):
            agente_actual.camino.append(list(proxima))
        # Actualizar la matriz al moverse
        r, c = agente_actual.pos_actual
        mundo_real_ref = mundo.obtener_matriz_visual(pos_agente=(r, c))
        conocimiento_ref = agente_actual.mostrar_mundo_matriz()
    else:
        print("RESULTADO: El agente no encuentra más caminos seguros.")
        SIN_CAMINOS = True
        JUEGO_TERMINADO = True

    return mundo_real_ref, conocimiento_ref

#Mostrar el mensaje de victoria o juego perdido 
def menssage(cadena, color):
    texto = fuente_game_over.render(cadena,True,color)
    rect = texto.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(texto, rect)

#Mostar puntuacion
def mostrar_puntuacion(agente_actual):
    puntuacion = 0
    if agente_actual == "ALEATORIO":
        puntuacion = agente.puntuacion
    if agente_actual == "LOGICO":
        puntuacion = agente_logico.puntuacion
    if agente_actual == "ASTAR":
        puntuacion = agente_astar.puntuacion
    fuente_puntuacion = pygame.font.SysFont("Arial", 40)
    texto = fuente_puntuacion.render(f"Puntuación: {puntuacion}", True, COLOR_FRAME)
    rect = texto.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
    screen.blit(texto, rect)
def main():
    global ultimo_movimiento
    global conocimiento_agente, mundo_real
    global conocimiento_agente_logico, mundo_real_logico
    global conocimiento_agente_astar, mundo_real_astar 
    global JUEGO_TERMINADO, VICTORIA, AGENTE_DEBORADO, SIN_CAMINOS, TURNO_ACTUAL,WUMPUS_MUERTO_UNO, WUMPUS_MUERTO_DOS
    
    # Tamaño y posición del rectángulo para el agente aleatorio
    rect_agente_aleatorio = pygame.Rect(RECT_ALEATORIO)
    # Tamaño y posición del rectángulo para el agente lógico
    rect_agente_logico = pygame.Rect(RECT_LOGICO)
    # Tamaño y posición del rectángulo para el agente astar
    rect_agente_astar = pygame.Rect(RECT_ASTAR) 

    running = True

    #Primier agente en ejecuatar
    agente_en_ejecucion = "ALEATORIO"
    #Tecla para continuar
    esperando_tecla = False
    while running:
        #Color de fondo
        screen.fill(color_fondo)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            #Para poder ejecuar opcion del tablero es con la tecla enter
                if event.key == pygame.K_RETURN and esperando_tecla:
                    #Por cada juego se reinicia
                    JUEGO_TERMINADO = False
                    VICTORIA = False
                    AGENTE_DEBORADO = False
                    TURNO_ACTUAL = 1
                    #Actualizar el estado del wumpus 
                    WUMPUS_MUERTO_UNO = False
                    WUMPUS_MUERTO_DOS = False
                    if agente_en_ejecucion == "ALEATORIO":
                        agente_en_ejecucion = "LOGICO"
                    elif agente_en_ejecucion == "LOGICO":
                        agente_en_ejecucion = "ASTAR"
                    #Cada vez que se precione la tecla cambia a false
                    esperando_tecla = False
                    ultimo_movimiento = pygame.time.get_ticks() 
                    
        tiempo_actual = pygame.time.get_ticks()
        #Hazta que no termine el juego cambia el estado
        if not esperando_tecla:
            if tiempo_actual - ultimo_movimiento >= DELAY_MOVIMIENTO:
                #Agente aleatorio 
                if agente_en_ejecucion == "ALEATORIO":
                # Mover el agente del tablero 
                    mundo_real, conocimiento_agente = actualizar_agente(
                        agente_actual=agente,
                        mundo_real_ref=mundo_real,
                        conocimiento_ref=conocimiento_agente
                    )
                    if JUEGO_TERMINADO:
                        esperando_tecla = True
                #Agente logio
                elif agente_en_ejecucion == "LOGICO":
                    mundo_real_logico, conocimiento_agente_logico = actualizar_agente(
                        agente_actual=agente_logico,
                        mundo_real_ref=mundo_real_logico,
                        conocimiento_ref=conocimiento_agente_logico
                    )
                    if JUEGO_TERMINADO:
                        esperando_tecla = True
                #Agente Astar
                elif agente_en_ejecucion == "ASTAR":
                    mundo_real_astar, conocimiento_agente_astar = actualizar_agente(
                        agente_actual=agente_astar,
                        mundo_real_ref=mundo_real_astar,
                        conocimiento_ref=conocimiento_agente_astar
                    )
                    if JUEGO_TERMINADO:
                        esperando_tecla = True
                ultimo_movimiento = tiempo_actual
            # Dibujar las 3 interfaces de los agentes
            draw_interface(rect_agente=rect_agente_aleatorio, mundo_real=mundo_real, conocimiento_agente=conocimiento_agente)
            draw_interface(rect_agente=rect_agente_logico, mundo_real=mundo_real_logico, conocimiento_agente=conocimiento_agente_logico)
            draw_interface(rect_agente=rect_agente_astar, mundo_real=mundo_real_astar, conocimiento_agente=conocimiento_agente_astar)

            if VICTORIA:
                menssage("¡WINNER!", color_verde)
                mostrar_puntuacion(agente_en_ejecucion)

            elif SIN_CAMINOS:
                menssage("¡SIN CAMINOS!", COLOR_SIN)
                mostrar_puntuacion(agente_en_ejecucion)

            elif AGENTE_DEBORADO:
                menssage("WUMPUS ELIMINO AL AGENTE", COLOR_MAR)
                mostrar_puntuacion(agente_en_ejecucion)

            elif JUEGO_TERMINADO:
                menssage("¡GAME OVER!", color_rojo)
                mostrar_puntuacion(agente_en_ejecucion)
            
            pygame.display.flip()
            clock.tick(60)

    pygame.quit()

    sys.exit()

if __name__ == "__main__":
    main()