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
- Botão "Lançar" que anima o deslocamento do projétil sobre a trajetória, na
  velocidade real do voo (a duração da animação é igual ao tempo de voo
  calculado, não um valor fixo)
- Sliders e botões travados durante uma animação, evitando lançamentos
  sobrepostos por engano
- Botão "Sobrepor", exibido depois do primeiro lançamento, para ativar o modo
  de comparação: a primeira trajetória é preservada e cada novo lançamento é
  desenhado por cima dos anteriores, com cor própria. A escala permanece
  estável e só aumenta quando necessário para enquadrar uma nova curva
- Tabela comparativa (ao lado do gráfico) com v0, θ, y0, g, alcance, altura
  máxima e tempo de voo de cada lançamento sobreposto
- Botão "Limpar" (visível durante o modo sobreposição) que remove todos os
  lançamentos sobrepostos, esvazia a tabela e volta o gráfico ao modo normal
- Tratamento de entradas inválidas (ângulo fora de 0–90°, velocidade ≤ 0, etc.)

## Estrutura do código

- `calcular_trajetoria()` — calcula os pontos (x, y) da curva a partir das
  fórmulas analíticas
- `calcular_resultados()` — calcula R, ymax e tvoo
- `entrada_valida()` — valida os parâmetros antes de calcular
- `atualizar_grafico()` — callback chamado quando um slider muda (atualiza a
  curva de prévia; não mexe nos eixos enquanto o modo sobreposição estiver ativo)
- `lancar()` — callback do botão "Lançar", roda a animação na velocidade real
  do voo e, no modo sobreposição, cria uma curva/ponto persistentes
- `alternar_sobreposicao()` — callback do botão "Sobrepor"
- `limpar()` — callback do botão "Limpar"
- `atualizar_tabela()` — redesenha a tabela comparativa
- `ajustar_eixos_lancamentos()` — reenquadra o gráfico para caber todos os
  lançamentos sobrepostos

## Autores

- Paulo Eduardo Silva
- Pedro Zeferino Bittencourt 
- Laura Coelho de Oliveira 

## Licença

Uso acadêmico.
