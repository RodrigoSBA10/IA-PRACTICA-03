from controlador.estado_juego import EstadoJuego
from controlador.inicializador import crear_mundos_y_agentes, inicializar_matrices
from controlador.simulador import actualizar_agente

from interfaz.config_tablero import *
from configuracion.config import *

import pygame

# Metodo principal para ejecutar la interfaz del juego
def ejecutar_interfaz():
    # Inicialización de Pygame y configuración de la ventana
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
    # Modo de juego inicial y el agenete inicial
    modo_mundos = "MISMO_MUNDO"
    agente_en_ejecucion = "ALEATORIO"
    # Trae el estado del juego
    estado = EstadoJuego()
    # Crear los mundos y agentes según el modo seleccionado, y luego inicializar las matrices de estado para cada agente
    datos_agentes = crear_mundos_y_agentes(modo_mundos)
    matrices = inicializar_matrices(datos_agentes)
    # Variable para controlar el tiempo entre movimientos de los agentes
    ultimo_movimiento = pygame.time.get_ticks()

    scroll_y = 0

    # Función para calcular las posiciones y tamaños de los paneles de cada agente según el tamaño actual de la ventana
    def obtener_layout():
        # Obtiene el ancho de la pantalla
        ancho = screen.get_width()
        # Define márgenes y espacios para organizar los paneles de los agentes
        margen = 20
        barra_superior = 150
        espacio = 25

        ancho_panel = ancho - margen * 2
        alto_panel = 285

        rect_aleatorio = pygame.Rect(
            margen,
            barra_superior + scroll_y,
            ancho_panel,
            alto_panel + 15
        )

        rect_logico = pygame.Rect(
            margen,
            barra_superior + alto_panel + espacio + scroll_y,
            ancho_panel,
            alto_panel + 15
        )

        rect_astar = pygame.Rect(
            margen,
            barra_superior + (alto_panel + espacio) * 2 + scroll_y,
            ancho_panel,
            alto_panel + 15
        )

        return rect_aleatorio, rect_logico, rect_astar
    # Función para obtener los rectángulos de los botones en la parte superior de la interfaz
    def obtener_botones():
        return {
            "mismo": pygame.Rect(20, 15, 180, 38),
            "independiente": pygame.Rect(215, 15, 250, 38),
            "aleatorio": pygame.Rect(500, 15, 150, 38),
            "logico": pygame.Rect(665, 15, 130, 38),
            "astar": pygame.Rect(810, 15, 110, 38),
            "reiniciar": pygame.Rect(940, 15, 140, 38),
        }
    # Función para dibujar un botón con su estado (activo o inactivo) y el texto correspondiente
    def dibujar_boton(rect, texto, activo=False):
        if activo:
            color_boton = COLOR_AZUL
            color_texto = COLOR_TEXT
        else:
            color_boton = COLOR_PANEL_HEADER
            color_texto = COLOR_SUBTEXT

        pygame.draw.rect(screen, color_boton, rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_FRAME, rect, 2, border_radius=12)

        texto_render = font_boton.render(texto, True, color_texto)
        texto_rect = texto_render.get_rect(center=rect.center)
        screen.blit(texto_render, texto_rect)
    # Función para dibujar todos los botones en la parte superior, resaltando el modo de mundo y el agente activo
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
    # Función para mostrar el estado actual del juego en un panel, incluyendo el modo de mundo, el agente activo y
    # las puntuaciones de cada agente
    def mostrar_estado_interfaz():
        pygame.draw.rect(
            screen,
            COLOR_PANEL,
            pygame.Rect(20, 58, screen.get_width() - 40, 65),
            border_radius=14
        )

        texto = font_estado.render(
            f"Modo: {modo_mundos}   |   Agente activo: {agente_en_ejecucion}",
            True,
            COLOR_TEXT
        )

        screen.blit(texto, (40, 68))

        puntuaciones = (
            f"Aleatorio: {datos_agentes['ALEATORIO']['agente'].puntuacion}    "
            f"Lógico: {datos_agentes['LOGICO']['agente'].puntuacion}    "
            f"A*: {datos_agentes['ASTAR']['agente'].puntuacion}"
        )

        texto_score = font_score.render(puntuaciones, True, COLOR_SUBTEXT)
        screen.blit(texto_score, (40, 96))
    # Función para mostrar las puntuaciones generales de cada agente en la parte inferior de la interfaz
    def mostrar_puntuaciones_generales():
        textos = [
            f"Aleatorio: {datos_agentes['ALEATORIO']['agente'].puntuacion}",
            f"Lógico: {datos_agentes['LOGICO']['agente'].puntuacion}",
            f"A*: {datos_agentes['ASTAR']['agente'].puntuacion}"
        ]

        x = 20
        y = 95

        for texto_score in textos:
            texto = font_score.render(texto_score, True, COLOR_FRAME)
            screen.blit(texto, (x, y))
            x += 190
    # Función para dibujar las celdas de la cuadrícula del mundo real y el conocimiento del agente, usando colores y
    # símbolos para representar diferentes elementos
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
                    color = COLOR_PWUMPUS
                elif element == "*":
                    color = COLOR_GOLD
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
    # Función para dibujar la interfaz de cada agente, incluyendo el panel, el título, las secciones del mundo real y
    # el conocimiento del agente, y las cuadrículas correspondientes
    def draw_interface(rect_agente, mundo_real, conocimiento_agente, titulo_agente):
        pygame.draw.rect(screen, COLOR_PANEL, rect_agente, border_radius=16)
        pygame.draw.rect(screen, COLOR_FRAME, rect_agente, 2, border_radius=16)

        header = pygame.Rect(rect_agente.x, rect_agente.y, rect_agente.width, 46)
        pygame.draw.rect(screen, COLOR_PANEL_HEADER, header, border_radius=16)

        titulo = font_estado.render(titulo_agente, True, COLOR_TEXT)
        screen.blit(titulo, (rect_agente.x + 18, rect_agente.y + 10))

        center_x = rect_agente.x + rect_agente.width // 2
        section_width = rect_agente.width // 2

        title_real = font_title.render("MUNDO REAL", True, COLOR_SUBTEXT)
        title_agent = font_title.render("CONOCIMIENTO DEL AGENTE", True, COLOR_SUBTEXT)

        screen.blit(
            title_real,
            (rect_agente.x + (section_width - title_real.get_width()) // 2, rect_agente.y + 58)
        )

        screen.blit(
            title_agent,
            (center_x + (section_width - title_agent.get_width()) // 2, rect_agente.y + 58)
        )

        pygame.draw.line(
            screen,
            COLOR_FRAME,
            (center_x, rect_agente.y + 50),
            (center_x, rect_agente.y + rect_agente.height - 15),
            2
        )

        grid_w_h = TAMANIO_MUNDO * CELL_SIZE
        grid_y = rect_agente.y + 88

        left_grid_x = rect_agente.x + (section_width - grid_w_h) // 2
        right_grid_x = center_x + (section_width - grid_w_h) // 2

        for start_x in [left_grid_x, right_grid_x]:
            fondo_grid = pygame.Rect(start_x, grid_y, grid_w_h, grid_w_h)
            pygame.draw.rect(screen, (20, 27, 42), fondo_grid, border_radius=8)

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
    # Función para mostrar un mensaje centralizado en la pantalla con un color específico, utilizada para mostrar
    # estados como victoria, derrota o sin caminos
    def menssage(cadena, color):
        texto = fuente_game_over.render(cadena, True, color)
        rect = texto.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2)
        )
        screen.blit(texto, rect)
    # Función para mostrar un popup con un título, subtítulo y color específico, utilizada para mostrar eventos como
    # la eliminación de una amenaza por parte del agente
    def mostrar_popup(titulo, subtitulo, color):
        ancho = 520
        alto = 160

        x = (screen.get_width() - ancho) // 2
        y = (screen.get_height() - alto) // 2

        rect = pygame.Rect(x, y, ancho, alto)

        pygame.draw.rect(screen, (25, 32, 48), rect, border_radius=18)
        pygame.draw.rect(screen, color, rect, 4, border_radius=18)

        texto_titulo = font_estado.render(titulo, True, color)
        texto_sub = font_score.render(subtitulo, True, COLOR_TEXT)

        screen.blit(
            texto_titulo,
            texto_titulo.get_rect(center=(rect.centerx, rect.y + 55))
        )

        screen.blit(
            texto_sub,
            texto_sub.get_rect(center=(rect.centerx, rect.y + 105))
        )
    # Función para mostrar un mensaje específico cuando el agente logra eliminar una amenaza, utilizando un popup con
    # un mensaje personalizado y un color azul, y luego espera un momento antes de continuar con la ejecución
    def mostrar_mensaje_wumpus(cadena):
        mostrar_popup(cadena, "El agente logró eliminar una amenaza",
                      COLOR_AZUL)
        pygame.display.flip()
        pygame.time.delay(1200)
    # Función para mostrar la puntuación actual del agente en ejecución, utilizando un texto grande
    # y centrado en la pantalla, con un color específico, y mostrando el valor de la puntuación obtenida por el agente
    def mostrar_puntuacion():
        puntuacion = datos_agentes[agente_en_ejecucion]["agente"].puntuacion

        fuente_puntuacion = pygame.font.SysFont("Arial", 40, bold=True)
        texto = fuente_puntuacion.render(
            f"Puntuación: {puntuacion}",
            True,
            COLOR_FRAME
        )

        rect = texto.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 + 80)
        )

        screen.blit(texto, rect)
    # Función para reiniciar completamente el juego, creando nuevos mundos y agentes según el modo seleccionado, y
    # reiniciando el estado del juego y el tiempo del último movimiento
    def reiniciar_todo():
        nonlocal datos_agentes, matrices, estado, ultimo_movimiento

        estado = EstadoJuego()
        datos_agentes = crear_mundos_y_agentes(modo_mundos)
        matrices = inicializar_matrices(datos_agentes)
        ultimo_movimiento = pygame.time.get_ticks()
    # Función para reiniciar solo el estado del juego, manteniendo los mismos mundos y agentes, pero
    # reiniciando el estado del juego y el tiempo del último movimiento, utilizada cuando se cambia el agente en ejecución
    def reiniciar_estado():
        nonlocal estado, ultimo_movimiento

        estado = EstadoJuego()
        ultimo_movimiento = pygame.time.get_ticks()

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

            elif event.type == pygame.MOUSEWHEEL:
                scroll_y += event.y * 40
                scroll_y = min(0, scroll_y)

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
                    reiniciar_estado()

                elif botones["logico"].collidepoint(event.pos):
                    agente_en_ejecucion = "LOGICO"
                    reiniciar_estado()

                elif botones["astar"].collidepoint(event.pos):
                    agente_en_ejecucion = "ASTAR"
                    reiniciar_estado()

                elif botones["reiniciar"].collidepoint(event.pos):
                    reiniciar_todo()

        tiempo_actual = pygame.time.get_ticks()

        if not estado.juego_terminado:
            if tiempo_actual - ultimo_movimiento >= DELAY_MOVIMIENTO:
                datos = datos_agentes[agente_en_ejecucion]

                matrices[agente_en_ejecucion]["mundo_real"], matrices[agente_en_ejecucion]["conocimiento"] = actualizar_agente(
                    agente_actual=datos["agente"],
                    mundo_actual=datos["mundo"],
                    mundo_real_ref=matrices[agente_en_ejecucion]["mundo_real"],
                    conocimiento_ref=matrices[agente_en_ejecucion]["conocimiento"],
                    estado_juego=estado,
                    mostrar_mensaje=mostrar_mensaje_wumpus
                )

                ultimo_movimiento = tiempo_actual

        rect_aleatorio, rect_logico, rect_astar = obtener_layout()

        draw_interface(
            rect_aleatorio,
            matrices["ALEATORIO"]["mundo_real"],
            matrices["ALEATORIO"]["conocimiento"],
            "AGENTE ALEATORIO"
        )

        draw_interface(
            rect_logico,
            matrices["LOGICO"]["mundo_real"],
            matrices["LOGICO"]["conocimiento"],
            "AGENTE LÓGICO"
        )

        draw_interface(
            rect_astar,
            matrices["ASTAR"]["mundo_real"],
            matrices["ASTAR"]["conocimiento"],
            "AGENTE A*"
        )

        dibujar_botones()
        mostrar_estado_interfaz()

        if estado.victoria:
            menssage("¡WINNER!", color_verde)
            mostrar_puntuacion()

        elif estado.sin_caminos:
            menssage("¡SIN CAMINOS!", COLOR_SIN)
            mostrar_puntuacion()

        elif estado.agente_devorado:
            menssage("WUMPUS ELIMINO AL AGENTE", COLOR_MAR)
            mostrar_puntuacion()

        elif estado.juego_terminado:
            menssage("¡GAME OVER!", color_rojo)
            mostrar_puntuacion()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()