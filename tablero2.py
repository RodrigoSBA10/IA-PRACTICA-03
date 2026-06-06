import pygame
import sys
import copy

from mundo import WumpusWorld
from AgenteAleatorio import AgenteAleatorio
from agente import AgenteLogico
from agente_astar import AgenteAStar
from config import *
from puntuaciones import *
from config_tablero import *


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Mundo de Wumpus")
clock = pygame.time.Clock()

fuente_game_over = pygame.font.SysFont("Arial", 56, bold=True)
font_title = pygame.font.SysFont("Courier", 18, bold=True)
font_cell = pygame.font.SysFont("Courier", 22, bold=True)
font_boton = pygame.font.SysFont("Arial", 20, bold=True)
font_estado = pygame.font.SysFont("Arial", 24, bold=True)
font_score = pygame.font.SysFont("Arial", 22, bold=True)

ultimo_movimiento = pygame.time.get_ticks()

modo_mundos = "MISMO_MUNDO"
agente_en_ejecucion = "ALEATORIO"


def crear_mundos_y_agentes():
    global mundo_aleatorio, mundo_logico, mundo_astar
    global agente, agente_logico, agente_astar

    if modo_mundos == "MISMO_MUNDO":
        mundo_base = WumpusWorld()

        mundo_aleatorio = copy.deepcopy(mundo_base)
        mundo_logico = copy.deepcopy(mundo_base)
        mundo_astar = copy.deepcopy(mundo_base)

    else:
        mundo_aleatorio = WumpusWorld()
        mundo_logico = WumpusWorld()
        mundo_astar = WumpusWorld()

    agente = AgenteAleatorio(mundo_aleatorio)
    agente_logico = AgenteLogico(mundo_logico)
    agente_astar = AgenteAStar(mundo_astar)


def inicializar_matrices():
    global mundo_real, conocimiento_agente
    global mundo_real_logico, conocimiento_agente_logico
    global mundo_real_astar, conocimiento_agente_astar

    r, c = agente.pos_actual
    mundo_real = mundo_aleatorio.obtener_matriz_visual(pos_agente=(r, c))
    conocimiento_agente = agente.mostrar_mundo_matriz()

    r_logico, c_logico = agente_logico.pos_actual
    mundo_real_logico = mundo_logico.obtener_matriz_visual(
        pos_agente=(r_logico, c_logico)
    )
    conocimiento_agente_logico = agente_logico.mostrar_mundo_matriz()

    r_astar, c_astar = agente_astar.pos_actual
    mundo_real_astar = mundo_astar.obtener_matriz_visual(
        pos_agente=(r_astar, c_astar)
    )
    conocimiento_agente_astar = agente_astar.mostrar_mundo_matriz()


def reiniciar_estado_juego():
    global JUEGO_TERMINADO, VICTORIA, AGENTE_DEBORADO, SIN_CAMINOS
    global TURNO_ACTUAL, WUMPUS_MUERTO_UNO, WUMPUS_MUERTO_DOS
    global ultimo_movimiento

    JUEGO_TERMINADO = False
    VICTORIA = False
    AGENTE_DEBORADO = False
    SIN_CAMINOS = False
    TURNO_ACTUAL = 1
    WUMPUS_MUERTO_UNO = False
    WUMPUS_MUERTO_DOS = False
    ultimo_movimiento = pygame.time.get_ticks()


def reiniciar_todo():
    crear_mundos_y_agentes()
    inicializar_matrices()
    reiniciar_estado_juego()


crear_mundos_y_agentes()
inicializar_matrices()


def obtener_layout():
    ancho = screen.get_width()
    alto = screen.get_height()

    margen = 20
    barra_superior = 140
    espacio = 22

    ancho_panel = ancho - margen * 2
    alto_disponible = alto - barra_superior - margen

    alto_panel = (alto_disponible - espacio * 2) // 3

    rect_aleatorio = pygame.Rect(
        margen,
        barra_superior,
        ancho_panel,
        alto_panel
    )

    rect_logico = pygame.Rect(
        margen,
        barra_superior + alto_panel + espacio,
        ancho_panel,
        alto_panel
    )

    rect_astar = pygame.Rect(
        margen,
        barra_superior + (alto_panel + espacio) * 2,
        ancho_panel,
        alto_panel
    )

    return rect_aleatorio, rect_logico, rect_astar


def obtener_botones():
    return {
        "mismo": pygame.Rect(20, 15, 180, 38),
        "independiente": pygame.Rect(215, 15, 250, 38),
        "aleatorio": pygame.Rect(500, 15, 150, 38),
        "logico": pygame.Rect(665, 15, 130, 38),
        "astar": pygame.Rect(810, 15, 110, 38),
        "reiniciar": pygame.Rect(940, 15, 140, 38),
    }


def dibujar_boton(rect, texto, activo=False):
    if activo:
        color_boton = COLOR_AZUL
        color_texto = color_fondo
    else:
        color_boton = color_fondo
        color_texto = COLOR_FRAME

    pygame.draw.rect(screen, color_boton, rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_FRAME, rect, 2, border_radius=10)

    texto_render = font_boton.render(texto, True, color_texto)
    texto_rect = texto_render.get_rect(center=rect.center)
    screen.blit(texto_render, texto_rect)


def dibujar_botones():
    botones = obtener_botones()

    dibujar_boton(
        botones["mismo"],
        "Mismo mundo",
        modo_mundos == "MISMO_MUNDO"
    )

    dibujar_boton(
        botones["independiente"],
        "Mundos independientes",
        modo_mundos == "MUNDOS_INDEPENDIENTES"
    )

    dibujar_boton(
        botones["aleatorio"],
        "Aleatorio",
        agente_en_ejecucion == "ALEATORIO"
    )

    dibujar_boton(
        botones["logico"],
        "Lógico",
        agente_en_ejecucion == "LOGICO"
    )

    dibujar_boton(
        botones["astar"],
        "A*",
        agente_en_ejecucion == "ASTAR"
    )

    dibujar_boton(botones["reiniciar"], "Reiniciar")


def mostrar_estado_interfaz():
    texto = font_estado.render(
        f"Modo: {modo_mundos} | Agente activo: {agente_en_ejecucion}",
        True,
        COLOR_FRAME
    )

    screen.blit(texto, (20, 60))


def mostrar_puntuaciones_generales():
    textos = [
        f"Aleatorio: {agente.puntuacion}",
        f"Lógico: {agente_logico.puntuacion}",
        f"A*: {agente_astar.puntuacion}"
    ]

    x = 20
    y = 95

    for texto_score in textos:
        texto = font_score.render(texto_score, True, COLOR_FRAME)
        screen.blit(texto, (x, y))
        x += 190


def draw_grid_cells(start_x, start_y, grid_data):
    for row in range(TAMANIO_MUNDO):
        for col in range(TAMANIO_MUNDO):
            element = grid_data[row][col]

            if not element:
                continue

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
            elif element == "AW":
                color = COLOR_WUMPUS
            elif element == "WP":
                color = COLOR_WUMPUS
            else:
                color = COLOR_TEXT

            text_surf = font_cell.render(element, True, color)
            text_rect = text_surf.get_rect(
                center=(
                    start_x + col * CELL_SIZE + CELL_SIZE // 2,
                    start_y + row * CELL_SIZE + CELL_SIZE // 2
                )
            )

            screen.blit(text_surf, text_rect)


def draw_interface(rect_agente, mundo_real, conocimiento_agente, titulo_agente):
    pygame.draw.rect(screen, COLOR_FRAME, rect_agente, 2, border_radius=8)

    titulo = font_estado.render(titulo_agente, True, COLOR_FRAME)
    screen.blit(titulo, (rect_agente.x + 12, rect_agente.y - 28))

    center_x = rect_agente.x + rect_agente.width // 2

    pygame.draw.line(
        screen,
        COLOR_FRAME,
        (center_x, rect_agente.y),
        (center_x, rect_agente.y + rect_agente.height),
        2
    )

    pygame.draw.line(
        screen,
        COLOR_FRAME,
        (rect_agente.x, rect_agente.y + 55),
        (rect_agente.x + rect_agente.width, rect_agente.y + 55),
        2
    )

    title_real = font_title.render("MUNDO REAL", True, COLOR_FRAME)
    title_agent = font_title.render("CONOCIMIENTO AGENTE", True, COLOR_FRAME)

    section_width = rect_agente.width // 2

    screen.blit(
        title_real,
        (
            rect_agente.x + (section_width - title_real.get_width()) // 2,
            rect_agente.y + 20
        )
    )

    screen.blit(
        title_agent,
        (
            center_x + (section_width - title_agent.get_width()) // 2,
            rect_agente.y + 20
        )
    )

    grid_w_h = TAMANIO_MUNDO * CELL_SIZE

    left_grid_x = rect_agente.x + (section_width - grid_w_h) // 2
    right_grid_x = center_x + (section_width - grid_w_h) // 2
    grid_y = rect_agente.y + 80

    for start_x in [left_grid_x, right_grid_x]:
        for i in range(TAMANIO_MUNDO + 1):
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

    draw_grid_cells(left_grid_x, grid_y, mundo_real)
    draw_grid_cells(right_grid_x, grid_y, conocimiento_agente)


def actualizar_agente(agente_actual, mundo_actual, mundo_real_ref, conocimiento_ref):
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

    if TURNO_ACTUAL % FRECUENCIA_MOVIMIENTO_WUMPUS == 0:
        mundo_actual.mover_wumpus()
        if hasattr(agente_actual, "posibles_wumpus"):
            agente_actual.posibles_wumpus.clear()
        if hasattr(agente_actual, "seguras"):
            agente_actual.seguras.clear()
        if hasattr(agente_actual, "kb"):
            for pos in agente_actual.kb:
                if agente_actual.kb[pos]["p_wumpus"] == "p":
                    agente_actual.kb[pos]["p_wumpus"] = "u"

        print("Los Wumpus se han movido...")

    if TURNO_ACTUAL % FRECUENCIA_NUEVO_POZO == 0:
        mundo_actual.agregar_pozo_aleatorio( agente_actual.pos_actual )
        if hasattr(agente_actual, "peligros"):
            agente_actual.peligros.clear()
        if hasattr(agente_actual, "seguras"):
            agente_actual.seguras = set(agente_actual.visitados)
        if hasattr(agente_actual, "kb"):
            for pos in agente_actual.kb:
                if agente_actual.kb[pos]["p_pozo"] == "p":
                    agente_actual.kb[pos]["p_pozo"] = "u"
        print(f"Ha aparecido un nuevo pozo ")

    mundo_actual.imprimir_tablero(agente_actual.pos_actual)

    r, c = agente_actual.pos_actual

    mundo_real_ref = mundo_actual.obtener_matriz_visual(pos_agente=(r, c))

    percepcion = mundo_actual.obtener_percepcion(r, c)

    agente_actual.integrar_percepcion(r, c, percepcion)

    agente_actual.mostrar_mundo_agente()

    conocimiento_ref = agente_actual.mostrar_mundo_matriz()

    if hasattr(agente_actual, "wumpus_restantes"):
        if agente_actual.wumpus_restantes == 1 and WUMPUS_MUERTO_UNO is False:
            WUMPUS_MUERTO_UNO = True
            menssage("Wumpus muerto, queda 1", COLOR_AZUL)
            pygame.display.flip()
            pygame.time.delay(1200)

        if agente_actual.wumpus_restantes == 0 and WUMPUS_MUERTO_DOS is False:
            WUMPUS_MUERTO_DOS = True
            menssage("Wumpus eliminados", COLOR_AZUL)
            pygame.display.flip()
            pygame.time.delay(1200)

    if percepcion["pozo"]:
        agente_actual.puntuacion += PUNTOS_CAER_POZO
        print("El agente cayó en un pozo.")
        JUEGO_TERMINADO = True
        return mundo_real_ref, conocimiento_ref

    if percepcion["wumpus"]:
        agente_actual.puntuacion += PUNTOS_MORIR
        print("El agente fue devorado por el Wumpus.")
        AGENTE_DEBORADO = True
        JUEGO_TERMINADO = True
        return mundo_real_ref, conocimiento_ref

    if percepcion["oro"]:
        agente_actual.puntuacion += PUNTOS_ORO
        print("¡VICTORIA! El agente ha encontrado el Oro.")
        VICTORIA = True
        JUEGO_TERMINADO = True
        return mundo_real_ref, conocimiento_ref

    proxima = agente_actual.planificar_siguiente_paso()

    if proxima:
        agente_actual.pos_actual = proxima

        if hasattr(agente_actual, "camino"):
            if agente_actual.camino[-1] != list(proxima):
                agente_actual.camino.append(list(proxima))

        r, c = agente_actual.pos_actual
        mundo_real_ref = mundo_actual.obtener_matriz_visual(pos_agente=(r, c))
        conocimiento_ref = agente_actual.mostrar_mundo_matriz()

    else:
        print("RESULTADO: El agente no encuentra más caminos seguros.")
        SIN_CAMINOS = True
        JUEGO_TERMINADO = True

    return mundo_real_ref, conocimiento_ref


def menssage(cadena, color):
    texto = fuente_game_over.render(cadena, True, color)
    rect = texto.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(texto, rect)


def mostrar_puntuacion(agente_actual):
    puntuacion = 0

    if agente_actual == "ALEATORIO":
        puntuacion = agente.puntuacion

    if agente_actual == "LOGICO":
        puntuacion = agente_logico.puntuacion

    if agente_actual == "ASTAR":
        puntuacion = agente_astar.puntuacion

    fuente_puntuacion = pygame.font.SysFont("Arial", 40, bold=True)
    texto = fuente_puntuacion.render(f"Puntuación: {puntuacion}", True, COLOR_FRAME)
    rect = texto.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 + 80)
    )
    screen.blit(texto, rect)


def main():
    global ultimo_movimiento
    global conocimiento_agente, mundo_real
    global conocimiento_agente_logico, mundo_real_logico
    global conocimiento_agente_astar, mundo_real_astar
    global JUEGO_TERMINADO, VICTORIA, AGENTE_DEBORADO, SIN_CAMINOS
    global TURNO_ACTUAL, WUMPUS_MUERTO_UNO, WUMPUS_MUERTO_DOS
    global agente_en_ejecucion, modo_mundos
    global screen

    running = True

    while running:
        screen.fill(color_fondo)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    (event.w, event.h),
                    pygame.RESIZABLE
                )

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                botones = obtener_botones()

                if botones["mismo"].collidepoint(event.pos):
                    modo_mundos = "MISMO_MUNDO"
                    reiniciar_todo()

                elif botones["independiente"].collidepoint(event.pos):
                    modo_mundos = "MUNDOS_INDEPENDIENTES"
                    reiniciar_todo()

                elif botones["aleatorio"].collidepoint(event.pos):
                    agente_en_ejecucion = "ALEATORIO"
                    reiniciar_estado_juego()

                elif botones["logico"].collidepoint(event.pos):
                    agente_en_ejecucion = "LOGICO"
                    reiniciar_estado_juego()

                elif botones["astar"].collidepoint(event.pos):
                    agente_en_ejecucion = "ASTAR"
                    reiniciar_estado_juego()

                elif botones["reiniciar"].collidepoint(event.pos):
                    reiniciar_todo()

        tiempo_actual = pygame.time.get_ticks()

        if not JUEGO_TERMINADO:
            if tiempo_actual - ultimo_movimiento >= DELAY_MOVIMIENTO:

                if agente_en_ejecucion == "ALEATORIO":
                    mundo_real, conocimiento_agente = actualizar_agente(
                        agente_actual=agente,
                        mundo_actual=mundo_aleatorio,
                        mundo_real_ref=mundo_real,
                        conocimiento_ref=conocimiento_agente
                    )

                elif agente_en_ejecucion == "LOGICO":
                    mundo_real_logico, conocimiento_agente_logico = actualizar_agente(
                        agente_actual=agente_logico,
                        mundo_actual=mundo_logico,
                        mundo_real_ref=mundo_real_logico,
                        conocimiento_ref=conocimiento_agente_logico
                    )

                elif agente_en_ejecucion == "ASTAR":
                    mundo_real_astar, conocimiento_agente_astar = actualizar_agente(
                        agente_actual=agente_astar,
                        mundo_actual=mundo_astar,
                        mundo_real_ref=mundo_real_astar,
                        conocimiento_ref=conocimiento_agente_astar
                    )

                ultimo_movimiento = tiempo_actual

        rect_agente_aleatorio, rect_agente_logico, rect_agente_astar = obtener_layout()

        draw_interface(
            rect_agente_aleatorio,
            mundo_real,
            conocimiento_agente,
            "AGENTE ALEATORIO"
        )

        draw_interface(
            rect_agente_logico,
            mundo_real_logico,
            conocimiento_agente_logico,
            "AGENTE LÓGICO"
        )

        draw_interface(
            rect_agente_astar,
            mundo_real_astar,
            conocimiento_agente_astar,
            "AGENTE A*"
        )

        dibujar_botones()
        mostrar_estado_interfaz()
        mostrar_puntuaciones_generales()

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