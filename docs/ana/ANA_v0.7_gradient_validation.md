# ANA v0.7 — Validação do gradiente temporal analítico

## Objetivo

Validar o estimador de diferenças finitas usado no crédito temporal de ANA v0.7
comparando-o com uma derivada analítica independente, antes de ampliar o número
de parâmetros treináveis.

## Regime matemático coberto

O teste é deliberadamente restrito à unidade escalar usada no benchmark, com
todos os caminhos de estado não envolvidos zerados:

\[
x_t = \tanh(w x_{t-1} + a u_t), \qquad
y_t = \tanh(v x_t)
\]

onde (w = w_{xx}[0][0]), (a = w_{xu}[0][0]) e (v = w_{yx}[0][0]).

A sensibilidade recorrente é calculada pela regra da cadeia:

\[
s_t = \frac{\partial x_t}{\partial w}
= (1-x_t^2)(x_{t-1}+w s_{t-1})
\]

\[
q_t = \frac{\partial y_t}{\partial w}
= (1-y_t^2)v s_t
\]

Para a perda MSE sobre (T) passos:

\[
J(w)=\frac{1}{T}\sum_{t=1}^{T}(y_t-r_t)^2,
\qquad
\frac{dJ}{dw}=\frac{2}{T}\sum_{t=1}^{T}(y_t-r_t)q_t
\]

A referência numérica é a diferença central:

\[
g_{FD}(w;\epsilon)=\frac{J(w+\epsilon)-J(w-\epsilon)}{2\epsilon}
\]

## Protocolo

- Comparar vários pesos recorrentes e epsilons.
- Registrar erro absoluto e relativo entre gradientes.
- Contabilizar avaliações completas de sequência: uma por peso para a derivada analítica e duas por par peso/epsilon para diferenças finitas.
- Manter o benchmark determinístico e sem dependências numéricas externas.

## Interpretação e limites

A derivada analítica é uma referência independente somente para esse regime escalar
simplificado. Não é BPTT genérico, não cobre os caminhos de memória/contexto/modulação
nem gradientes de uma rede multiunidade. A contagem de avaliações é uma medida
determinística de trabalho, não uma medição de tempo de parede. Concordância neste
protocolo valida a implementação nesse caso, não prova aprendizado geral ou inteligência.
