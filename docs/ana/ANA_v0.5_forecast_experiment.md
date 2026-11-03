# ANA v0.5 — Previsão temporal com a rede completa

**Estado:** benchmark experimental; revisão em PRs #13 e #14 (dependentes em sequência)  
**Implementações:** `ama.ana.forecast.run_forecast_benchmark` e `run_forecast_suite`  
**Tarefa:** previsão de um passo à frente em uma série sintética AR(2)-like.

## Pergunta experimental

Uma rede ANA recorrente de duas unidades, com estado interno e realimentação relacional, pode produzir representações úteis para prever o próximo valor de uma sequência? A adaptação de peso ou a plasticidade estrutural altera o erro em dados posteriores aos usados no ajuste?

## Protocolo por semente

- Sequência determinística limitada, gerada com uma semente explícita.
- Divisão temporal: segmento inicial de treino e segmento final de avaliação.
- Três variantes: conexão fixa, peso adaptativo sem mudança topológica e plasticidade estrutural.
- As três variantes recebem a mesma sequência, arquitetura local e regra de readout.
- A rede completa é executada a cada passo por `step_network`; o estado recorrente é mantido entre passos.
- Um readout linear escalar com sete características da rede é atualizado por LMS somente no segmento de treino.
- A adaptação de conexões também ocorre somente no segmento de treino e fica congelada durante a avaliação.
- O estado dinâmico da rede continua através da fronteira treino/avaliação.
- A previsão de persistência (`x[t+1] = x[t]`) é reportada como baseline separada.

## Protocolo multi-semente

`run_forecast_suite` executa o mesmo protocolo para uma tupla de sementes únicas, preserva os relatórios individuais para comparação pareada e calcula média e desvio padrão populacional de MSE e MAE por estratégia. A baseline de persistência também é agregada.

O desvio padrão é uma estatística descritiva da dispersão entre sementes. **Não é intervalo de confiança, teste de significância nem evidência causal.** As estratégias são comparadas nas mesmas sequências de cada semente, mas sementes diferentes geram sequências distintas.

## O que o experimento mede

MSE e MAE no segmento temporal final, dispersão entre sementes, peso e estado final da conexão candidata. A métrica principal é o erro de previsão fora do segmento usado para atualizar o readout.

## Limites de interpretação

Este experimento **não treina os parâmetros internos das unidades nem realiza backpropagation através da rede**. O LMS ajusta somente um readout linear externo; a adaptação de peso altera uma conexão fixa e a variante estrutural pode ativar/podar somente uma conexão candidata explícita. A sequência é sintética, a arquitetura tem duas unidades e uma conexão candidata. Portanto, o resultado não demonstra inteligência, compreensão, generalização para dados reais ou superioridade geral de uma variante.

A avaliação multi-semente reduz a dependência de uma única realização, mas ainda não inclui mudanças de regime. Próximos experimentos devem testar sequências independentes, relações temporais não estacionárias, baselines adicionais e intervalos de incerteza apropriados.
