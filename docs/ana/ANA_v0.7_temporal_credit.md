# ANA v0.7 — Crédito temporal por diferenças finitas

**Estado:** protótipo experimental em revisão no PR #19, dependente do PR #18.  
**API:** `ama.ana.temporal_credit.fit_recurrent_weight` e `run_temporal_credit_benchmark`.

## 1. Pergunta experimental

É possível ajustar um parâmetro da dinâmica recorrente de uma unidade usando o efeito que ele exerce sobre o erro acumulado ao longo de uma sequência, sem recorrer ainda a backpropagation through time?

## 2. Método

A implementação altera somente o escalar `w_xx[0][0]`, que controla a contribuição do estado anterior para o próximo estado interno.

Para uma sequência de entradas (u_{1:T}) e alvos (y_{1:T}), a função de custo é:

[
J(w) = rac{1}{T}sum_{t=1}^{T}
left(hat y_t(w;u_{1:t}) - y_tight)^2
]

A derivada é aproximada por diferenças finitas centrais:

[
rac{partial J}{partial w}
approx
rac{J(w+epsilon)-J(w-epsilon)}{2epsilon}
]

A atualização usa descida de gradiente com limites de peso e de passo. Cada avaliação de (J) reexecuta a sequência inteira desde o estado inicial. Assim, a perturbação do peso é avaliada por seus efeitos acumulados ao longo do tempo.

## 3. Benchmark

O benchmark usa uma sequência sintética limitada cuja meta depende do valor atual e do valor anterior:

[
y_t = 0.55u_t + 0.35u_{t-1}
]

A unidade mantém fixa a projeção de entrada e saída; começa com peso recorrente zero. O treino ajusta apenas (w_{xx}). A avaliação usa um segmento futuro separado, com parâmetros congelados e estado aquecido ao reproduzir o segmento de treino.

Compara:
- dinâmica fixa, com (w_{xx}=0);
- dinâmica treinada pelo objetivo temporal.

## 4. Escopo e limitações

- É uma aproximação numérica de crédito temporal por otimização da sequência, não BPTT.
- Apenas uma unidade escalar e um parâmetro recorrente são suportados.
- O custo é maior que um gradiente analítico: cada época requer duas reexecuções completas da sequência.
- Não treina memória, contexto, modulação, conexões entre unidades nem matrizes recorrentes gerais.
- Não oferece garantia de convergência, estabilidade geral ou generalização fora da tarefa sintética.
- A avaliação é uma demonstração controlada de mecanismo, não evidência de inteligência.

## 5. Próximos experimentos

1. Comparar diferenças finitas com derivadas analíticas em uma unidade pequena.
2. Medir custo computacional e sensibilidade a epsilon, taxa de aprendizado e comprimento da sequência.
3. Expandir para múltiplos parâmetros com orçamento de otimização explícito.
4. Investigar propagação de crédito temporal em rede com várias unidades, preservando comparação com topologia fixa.
