# ANA v0.6 — Previsão temporal com aprendizado da unidade

**Estado:** benchmark experimental em revisão no PR #18, dependente do PR #17.  
**API:** `ama.ana.unit_forecast.run_unit_forecast_benchmark` e `run_unit_forecast_suite`.

## Pergunta

O aprendizado supervisionado da projeção de saída interna de uma unidade reduz o erro de previsão em valores futuros, em comparação com manter a projeção fixa?

## Protocolo

- Série sintética AR(1) limitada, com coeficiente 0,78 e ruído gaussiano de desvio 0,06.
- Divisão temporal contígua: segmento inicial de treino e segmento final de avaliação.
- Duas variantes com os mesmos parâmetros de dinâmica de estado:
  - `fixed`: projeção de saída permanece fixa;
  - `learned`: atualiza somente `w_yx` e `b_y` durante o treino.
- Durante a avaliação, todos os parâmetros ficam congelados.
- A baseline de persistência prevê que o próximo valor será igual ao valor atual.
- O modo multi-semente preserva relatórios pareados e agrega MSE/MAE por média e desvio padrão populacional.

## O que o experimento mede

MSE e MAE em amostras futuras não usadas para atualização, dispersão entre sementes e parâmetros finais da projeção treinável.

## Limites

O teste usa uma unidade, uma série sintética estacionária e um estado interno cuja dinâmica permanece fixa. Apenas a projeção de saída é treinada; memória, contexto, modulação, transição recorrente e conexões de rede não são otimizados. A tarefa é simples e não demonstra generalização para dados reais, aprendizado de conceitos ou inteligência.

O benchmark serve como primeira validação quantitativa do mecanismo de aprendizado interno local. Próximas etapas devem ampliar as tarefas, comparar múltiplas sementes e, separadamente, pesquisar crédito temporal para os parâmetros que geram os estados internos.
