# ANA v0.5 — Adaptação a mudança de regime

**Estado:** experimento implementado; revisão pendente no PR #15, dependente do PR #14.  
**Implementações:** `ama.ana.forecast.run_regime_shift_benchmark` e `run_regime_shift_suite`.

## Pergunta

Quando a relação temporal dos dados muda, a ANA consegue adaptar o readout e as conexões candidatas durante uma janela controlada e depois manter desempenho em uma avaliação sem aprendizado?

## Protocolo

A sequência sintética AR(2)-like começa com coeficientes `0.72` e `-0.18`. Após o segmento inicial, ocorre uma mudança para `0.15` e `0.55`, mantendo ruído gaussiano limitado e a mesma semente entre execuções.

O protocolo tem três fases:

1. **Treino inicial:** todas as variantes ajustam o readout no primeiro regime.
2. **Adaptação:** após a mudança, as variantes adaptativas continuam atualizando o readout; as variantes de peso e estrutural também podem modificar a conexão candidata. A variante `frozen` não aprende após a mudança.
3. **Avaliação final:** readouts e conexões ficam congelados; somente o estado dinâmico da rede continua evoluindo.

Variantes comparadas:
- `frozen`: sem atualização após a mudança de regime;
- `fixed_adaptive`: readout adapta, conexão fica fixa;
- `weight_only`: readout e peso da conexão adaptam, sem mudar topologia;
- `structural`: readout e plasticidade estrutural limitada adaptam.

## Métricas

O relatório fornece MSE durante a janela de adaptação, MSE/MAE na avaliação final e baseline de persistência na avaliação. Os pesos e estados finais da conexão candidata também são registrados.

## Agregação multi-semente

`run_regime_shift_suite` executa o protocolo com sementes únicas, mantém os relatórios individuais para comparações pareadas e calcula médias e desvios padrão populacionais de MSE na adaptação e avaliação, além de MAE na avaliação. A baseline de persistência também é agregada. O desvio padrão é descritivo: não representa intervalo de confiança nem teste de significância.

## Limites

A tarefa é sintética e usa duas unidades e uma conexão candidata. O LMS atualiza somente um readout externo; os parâmetros internos das unidades não são treinados. O experimento mede adaptação em uma mudança de regime específica, não inteligência, entendimento ou generalização para dados reais. A agregação multi-semente reduz dependência de uma única sequência, mas ainda usa uma única família sintética e uma mudança de regime específica. Não é evidência suficiente de generalização para problemas reais.
