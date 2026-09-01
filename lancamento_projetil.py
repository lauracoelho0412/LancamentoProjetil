import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation

# ---------------------------------------------------------------------------
# FÍSICA (separada da interface, conforme pedido no enunciado)
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

    # Alcance horizontal (assumindo x0 = 0 por simplicidade; ajuste se quiser x0 != 0)
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


# ---------------------------------------------------------------------------
# INTERFACE GRÁFICA
# ---------------------------------------------------------------------------

# Estado inicial
v0_init, theta_init, y0_init, g_init = 40.0, 45.0, 0.0, 9.8

fig, ax = plt.subplots(figsize=(9, 6))
plt.subplots_adjust(left=0.1, bottom=0.42)  # espaço embaixo para os sliders

# Linha da trajetória (curva estática, atualizada a cada mudança de slider)
linha_trajetoria, = ax.plot([], [], lw=2, color="steelblue", label="Trajetória")

# Ponto animado (projétil), usado pelo botão "Lançar"
ponto_projetil, = ax.plot([], [], "o", color="crimson", markersize=8)

ax.set_xlabel("Distância horizontal x (m)")
ax.set_ylabel("Altura y (m)")
ax.set_title("Lançamento de Projétil - Trajetória")
ax.grid(True, alpha=0.3)
ax.set_aspect("equal", adjustable="datalim")  # evita trajetória distorcida

# Caixa de texto com os resultados numéricos (R, y_max, t_voo)
texto_resultados = ax.text(
    0.02, 0.98, "", transform=ax.transAxes, va="top", ha="left",
    fontsize=10, bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
)

# Caixa de aviso para entradas inválidas
texto_erro = fig.text(0.5, 0.02, "", ha="center", color="red", fontsize=10)


# --- Sliders ---
eixo_v0 = plt.axes([0.15, 0.30, 0.65, 0.03])
eixo_theta = plt.axes([0.15, 0.25, 0.65, 0.03])
eixo_y0 = plt.axes([0.15, 0.20, 0.65, 0.03])
eixo_g = plt.axes([0.15, 0.15, 0.65, 0.03])

slider_v0 = Slider(eixo_v0, "v0 (m/s)", 5, 150, valinit=v0_init)
slider_theta = Slider(eixo_theta, "θ (graus)", 1, 89, valinit=theta_init)
slider_y0 = Slider(eixo_y0, "y0 (m)", 0, 50, valinit=y0_init)
slider_g = Slider(eixo_g, "g (m/s²)", 1.6, 24.8, valinit=g_init)

# --- Botão "Lançar" ---
eixo_botao = plt.axes([0.4, 0.05, 0.2, 0.05])
botao_lancar = Button(eixo_botao, "Lançar")

# Variável para guardar a animação ativa (evita que o garbage collector a mate)
animacao_ativa = None


def atualizar_grafico(event=None):
    """Chamada sempre que um slider é alterado. Recalcula e redesenha
    a trajetória + resultados numéricos."""
    v0 = slider_v0.val
    theta_graus = slider_theta.val
    y0 = slider_y0.val
    g = slider_g.val

    valido, mensagem = entrada_valida(v0, theta_graus, y0, g)
    if not valido:
        texto_erro.set_text(mensagem)
        return
    texto_erro.set_text("")

    x, y, _ = calcular_trajetoria(v0, theta_graus, y0, g)
    t_voo, y_max, alcance = calcular_resultados(v0, theta_graus, y0, g)

    linha_trajetoria.set_data(x, y)
    ponto_projetil.set_data([], [])  # limpa o ponto animado ao mudar parâmetros

    ax.set_xlim(0, max(x.max() * 1.1, 1))
    ax.set_ylim(0, max(y.max() * 1.2, 1))

    texto_resultados.set_text(
        f"Alcance R = {alcance:.2f} m\n"
        f"Altura máxima ymax = {y_max:.2f} m\n"
        f"Tempo de voo tvoo = {t_voo:.2f} s"
    )

    fig.canvas.draw_idle()


def lancar(event):
    """Chamada pelo botão 'Lançar'. Anima o ponto percorrendo a trajetória
    já calculada."""
    global animacao_ativa

    v0 = slider_v0.val
    theta_graus = slider_theta.val
    y0 = slider_y0.val
    g = slider_g.val

    valido, mensagem = entrada_valida(v0, theta_graus, y0, g)
    if not valido:
        texto_erro.set_text(mensagem)
        return

    x, y, _ = calcular_trajetoria(v0, theta_graus, y0, g)

    def frame_update(i):
        ponto_projetil.set_data([x[i]], [y[i]])
        return ponto_projetil,

    # interval controla a velocidade da animação (ms entre frames)
    animacao_ativa = FuncAnimation(
        fig, frame_update, frames=len(x), interval=15, blit=True, repeat=False
    )
    fig.canvas.draw_idle()


# Conecta os sliders e o botão às funções de callback
slider_v0.on_changed(atualizar_grafico)
slider_theta.on_changed(atualizar_grafico)
slider_y0.on_changed(atualizar_grafico)
slider_g.on_changed(atualizar_grafico)
botao_lancar.on_clicked(lancar)

# Desenha o estado inicial
atualizar_grafico()

plt.show()
