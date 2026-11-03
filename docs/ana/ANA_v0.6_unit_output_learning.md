# ANA v0.6 — Aprendizado supervisionado dos parâmetros de saída da unidade

**Estado:** protótipo experimental em revisão no PR #17.  
**API:** `ama.ana.unit_learning.supervised_unit_output_step`.

## 1. Objetivo

A ANA v0.4 ajustava um vetor de pesos de um readout linear externo. A v0.6 introduz uma primeira atualização de parâmetros pertencentes à própria unidade neural: a projeção de saída.

Para uma unidade com estado atual ((x,m,c)), a saída local é recalculada por:

[
z = W_{yx}x + W_{ym}m + W_{yc}c + b_y
]

[
hat y = 	anh(z)
]

Dado um alvo supervisionado (y^*), define-se o erro:

[
e = y^* - hat y
]

Para perda quadrática e derivada da tangente hiperbólica, o sinal local de atualização é:

[
delta = e odot (1-hat y odot hat y)
]

As matrizes de saída e o viés são atualizados por gradiente local:

[
W_{yx}' = operatorname{clip}(W_{yx} + eta,delta x^T)
]

[
W_{ym}' = operatorname{clip}(W_{ym} + eta,delta m^T)
]

[
W_{yc}' = operatorname{clip}(W_{yc} + eta,delta c^T)
]

[
b_y' = operatorname{clip}(b_y + eta,delta)
]

Cada alteração individual e cada parâmetro possuem limites configuráveis. A API retorna a previsão e o erro anteriores à atualização, os novos parâmetros e a maior alteração efetivamente aplicada.

## 2. O que é treinado

Somente:
- `w_yx`: influência do estado instantâneo na saída;
- `w_ym`: influência da memória na saída;
- `w_yc`: influência do contexto na saída;
- `b_y`: viés da saída.

Os parâmetros que definem a evolução de (x), (m), (c) e (g) permanecem fixos.

## 3. O que ainda não é treinado

Esta versão **não implementa backpropagation through time**, não deriva a perda através das transições recorrentes, não atualiza `w_xx`, `w_xm`, `w_xc`, `w_xu`, `w_xr`, matrizes de memória/contexto/modulação ou pesos das conexões da rede por gradiente. Também não atribui automaticamente alvos às unidades de uma rede.

É aprendizado supervisionado local da projeção de saída interna, não treinamento completo da ANA.

## 4. Integridade e limites

- Atualização explícita; inferência não altera parâmetros.
- Estados e parâmetros de entrada são imutáveis.
- Dimensões e valores finitos são validados.
- Alvos, características, pesos e atualizações têm limites configuráveis.
- A mesma entrada produz a mesma atualização.
- O chamador é responsável por fornecer alvos legítimos e dados de treino.

## 5. Critérios experimentais

Os testes verificam direção da atualização, redução do erro em um caso controlado, múltiplas saídas, limites, validação e imutabilidade. Isso valida o mecanismo local, mas não prova convergência geral, utilidade em tarefas complexas ou capacidade cognitiva.

## 6. Próximas etapas

1. Medir aprendizado em uma sequência temporal usando a própria saída da unidade.
2. Comparar projeção fixa e projeção treinável em dados de treino e avaliação separados.
3. Estudar atribuição de erro às unidades em rede, evitando atribuir alvos artificiais sem justificativa.
4. Só então investigar gradientes locais ou aproximações de crédito temporal para a dinâmica recorrente.
