import numpy as np

# ---------------------------------------------------------------------------
# FÍSICA
# ---------------------------------------------------------------------------

def calcular_resultados(v0, theta_graus, y0, g):
    """Calcula tempo de voo, altura máxima e alcance a partir das fórmulas
    analíticas (sem resistência do ar)."""
    theta = np.radians(theta_graus)

    # Tempo de voo (raiz positiva da equação quadrática de y(t) = 0)
    discriminante = (v0 * np.sin(theta)) ** 2 + 2 * g * y0
    t_voo = (v0 * np.sin(theta) + np.sqrt(discriminante)) / g

    # Altura máxima
    y_max = y0 + (v0 * np.sin(theta)) ** 2 / (2 * g)

    # Alcance horizontal (assumindo x0 = 0 por simplicidade)
    alcance = v0 * np.cos(theta) * t_voo

    return t_voo, y_max, alcance


def calcular_trajetoria(v0, theta_graus, y0, g, n_pontos=300):
    """Gera os pontos (x, y) da trajetória entre t=0 e t=t_voo."""
    theta = np.radians(theta_graus)
    t_voo, _, _ = calcular_resultados(v0, theta_graus, y0, g)

    t = np.linspace(0, t_voo, n_pontos)
    x = v0 * np.cos(theta) * t
    y = y0 + v0 * np.sin(theta) * t - 0.5 * g * t ** 2

    return x, y, t


def entrada_valida(v0, theta_graus, y0, g):
    """Valida os parâmetros de entrada. Retorna (bool, mensagem)."""
    if v0 <= 0:
        return False, "Velocidade inicial deve ser maior que zero."
    if not (0 < theta_graus < 90):
        return False, "Ângulo deve estar entre 0° e 90° (exclusivo)."
    if y0 < 0:
        return False, "Altura inicial não pode ser negativa."
    if g <= 0:
        return False, "Gravidade deve ser maior que zero."
    return True, ""