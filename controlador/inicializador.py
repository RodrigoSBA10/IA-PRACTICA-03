import copy
from entorno.mundo import WumpusWorld
from agentes.AgenteAleatorio import AgenteAleatorio
from agentes.agente import AgenteLogico
from agentes.agente_astar import AgenteAStar

# Función para crear mundos y agentes según el modo seleccionado
def crear_mundos_y_agentes(modo_mundos):
    # Si el modo es "MISMO_MUNDO", se crea un solo mundo y se hacen copias para cada agente
    if modo_mundos == "MISMO_MUNDO":
        mundo_base = WumpusWorld()

        mundo_aleatorio = copy.deepcopy(mundo_base)
        mundo_logico = copy.deepcopy(mundo_base)
        mundo_astar = copy.deepcopy(mundo_base)
    # Si el modo es "MUNDOS_DIFERENTES", se crean mundos independientes para cada agente
    else:
        mundo_aleatorio = WumpusWorld()
        mundo_logico = WumpusWorld()
        mundo_astar = WumpusWorld()

    agente_aleatorio = AgenteAleatorio(mundo_aleatorio)
    agente_logico = AgenteLogico(mundo_logico)
    agente_astar = AgenteAStar(mundo_astar)

    # Se devuelve un diccionario con los agentes y sus respectivos mundos
    return {
        "ALEATORIO": {
            "agente": agente_aleatorio,
            "mundo": mundo_aleatorio
        },
        "LOGICO": {
            "agente": agente_logico,
            "mundo": mundo_logico
        },
        "ASTAR": {
            "agente": agente_astar,
            "mundo": mundo_astar
        }
    }

# Función para inicializar las matrices de cada agente con el mundo real y su conocimiento actual
def inicializar_matrices(datos_agentes):
    matrices = {}
    # Se recorre cada agente y se obtiene su posición actual para mostrar el mundo real y su conocimiento
    for nombre, datos in datos_agentes.items():
        agente = datos["agente"]
        mundo = datos["mundo"]

        r, c = agente.pos_actual

        matrices[nombre] = {
            "mundo_real": mundo.obtener_matriz_visual(pos_agente=(r, c)),
            "conocimiento": agente.mostrar_mundo_matriz()
        }
    # Se devuelve un diccionario con las matrices del mundo real y el conocimiento de cada agente
    return matrices