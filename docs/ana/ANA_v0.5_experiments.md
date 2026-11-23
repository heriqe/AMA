# ANA v0.5 — Plano de avaliação experimental

**Estado:** benchmark de referência e experimento com ruído em cinco sementes executados; avaliação em rede completa pendente.  
**Implementação:** ama.ana.plasticity e ama.ana.benchmark.

## Pergunta

Como o mecanismo de plasticidade de conexões candidatas se comporta, em uma sequência sintética com mudança de correlação, em comparação com uma conexão fixa e com adaptação de peso sem alteração topológica?

## Protocolo de referência

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

## Resultado do protocolo de referência

Execução com 40 passos por fase (160 observações), conforme o protocolo acima:

| Variante | Erro absoluto médio | Magnitude média | Fração ativa | Ativações | Desativações | Máximo |
|---|---:|---:|---:|---:|---:|---:|
| Fixa | 0,7500 | 0,0500 | 1,0000 | 0 | 0 | 0,0500 |
| Peso adaptativo | 0,1323 | 0,7450 | 1,0000 | 0 | 0 | 1,0000 |
| Estrutural | 0,1643 | 0,7066 | 0,8813 | 2 | 1 | 1,0000 |

Neste protocolo, a variante adaptativa sem mudanças topológicas apresentou menor erro de rastreamento que a variante estrutural. A ativação e a poda reduziram a fração de passos ativa e introduziram atraso nas mudanças de regime. Portanto, o experimento não demonstra superioridade da plasticidade estrutural.

## Experimento com ruído e múltiplas sementes

A função run_noisy_plasticity_benchmark executa as mesmas quatro fases com ruído uniforme independente em cada atividade. O ruído é somado à atividade-base e o resultado é limitado ao intervalo [-1, 1]. Para cada semente, as três variantes recebem exatamente o mesmo fluxo de observações.

Configuração registrada:

- 40 passos por fase;
- amplitude de ruído: 0,1;
- sementes: 0, 1, 2, 3 e 4;
- 160 observações por semente; 800 observações no total;
- desvio-padrão populacional calculado sobre os cinco erros médios por semente.

| Variante | Erro absoluto médio | Desvio entre sementes | Fração ativa média | Ativações médias | Desativações médias | Máximo |
|---|---:|---:|---:|---:|---:|---:|
| Fixa | 0,714809 | 0,002486 | 1,0000 | 0,0 | 0,0 | 0,0500 |
| Peso adaptativo | 0,158971 | 0,003401 | 1,0000 | 0,0 | 0,0 | 1,0000 |
| Estrutural | 0,188558 | 0,003151 | 0,8825 | 2,0 | 1,0 | 1,0000 |

Neste protocolo ruidoso, a variante apenas de peso também apresentou menor erro médio que a variante estrutural. A dispersão entre as cinco sementes foi pequena para esta configuração, mas cinco sementes não sustentam uma conclusão estatística ampla. O resultado não demonstra superioridade geral, robustez em redes maiores ou benefício cognitivo.

## Limitações e próximos experimentos

O experimento usa uma única conexão abstrata, quatro regimes abruptos, ruído uniforme limitado e parâmetros fixos. Não mede propagação em uma rede completa, generalização, estabilidade global, robustez a outros tipos de ruído ou desempenho cognitivo. A avaliação em rede completa, com mais sementes, ruído variado e mudanças graduais de regime permanece pendente.

Os resultados são determinísticos para as sementes e a versão do protocolo registradas; não devem ser generalizados para outras tarefas, topologias ou distribuições.
