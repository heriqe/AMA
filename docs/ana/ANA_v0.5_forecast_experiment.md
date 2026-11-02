# ANA v0.5 — Previsão temporal com a rede completa

**Estado:** benchmark experimental implementado; revisão pendente no PR #13  
**Implementação:** `ama.ana.forecast.run_forecast_benchmark`  
**Tarefa:** previsão de um passo à frente em uma série sintética AR(2)-like.

## Pergunta experimental

Uma rede ANA recorrente de duas unidades, com estado interno e realimentação relacional, pode produzir representações úteis para prever o próximo valor de uma sequência? A adaptação de peso ou a plasticidade estrutural altera o erro em dados não usados para atualizar o readout?

## Protocolo

- Sequência determinística limitada, gerada com uma semente explícita.
- Divisão temporal: segmento inicial de treino e segmento final de avaliação.
- Três variantes: conexão fixa, peso adaptativo sem mudança topológica e plasticidade estrutural.
- As três variantes recebem a mesma sequência, arquitetura local e regra de readout.
- A rede completa é executada a cada passo por `step_network`; o estado recorrente é mantido entre passos.
- Um readout linear escalar com sete características da rede é atualizado por LMS somente no segmento de treino.
- A plasticidade de conexões também é atualizada somente no segmento de treino e fica congelada durante a avaliação.
- O estado dinâmico da rede continua através da fronteira treino/avaliação.
- A previsão de persistência (`x[t+1] = x[t]`) é reportada como baseline separada.

## O que o experimento mede

MSE e MAE no segmento temporal final, além do peso e estado final da conexão candidata. A métrica principal é o erro de previsão fora do segmento usado para atualizar o readout.

## Limites de interpretação

Este experimento **não treina os parâmetros internos das unidades nem realiza backpropagation através da rede**. O LMS ajusta somente um readout linear externo; a plasticidade modifica apenas a conexão candidata explicitamente declarada. A sequência sintética é estacionária e simples, a arquitetura tem duas unidades e uma conexão candidata, e o resultado usa uma única semente por execução. Portanto, o resultado não demonstra inteligência, compreensão, generalização para dados reais ou superioridade geral de uma variante.

O teste verifica reprodutibilidade, validação de parâmetros, separação temporal e produção de métricas finitas. Para conclusões científicas mais fortes, serão necessários múltiplas sementes, tarefas com mudanças de regime, intervalos de incerteza, baselines adicionais e avaliação em sequências independentes.
