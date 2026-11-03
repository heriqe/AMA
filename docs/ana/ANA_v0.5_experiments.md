# ANA v0.5 — Relatório de experimento sintético

**Estado:** experimento determinístico reproduzível  
**Implementação:** `ama.ana.benchmark.run_plasticity_benchmark`  
**Escopo:** rastreamento de peso de uma conexão escalar; não é benchmark de inteligência.

## Pergunta

Como a plasticidade estrutural da v0.5 se comporta, em comparação com uma conexão fixa e com adaptação de peso sem mudanças topológicas, quando a correlação entre duas atividades muda ao longo do tempo?

## Protocolo

O experimento executa quatro fases de 40 passos (160 observações no total), sem aleatoriedade:

| Fase | Correlação-alvo | Atividade pré | Atividade pós |
|---|---:|---:|---:|
| 1 | +1 | +1 | +1 |
| 2 | -1 | +1 | -1 |
| 3 | 0 | 0 | 0 |
| 4 | +1 | +1 | +1 |

As três variantes são:

1. **Fixa:** peso constante de 0,05.
2. **Peso adaptativo:** mesma regra Hebbiana limitada e decaimento da v0.5, mas a conexão permanece ativa; não há ativação nem poda.
3. **Estrutural:** mecanismo completo da v0.5, iniciando com a candidata inativa; ativa após três passos consecutivos de coativação e poda após três passos consecutivos abaixo do limiar.

Parâmetros: taxa de aprendizado 0,2; decaimento 0,1; limite absoluto de peso 1,0; limiar de ativação 0,5; peso inicial 0,05; limiar de poda 0,08. Todos os valores de atividade estão em [-1, 1].

## Métricas

- **Erro absoluto médio de rastreamento:** média de `abs(peso - correlação_alvo)`. É um proxy da qualidade de rastreamento do peso, não erro de previsão da rede.
- **Magnitude média do peso:** média de `abs(peso)`.
- **Fração de passos ativa:** proporção dos passos em que a conexão está ativa.
- **Ativações/desativações:** transições topológicas observadas.

## Resultado de referência

Execução determinística com 40 passos por fase:

| Variante | Erro absoluto médio | Magnitude média | Fração ativa | Ativações | Desativações |
|---|---:|---:|---:|---:|---:|
| Fixa | 0,7500 | 0,0500 | 1,0000 | 0 | 0 |
| Peso adaptativo | 0,1323 | 0,7450 | 1,0000 | 0 | 0 |
| Estrutural | 0,1643 | 0,7066 | 0,8813 | 2 | 1 |

A variante adaptativa sem mudanças topológicas teve menor erro de rastreamento neste protocolo do que a variante estrutural. A estrutura dinâmica reduziu a fração de atividade e conseguiu reativar a candidata após a fase sem correlação, mas pagou o custo do atraso de ativação e da poda. Portanto, **este experimento não demonstra superioridade da plasticidade estrutural**.

## Limitações

- Apenas duas unidades abstratas e uma conexão candidata.
- Sequência determinística, sem ruído, sem múltiplas sementes e sem perturbações estocásticas.
- O alvo é correlação de atividade, não desempenho em uma tarefa cognitiva.
- Não mede propagação da rede, memória temporal, generalização ou aprendizado ponta a ponta.
- Os parâmetros foram escolhidos para tornar as transições observáveis, não otimizados em validação independente.

## Próximos experimentos

1. Repetir com ruído controlado e várias sementes fixas.
2. Variar duração das fases e intensidade de correlação.
3. Fazer varredura de taxa de aprendizado, decaimento e limiares.
4. Medir recuperação após mudanças abruptas e graduais.
5. Avaliar tarefas de previsão com a rede completa, comparando topologia fixa e adaptativa sob o mesmo orçamento de parâmetros.

Nenhuma alteração de parâmetros deve ser considerada melhoria sem comparação pré-registrada, métricas e repetição reproduzível.
