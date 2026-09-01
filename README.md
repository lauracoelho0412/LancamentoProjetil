# Lançamento de Projéteis — Interface Gráfica Interativa

Atividade de Física (Práticas Extensivas) — simulação interativa de lançamento
de projétil sem resistência do ar, com gráfico de trajetória atualizando em
tempo real.

## Requisitos

- Python 3.10+ (testado em 3.13.5)
- Bibliotecas: `matplotlib`, `numpy`

## Instalação

Caso o `pip` não esteja disponível na sua instalação do Python:

```bash
python -m ensurepip --upgrade
```

Depois, instale as dependências:

```bash
python -m pip install matplotlib numpy
```

## Como executar

```bash
python lancamento_projetil.py
```

Uma janela com o gráfico, sliders e botão "Lançar" deve abrir automaticamente.

## Funcionalidades

- Sliders para ajustar velocidade inicial (v0), ângulo de lançamento (θ),
  altura inicial (y0) e gravidade (g)
- Gráfico da trajetória atualizado em tempo real conforme os parâmetros mudam
- Exibição de alcance (R), altura máxima (ymax) e tempo de voo (tvoo)
- Botão "Lançar" que anima o deslocamento do projétil sobre a trajetória
- Tratamento de entradas inválidas (ângulo fora de 0–90°, velocidade ≤ 0, etc.)

## Estrutura do código

- `calcular_trajetoria()` — calcula os pontos (x, y) da curva a partir das
  fórmulas analíticas
- `calcular_resultados()` — calcula R, ymax e tvoo
- `entrada_valida()` — valida os parâmetros antes de calcular
- `atualizar_grafico()` — callback chamado quando um slider muda
- `lancar()` — callback do botão "Lançar", roda a animação

## Autores

- (preencher com os nomes do grupo)

## Licença

Uso acadêmico.
