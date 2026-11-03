# ANA v0.8 — Gradientes temporais multivariáveis (experimento)

## Objetivo

Ampliar a validação de ANA v0.7 de um parâmetro recorrente para dois parâmetros
da mesma unidade escalar: o peso recorrente (w=w_{xx}[0][0]) e o peso de entrada
(a=w_{xu}[0][0]). A etapa ainda é validação matemática, não treinamento geral.

## Dinâmica de referência

\[
x_t=\tanh(wx_{t-1}+au_t),\qquad y_t=\tanh(vx_t)
\]

As sensibilidades dos estados em relação aos dois parâmetros são propagadas
simultaneamente:

\[
s_t^{(w)}=(1-x_t^2)(x_{t-1}+w s_{t-1}^{(w)})
\]

\[
s_t^{(a)}=(1-x_t^2)(u_t+w s_{t-1}^{(a)})
\]

Com (q_t^{(p)}=(1-y_t^2)v s_t^{(p)}), para (p\in\{w,a\}), os gradientes
da perda MSE são:

\[
\frac{\partial J}{\partial p}
=\frac{2}{T}\sum_{t=1}^{T}(y_t-r_t)q_t^{(p)}
\]

Cada gradiente analítico é comparado com uma diferença central calculada ao
perturbar somente o parâmetro correspondente, mantendo o outro fixo.

## Protocolo

- Dois parâmetros treináveis no modelo matemático: (w_{xx}[0][0]) e (w_{xu}[0][0]).
- Quatro cenários determinísticos de pesos.
- Três epsilons por parâmetro e cenário.
- Comparação de erro absoluto e relativo.
- Contagem de avaliações completas da sequência.

## Limites

A validação cobre somente uma unidade escalar com caminhos de memória, contexto
e modulação sem contribuição. Não implementa ainda atualização simultânea dos
parâmetros, não é uma validação de rede multiunidade e não garante convergência,
generalização ou inteligência. A contagem de avaliações é determinística e não
substitui benchmark de tempo de parede.
