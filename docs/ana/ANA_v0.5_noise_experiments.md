# ANA v0.5 — Experimento de robustez a ruído

**Estado:** protocolo determinístico com múltiplas sementes  
**Implementação:** `ama.ana.benchmark.run_noise_robustness_benchmark`  
**Escopo:** rastreamento escalar de peso sob perturbação de atividades.

## Objetivo

Verificar se o comportamento observado no primeiro experimento permanece semelhante quando as atividades de entrada recebem ruído gaussiano limitado, usando várias sementes e as mesmas sequências para as três variantes.

## Protocolo

- Cinco sementes fixas: 7, 17, 27, 37 e 47.
- 40 passos por fase, quatro fases, 160 passos por semente.
- Amplitude do ruído gaussiano: desvio padrão 0,1; atividades limitadas a [-1, 1].
- Correlações-alvo ideais: +1, -1, 0 e +1.
- Cada variante recebe exatamente a mesma sequência ruidosa dentro de cada semente.
- Variantes: peso fixo, peso adaptativo sem alteração topológica e plasticidade estrutural v0.5.
- Parâmetros de plasticidade iguais aos do benchmark de referência.

A média e o desvio padrão são calculados sobre as cinco sementes. O desvio padrão reportado é populacional, não amostral.

## Resultados de referência

| Variante | Erro médio | Desvio padrão do erro | Fração ativa | Ativações médias | Desativações médias |
|---|---:|---:|---:|---:|---:|
| Fixa | 0,7500 | 0,0000 | 1,0000 | 0,0 | 0,0 |
| Peso adaptativo | 0,1405 | 0,0014 | 1,0000 | 0,0 | 0,0 |
| Estrutural | 0,1724 | 0,0021 | 0,8825 | 2,0 | 1,0 |

O ruído não alterou a conclusão do teste simples: a variante de peso adaptativo teve menor erro médio de rastreamento que a variante estrutural. A variante estrutural reduziu o tempo em que a conexão permaneceu ativa e realizou ativações e poda de forma repetível.

## Interpretação

Este resultado não prova que a topologia dinâmica seja pior em geral. O protocolo contém apenas uma conexão, quatro fases, uma amplitude de ruído e parâmetros fixos. O custo de ativação e a poda foram deliberadamente mantidos; em outra tarefa, o benefício de remover conexões irrelevantes pode superar o atraso observado aqui.

## Limitações e próximos testes

- Não mede desempenho preditivo da rede completa.
- Não testa ruído correlacionado, ruído impulsivo ou deriva gradual.
- Cinco sementes são uma amostra pequena.
- Não faz busca de hiperparâmetros nem validação fora da amostra.
- Não integra memória temporal multiescala ao mecanismo de plasticidade.

Próximo passo: variar sistematicamente ruído, duração das fases e taxa de mudança do padrão, e depois avaliar uma tarefa preditiva na rede completa. Não ajustar parâmetros com base no mesmo conjunto usado para reportar desempenho.
