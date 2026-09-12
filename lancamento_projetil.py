import time

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation

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


# ---------------------------------------------------------------------------
# INTERFACE GRÁFICA
# ---------------------------------------------------------------------------

# Estado inicial
v0_init, theta_init, y0_init, g_init = 40.0, 45.0, 0.0, 9.8

# Cores usadas para os lançamentos sobrepostos (cicla se houver muitos)
CORES_LANCAMENTOS = ["crimson", "darkorange", "seagreen", "purple", "teal", "goldenrod"]
COLUNAS_TABELA = ["#", "v0 (m/s)", "θ (°)", "y0 (m)", "g (m/s²)", "R (m)", "ymax (m)", "tvoo (s)"]

fig = plt.figure(figsize=(12, 7))

# Gráfico principal (à esquerda) + painel de tabela comparativa (à direita)
ax = fig.add_axes([0.08, 0.42, 0.56, 0.52])
ax_tabela = fig.add_axes([0.68, 0.42, 0.29, 0.52])
ax_tabela.axis("off")

# Linha da trajetória (curva "prévia", atualizada a cada mudança de slider)
linha_trajetoria, = ax.plot([], [], lw=2, color="steelblue", label="Trajetória")

# Ponto animado (projétil), usado pelo botão "Lançar" fora do modo sobreposição
ponto_projetil, = ax.plot([], [], "o", color="crimson", markersize=8)

ax.set_xlabel("Distância horizontal x (m)")
ax.set_ylabel("Altura y (m)")
ax.set_title("Lançamento de Projétil - Trajetória")
ax.grid(True, alpha=0.3)
ax.set_aspect("equal", adjustable="datalim")  # evita trajetória distorcida

# Caixa de texto com os resultados numéricos (R, y_max, t_voo) do estado atual dos sliders
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


todos_sliders = [slider_v0, slider_theta, slider_y0, slider_g]
cores_originais = [s.poly.get_facecolor() for s in todos_sliders]
COR_DESABILITADO = "lightgray"

# --- Botões "Lançar" / "Sobrepor" / "Limpar" ---
eixo_botao_lancar = plt.axes([0.15, 0.05, 0.18, 0.05])
eixo_botao_sobrepor = plt.axes([0.36, 0.05, 0.18, 0.05])
eixo_botao_limpar = plt.axes([0.57, 0.05, 0.18, 0.05])

botao_lancar = Button(eixo_botao_lancar, "Lançar")
botao_sobrepor = Button(eixo_botao_sobrepor, "Sobrepor")
botao_limpar = Button(eixo_botao_limpar, "Limpar")

eixo_botao_sobrepor.set_visible(False)
eixo_botao_limpar.set_visible(False)

todos_botoes = [botao_lancar, botao_sobrepor, botao_limpar]

# Variável para guardar a animação ativa (evita que o garbage collector a mate)
animacao_ativa = None

# Flag de controle: True enquanto um lançamento está em andamento
animando = False

modo_sobreposicao = False
lancamentos = []
ultimo_lancamento_normal = None


def atualizar_tabela():
    #Redesenha a tabela comparativa com os lançamentos já sobrepostos.
    ax_tabela.clear()
    ax_tabela.axis("off")

    if not lancamentos:
        ax_tabela.text(
            0.5, 0.5, "Faça um lançamento e clique em\n\"Sobrepor\" para comparar",
            ha="center", va="center", fontsize=9, color="gray",
            transform=ax_tabela.transAxes
        )
        return

    linhas = []
    cores = []
    for i, entrada in enumerate(lancamentos, start=1):
        v0, theta_graus, y0, g = entrada["params"]
        t_voo, y_max, alcance = entrada["resultados"]
        linhas.append([
            str(i), f"{v0:.1f}", f"{theta_graus:.1f}", f"{y0:.1f}",
            f"{g:.2f}", f"{alcance:.2f}", f"{y_max:.2f}", f"{t_voo:.2f}",
        ])
        cores.append(entrada["cor"])

    tabela = ax_tabela.table(
        cellText=linhas, colLabels=COLUNAS_TABELA, loc="center", cellLoc="center"
    )
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(8)
    tabela.scale(1, 1.5)

    # Colore a coluna "#" com a mesma cor da curva correspondente no gráfico
    for i, cor in enumerate(cores, start=1):
        celula = tabela[i, 0]
        celula.set_facecolor(cor)
        celula.get_text().set_color("white")


def ajustar_eixos_lancamentos():
    """Mantém uma escala comum para todos os lançamentos da comparação.

    Como as curvas anteriores continuam na lista, os limites não encolhem;
    eles apenas aumentam quando uma nova trajetória exigir mais espaço.
    """
    xs = np.concatenate([e["linha"].get_xdata() for e in lancamentos])
    ys = np.concatenate([e["linha"].get_ydata() for e in lancamentos])
    ax.set_xlim(0, max(xs.max() * 1.1, 1))
    ax.set_ylim(0, max(ys.max() * 1.2, 1))


def adicionar_lancamento(x, y, params, resultados):
    #Adiciona uma trajetória persistente à comparação e retorna seu ponto.
    cor = CORES_LANCAMENTOS[len(lancamentos) % len(CORES_LANCAMENTOS)]
    nova_linha, = ax.plot(x, y, lw=2, color=cor, alpha=0.9)
    novo_ponto, = ax.plot([], [], "o", color=cor, markersize=8)
    lancamentos.append({
        "linha": nova_linha,
        "ponto": novo_ponto,
        "params": params,
        "resultados": resultados,
        "cor": cor,
    })
    ajustar_eixos_lancamentos()
    atualizar_tabela()
    return novo_ponto


def atualizar_grafico(event=None):
    """Chamada sempre que um slider é alterado. Recalcula e redesenha a
    curva de prévia + resultados numéricos. No modo sobreposição, os eixos
    permanecem fixos (não reagem à prévia) para permitir a comparação."""
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

    if not modo_sobreposicao:
        ax.set_xlim(0, max(x.max() * 1.1, 1))
        ax.set_ylim(0, max(y.max() * 1.2, 1))

    prefixo = "Próximo lançamento (prévia)\n" if modo_sobreposicao else ""
    texto_resultados.set_text(
        f"{prefixo}"
        f"Alcance R = {alcance:.2f} m\n"
        f"Altura máxima ymax = {y_max:.2f} m\n"
        f"Tempo de voo = {t_voo:.2f} s"
    )

    fig.canvas.draw_idle()


def travar_controles(travar):
    """Habilita/desabilita sliders e botões enquanto uma animação estiver em
    andamento, evitando cliques/alterações empilhadas."""
    ativo = not travar
    for slider, cor_original in zip(todos_sliders, cores_originais):
        slider.set_active(ativo)
        slider.poly.set_facecolor(COR_DESABILITADO if travar else cor_original)

    for botao in todos_botoes:
        botao.set_active(ativo)

    # Feedback visual simples de que os controles estão bloqueados
    botao_lancar.label.set_text("Lançando..." if travar else "Lançar")
    fig.canvas.draw_idle()


def lancar(event):
    """
    Chamada pelo botão 'Lançar'. Anima o ponto percorrendo a trajetória já calculada, na 
    velocidade real (duração da animação = tempo de voo).
    Ignora cliques enquanto uma animação já está rodando. No modo sobreposição, cria uma nova curva/ponto
    persistentes em vez de reusar os únicos existentes, e acrescenta uma linha na tabela comparativa.
    """
    global animacao_ativa, animando, ultimo_lancamento_normal

    if animando:
        return  # já existe uma animação em andamento, ignora o clique

    v0 = slider_v0.val
    theta_graus = slider_theta.val
    y0 = slider_y0.val
    g = slider_g.val

    valido, mensagem = entrada_valida(v0, theta_graus, y0, g)
    if not valido:
        texto_erro.set_text(mensagem)
        return

    x, y, tempos = calcular_trajetoria(v0, theta_graus, y0, g)
    t_voo, y_max, alcance = calcular_resultados(v0, theta_graus, y0, g)

    animando = True
    travar_controles(True)

    if modo_sobreposicao:
        ponto_ativo = adicionar_lancamento(
            x, y, (v0, theta_graus, y0, g), (t_voo, y_max, alcance)
        )
    else:
        ponto_ativo = ponto_projetil
        ultimo_lancamento_normal = {
            "x": x.copy(),
            "y": y.copy(),
            "params": (v0, theta_graus, y0, g),
            "resultados": (t_voo, y_max, alcance),
        }

    """ 
    A posição é determinada pelo tempo realmente transcorrido, e não pela
     quantidade de quadros renderizados. Assim, atrasos da interface pulam
     quadros em vez de deixar o projétil artificialmente mais lento.
    """
    fps_alvo = 60
    total_frames = max(2, int(np.ceil(t_voo * fps_alvo)) + 1)
    inicio_animacao = time.perf_counter()

    def frame_update(i):
        decorrido = time.perf_counter() - inicio_animacao
        if i == total_frames - 1:
            decorrido = t_voo
        indice = min(np.searchsorted(tempos, decorrido, side="right") - 1, len(x) - 1)
        indice = max(0, indice)
        ponto_ativo.set_data([x[indice]], [y[indice]])

        if decorrido >= t_voo:
            global animando
            animando = False
            if not modo_sobreposicao:
                eixo_botao_sobrepor.set_visible(True)
            travar_controles(False)
        return ponto_ativo,

    animacao_ativa = FuncAnimation(
        fig, frame_update, frames=total_frames, interval=1000 / fps_alvo,
        blit=True, repeat=False
    )
    fig.canvas.draw_idle()


def alternar_sobreposicao(event):
    """
    Chamada pelo botão 'Sobrepor'. Ativa o modo de comparação, no qual
    o lançamento anterior e cada novo lançamento ficam desenhados juntos,
    usando uma escala comum. A saída do modo é feita pelo botão 'Limpar'.
    """
    global modo_sobreposicao

    if animando:
        return
    if ultimo_lancamento_normal is None:
        return
    if modo_sobreposicao and lancamentos:
        return  # já há comparação em andamento; use "Limpar" para sair

    modo_sobreposicao = not modo_sobreposicao

    if modo_sobreposicao:
        # O lançamento feito antes do clique é a primeira referência da comparação. 
        # Ele precisa ser copiado antes que os sliders alterem a linha de prévia.
        primeiro = ultimo_lancamento_normal
        primeiro_ponto = adicionar_lancamento(
            primeiro["x"], primeiro["y"], primeiro["params"], primeiro["resultados"]
        )
        primeiro_ponto.set_data([primeiro["x"][-1]], [primeiro["y"][-1]])
        botao_sobrepor.label.set_text("Sobrepor: ON")
        linha_trajetoria.set_color("gray")
        linha_trajetoria.set_linestyle("--")
        eixo_botao_limpar.set_visible(True)
    else:
        botao_sobrepor.label.set_text("Sobrepor")
        linha_trajetoria.set_color("steelblue")
        linha_trajetoria.set_linestyle("-")
        eixo_botao_limpar.set_visible(False)

    atualizar_grafico()
    fig.canvas.draw_idle()


def limpar(event):
    """
    Chamada pelo botão 'Limpar'. Remove todos os lançamentos sobrepostos,
    esvazia a tabela e sai do modo de comparação, voltando o gráfico ao
    comportamento dinâmico (eixos que se ajustam à prévia).
    """
    global modo_sobreposicao, ultimo_lancamento_normal

    if animando:
        return

    for entrada in lancamentos:
        entrada["linha"].remove()
        entrada["ponto"].remove()
    lancamentos.clear()
    ultimo_lancamento_normal = None

    modo_sobreposicao = False
    botao_sobrepor.label.set_text("Sobrepor")
    linha_trajetoria.set_color("steelblue")
    linha_trajetoria.set_linestyle("-")
    eixo_botao_limpar.set_visible(False)
    eixo_botao_sobrepor.set_visible(False)

    atualizar_tabela()
    atualizar_grafico()
    fig.canvas.draw_idle()


# Conecta os sliders e os botões às funções de callback
slider_v0.on_changed(atualizar_grafico)
slider_theta.on_changed(atualizar_grafico)
slider_y0.on_changed(atualizar_grafico)
slider_g.on_changed(atualizar_grafico)
botao_lancar.on_clicked(lancar)
botao_sobrepor.on_clicked(alternar_sobreposicao)
botao_limpar.on_clicked(limpar)

# Desenha o estado inicial
atualizar_tabela()
atualizar_grafico()

plt.show()
