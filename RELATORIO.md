# Relatório — Simulação de Lançamento de Projétil

**Disciplina:** Física (Práticas Extensivas) — SENAC, 4º Semestre  
**Autores:** Paulo Eduardo Silva, Pedro Zeferino Bittencourt e Laura Coelho de Oliveira

O trabalho teve como objetivo estudar o lançamento oblíquo por meio de um
simulador desenvolvido em Python com as bibliotecas NumPy e Matplotlib. O
modelo desconsidera a resistência do ar e separa o movimento em dois eixos:
no horizontal, a velocidade é constante; no vertical, atua a aceleração da
gravidade. As posições são calculadas por `x(t) = v0·cos(θ)·t` e
`y(t) = y0 + v0·sen(θ)·t − g·t²/2`.

A interface permite alterar a velocidade inicial, o ângulo, a altura inicial
e a gravidade. Ela apresenta a trajetória, o alcance, a altura máxima e o
tempo de voo. Durante a animação, os controles permanecem bloqueados. Depois
do primeiro lançamento, o modo **Sobrepor** permite comparar novas
trajetórias na mesma escala e registra os valores em uma tabela; o botão
**Limpar** reinicia a experiência. A posição animada acompanha o tempo físico
calculado, independentemente da quantidade de quadros renderizados.

Como teste, foram comparados lançamentos com `v0 = 40 m/s`, `y0 = 0 m` e
`g = 9,8 m/s²`. Para 30°, o alcance foi 141,39 m, a altura máxima 20,41 m e o
tempo de voo 4,08 s. Para 45°, obtiveram-se 163,27 m, 40,82 m e 5,77 s. Para
60°, os resultados foram 141,39 m, 61,22 m e 7,07 s.

Conclui-se que ângulos complementares apresentam o mesmo alcance quando a
altura inicial é zero, enquanto ângulos maiores aumentam a altura e o tempo
de voo. Entre os casos analisados, 45° produziu o maior alcance, de acordo
com a teoria do lançamento oblíquo.
