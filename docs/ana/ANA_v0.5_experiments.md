# ANA v0.5 — Plano de avaliação experimental

**Estado:** benchmark sintético determinístico executado; experimentos de ruído e múltiplas sementes pendentes.  
**Implementação:** `ama.ana.plasticity` e `ama.ana.benchmark`.

## Pergunta

Como o mecanismo de plasticidade de conexões candidatas se comporta, em uma sequência sintética com mudança de correlação, em comparação com uma conexão fixa e com adaptação de peso sem alteração topológica?

## Protocolo inicial

Executar quatro fases determinísticas, cada uma com 40 passos:

| Fase | Alvo de correlação | Atividade pré | Atividade pós |
|---|---:|---:|---:|
| 1 | +1 | +1 | +1 |
| 2 | -1 | +1 | -1 |
| 3 | 0 | 0 | 0 |
| 4 | +1 | +1 | +1 |

Variantes:

1. **Fixa:** peso constante de 0,05.
2. **Peso adaptativo:** mesma regra de atualização e clipping, sem ativação ou poda.
3. **Estrutural:** candidata inicialmente inativa, ativação e poda por persistência.

Parâmetros iniciais: taxa 0,2; decaimento 0,1; limite de peso 1,0; limiar de ativação 0,5 por três passos; peso inicial 0,05; limiar de poda 0,08 por três passos. Atividades ficam em [-1, 1].

## Métricas

- Erro absoluto médio entre peso e produto-alvo de atividade. É proxy de rastreamento de correlação, não erro preditivo da rede.
- Magnitude média absoluta do peso.
- Fração de passos em que a conexão permanece ativa.
- Quantidade de ativações e desativações.
- Maior magnitude de peso observada.

## Limitações do protocolo

Este teste inicial usa uma única conexão abstrata e uma sequência sem ruído. Não mede desempenho cognitivo, propagação em uma rede completa, generalização, robustez estatística ou estabilidade global. Experimentos com ruído, múltiplas sementes e mudanças graduais de regime permanecem pendentes.


## Resultado do protocolo de referência

Execução com 40 passos por fase (160 observações), conforme o protocolo acima:

| Variante | Erro absoluto médio | Magnitude média | Fração ativa | Ativações | Desativações | Máximo | 
|---|---:|---:|---:|---:|---:|---:|
| Fixa | 0,7500 | 0,0500 | 1,0000 | 0 | 0 | 0,0500 |
| Peso adaptativo | 0,1323 | 0,7450 | 1,0000 | 0 | 0 | 1,0000 |
| Estrutural | 0,1643 | 0,7066 | 0,8813 | 2 | 1 | 1,0000 |

Neste protocolo, a variante adaptativa sem mudanças topológicas apresentou menor erro de rastreamento que a variante estrutural. A ativação e a poda reduziram a fração de passos ativa e introduziram atraso nas mudanças de regime. Portanto, **o experimento não demonstra superioridade da plasticidade estrutural**.

O resultado é determinístico e específico desta sequência e destes parâmetros. Não deve ser generalizado para outras tarefas, topologias ou distribuições.
