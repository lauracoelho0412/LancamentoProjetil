
import time

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation

from fisica import calcular_resultados, calcular_trajetoria, entrada_valida


# ---------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------

CORES_LANCAMENTOS = ["crimson", "darkorange", "seagreen", "purple", "teal", "goldenrod"]
COLUNAS_TABELA = ["#", "v0 (m/s)", "θ (°)", "y0 (m)", "g (m/s²)", "R (m)", "ymax (m)", "tvoo (s)"]
COR_DESABILITADO = "lightgray"


# ---------------------------------------------------------------------------
# FUNÇÕES DA INTERFACE GRÁFICA
# ---------------------------------------------------------------------------

def criar_figura(v0_init, theta_init, y0_init, g_init):
    """Cria a figura, eixos, sliders e botões. Retorna um dicionário com
    todas as referências necessárias para as demais funções da interface."""

    fig = plt.figure(figsize=(12, 7))

    # Gráfico principal (à esquerda) + painel de tabela comparativa (à direita)
    ax = fig.add_axes([0.08, 0.42, 0.56, 0.52])
    ax_tabela = fig.add_axes([0.68, 0.42, 0.29, 0.52])
    ax_tabela.axis("off")

    # Linha da trajetória (curva "prévia", atualizada a cada mudança de slider)
    linha_trajetoria, = ax.plot([], [], lw=2, color="steelblue", label="Trajetória")

    # Ponto animado (projétil), usado pelo botão "Lançar" fora do modo sobreposição
    ponto_projetil, = ax.plot([], [], "o", color="steelblue", markersize=8)

    ax.set_xlabel("Distância horizontal x (m)")
    ax.set_ylabel("Altura y (m)")
    ax.set_title("Lançamento de Projétil - Trajetória")
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal", adjustable="datalim")  # evita trajetória distorcida

    # Caixa de texto com os resultados numéricos (R, y_max, t_voo) do estado atual
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

    return {
        "fig": fig,
        "ax": ax,
        "ax_tabela": ax_tabela,
        "linha_trajetoria": linha_trajetoria,
        "ponto_projetil": ponto_projetil,
        "texto_resultados": texto_resultados,
        "texto_erro": texto_erro,
        "slider_v0": slider_v0,
        "slider_theta": slider_theta,
        "slider_y0": slider_y0,
        "slider_g": slider_g,
        "todos_sliders": todos_sliders,
        "cores_originais": cores_originais,
        "eixo_botao_sobrepor": eixo_botao_sobrepor,
        "eixo_botao_limpar": eixo_botao_limpar,
        "botao_lancar": botao_lancar,
        "botao_sobrepor": botao_sobrepor,
        "botao_limpar": botao_limpar,
        "todos_botoes": todos_botoes,
        # Estado mutável compartilhado entre as callbacks
        "animacao_ativa": None,
        "animando": False,
        "modo_sobreposicao": False,
        "lancamentos": [],
        "ultimo_lancamento_normal": None,
    }


def atualizar_tabela(ctx):
    """Redesenha a tabela comparativa com os lançamentos já sobrepostos."""
    ax_tabela = ctx["ax_tabela"]
    lancamentos = ctx["lancamentos"]

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


def ajustar_eixos_lancamentos(ctx):
    """Mantém uma escala comum para todos os lançamentos da comparação."""
    ax = ctx["ax"]
    lancamentos = ctx["lancamentos"]

    xs = np.concatenate([e["linha"].get_xdata() for e in lancamentos])
    ys = np.concatenate([e["linha"].get_ydata() for e in lancamentos])
    ax.set_xlim(0, max(xs.max() * 1.1, 1))
    ax.set_ylim(0, max(ys.max() * 1.2, 1))


def adicionar_lancamento(ctx, x, y, params, resultados):
    """Adiciona uma trajetória persistente à comparação e retorna seu ponto."""
    ax = ctx["ax"]
    lancamentos = ctx["lancamentos"]

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
    ajustar_eixos_lancamentos(ctx)
    atualizar_tabela(ctx)
    return novo_ponto


def atualizar_grafico(ctx, event=None):
    """Chamada sempre que um slider é alterado. Recalcula e redesenha a
    curva de prévia + resultados numéricos."""
    fig = ctx["fig"]
    ax = ctx["ax"]
    linha_trajetoria = ctx["linha_trajetoria"]
    ponto_projetil = ctx["ponto_projetil"]
    texto_resultados = ctx["texto_resultados"]
    texto_erro = ctx["texto_erro"]

    v0 = ctx["slider_v0"].val
    theta_graus = ctx["slider_theta"].val
    y0 = ctx["slider_y0"].val
    g = ctx["slider_g"].val

    valido, mensagem = entrada_valida(v0, theta_graus, y0, g)
    if not valido:
        texto_erro.set_text(mensagem)
        return
    texto_erro.set_text("")

    x, y, _ = calcular_trajetoria(v0, theta_graus, y0, g)
    t_voo, y_max, alcance = calcular_resultados(v0, theta_graus, y0, g)

    linha_trajetoria.set_data(x, y)
    ponto_projetil.set_data([], [])  # limpa o ponto animado ao mudar parâmetros

    if not ctx["modo_sobreposicao"]:
        ax.set_xlim(0, max(x.max() * 1.1, 1))
        ax.set_ylim(0, max(y.max() * 1.2, 1))

    prefixo = "Próximo lançamento (prévia)\n" if ctx["modo_sobreposicao"] else ""
    texto_resultados.set_text(
        f"{prefixo}"
        f"Alcance R = {alcance:.2f} m\n"
        f"Altura máxima ymax = {y_max:.2f} m\n"
        f"Tempo de voo = {t_voo:.2f} s"
    )

    fig.canvas.draw_idle()


def travar_controles(ctx, travar):
    """Habilita/desabilita sliders e botões enquanto uma animação estiver em
    andamento, evitando cliques/alterações empilhadas."""
    fig = ctx["fig"]
    botao_lancar = ctx["botao_lancar"]

    ativo = not travar
    for slider, cor_original in zip(ctx["todos_sliders"], ctx["cores_originais"]):
        slider.set_active(ativo)
        slider.poly.set_facecolor(COR_DESABILITADO if travar else cor_original)

    for botao in ctx["todos_botoes"]:
        botao.set_active(ativo)

    # Feedback visual simples de que os controles estão bloqueados
    botao_lancar.label.set_text("Lançando..." if travar else "Lançar")
    fig.canvas.draw_idle()


def lancar(ctx, event=None):
    """Chamada pelo botão 'Lançar'. Anima o ponto percorrendo a trajetória já
    calculada, na velocidade real (duração da animação = tempo de voo)."""
    fig = ctx["fig"]
    texto_erro = ctx["texto_erro"]
    ponto_projetil = ctx["ponto_projetil"]

    if ctx["animando"]:
        return  # já existe uma animação em andamento, ignora o clique

    v0 = ctx["slider_v0"].val
    theta_graus = ctx["slider_theta"].val
    y0 = ctx["slider_y0"].val
    g = ctx["slider_g"].val

    valido, mensagem = entrada_valida(v0, theta_graus, y0, g)
    if not valido:
        texto_erro.set_text(mensagem)
        return

    x, y, tempos = calcular_trajetoria(v0, theta_graus, y0, g)
    t_voo, y_max, alcance = calcular_resultados(v0, theta_graus, y0, g)

    ctx["animando"] = True
    travar_controles(ctx, True)

    if ctx["modo_sobreposicao"]:
        ponto_ativo = adicionar_lancamento(
            ctx, x, y, (v0, theta_graus, y0, g), (t_voo, y_max, alcance)
        )
    else:
        ponto_ativo = ponto_projetil
        ctx["ultimo_lancamento_normal"] = {
            "x": x.copy(),
            "y": y.copy(),
            "params": (v0, theta_graus, y0, g),
            "resultados": (t_voo, y_max, alcance),
        }

    # A posição é determinada pelo tempo realmente transcorrido, e não pela
    # quantidade de quadros renderizados. Assim, atrasos da interface pulam
    # quadros em vez de deixar o projétil artificialmente mais lento.
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
            ctx["animando"] = False
            if not ctx["modo_sobreposicao"]:
                ctx["eixo_botao_sobrepor"].set_visible(True)
            travar_controles(ctx, False)
        return ponto_ativo,

    ctx["animacao_ativa"] = FuncAnimation(
        fig, frame_update, frames=total_frames, interval=1000 / fps_alvo,
        blit=True, repeat=False
    )
    fig.canvas.draw_idle()


def alternar_sobreposicao(ctx, event=None):
    """Chamada pelo botão 'Sobrepor'. Ativa o modo de comparação, no qual
    o lançamento anterior e cada novo lançamento ficam desenhados juntos,
    usando uma escala comum. A saída do modo é feita pelo botão 'Limpar'."""
    fig = ctx["fig"]
    linha_trajetoria = ctx["linha_trajetoria"]
    botao_sobrepor = ctx["botao_sobrepor"]

    if ctx["animando"]:
        return
    if ctx["ultimo_lancamento_normal"] is None:
        return
    if ctx["modo_sobreposicao"] and ctx["lancamentos"]:
        return  # já há comparação em andamento; use "Limpar" para sair

    ctx["modo_sobreposicao"] = not ctx["modo_sobreposicao"]

    if ctx["modo_sobreposicao"]:
        # O lançamento feito antes do clique é a primeira referência da comparação.
        primeiro = ctx["ultimo_lancamento_normal"]
        primeiro_ponto = adicionar_lancamento(
            ctx, primeiro["x"], primeiro["y"], primeiro["params"], primeiro["resultados"]
        )
        primeiro_ponto.set_data([primeiro["x"][-1]], [primeiro["y"][-1]])
        botao_sobrepor.label.set_text("Sobrepor: ON")
        linha_trajetoria.set_color("gray")
        linha_trajetoria.set_linestyle("--")
        ctx["eixo_botao_limpar"].set_visible(True)
    else:
        botao_sobrepor.label.set_text("Sobrepor")
        linha_trajetoria.set_color("steelblue")
        linha_trajetoria.set_linestyle("-")
        ctx["eixo_botao_limpar"].set_visible(False)

    atualizar_grafico(ctx)
    fig.canvas.draw_idle()


def limpar(ctx, event=None):
    """Chamada pelo botão 'Limpar'. Remove todos os lançamentos sobrepostos,
    esvazia a tabela e sai do modo de comparação, voltando o gráfico ao
    comportamento dinâmico (eixos que se ajustam à prévia)."""
    fig = ctx["fig"]
    linha_trajetoria = ctx["linha_trajetoria"]
    botao_sobrepor = ctx["botao_sobrepor"]

    if ctx["animando"]:
        return

    for entrada in ctx["lancamentos"]:
        entrada["linha"].remove()
        entrada["ponto"].remove()
    ctx["lancamentos"].clear()
    ctx["ultimo_lancamento_normal"] = None

    ctx["modo_sobreposicao"] = False
    botao_sobrepor.label.set_text("Sobrepor")
    linha_trajetoria.set_color("steelblue")
    linha_trajetoria.set_linestyle("-")
    ctx["eixo_botao_limpar"].set_visible(False)
    ctx["eixo_botao_sobrepor"].set_visible(False)

    atualizar_tabela(ctx)
    atualizar_grafico(ctx)
    fig.canvas.draw_idle()


def conectar_eventos(ctx):
    """Conecta sliders e botões às funções de callback da interface."""
    ctx["slider_v0"].on_changed(lambda val: atualizar_grafico(ctx))
    ctx["slider_theta"].on_changed(lambda val: atualizar_grafico(ctx))
    ctx["slider_y0"].on_changed(lambda val: atualizar_grafico(ctx))
    ctx["slider_g"].on_changed(lambda val: atualizar_grafico(ctx))

    ctx["botao_lancar"].on_clicked(lambda event: lancar(ctx))
    ctx["botao_sobrepor"].on_clicked(lambda event: alternar_sobreposicao(ctx))
    ctx["botao_limpar"].on_clicked(lambda event: limpar(ctx))


def iniciar_interface(v0_init=40.0, theta_init=45.0, y0_init=0.0, g_init=9.8):
    """Ponto de entrada da interface gráfica: cria a figura, conecta os eventos
    e exibe a janela."""
    ctx = criar_figura(v0_init, theta_init, y0_init, g_init)
    conectar_eventos(ctx)
    atualizar_tabela(ctx)
    atualizar_grafico(ctx)
    plt.show()