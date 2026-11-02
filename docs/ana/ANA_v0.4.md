# ANA v0.4 — Aprendizado e Adaptação Controlada

**Projeto:** AMA — Autonomous Money AI  
**Linha:** ANA — AMA Neural Architecture  
**Versão:** 0.4  
**Estado:** especificação e protótipo experimental

## 1. Objetivo

A v0.4 introduz regras explícitas de atualização de parâmetros. O objetivo é demonstrar três fontes de sinal de aprendizado em um componente pequeno, determinístico e limitado: erro supervisionado, recompensa relativa a uma linha de base e previsão do próximo valor observado.

Esta versão não treina a rede recorrente inteira. O protótipo ajusta um vetor de pesos de uma saída linear escalar. A integração com estados e conexões da rede fica para uma etapa posterior, após avaliação experimental.

## 2. Modelo adaptativo mínimo

Para pesos theta(t) e vetor de características phi(t), a previsão escalar é:

y_hat(t) = theta(t) · phi(t)

Os pesos são um vetor finito de dimensão d. A transição recebe um estado imutável, características e um sinal de aprendizado. Não há atualização implícita durante inferência: o chamador precisa invocar explicitamente uma regra de aprendizado.

## 3. Aprendizado supervisionado

Dado um alvo explícito y(t), o erro é:

e(t) = y(t) - y_hat(t)

A atualização LMS é:

theta(t+1) = clip_W(theta(t) + clip_U(eta * e(t) * phi(t)))

A função clip_U limita cada alteração individual por max_abs_update. clip_W mantém cada peso no intervalo [-max_abs_weight, max_abs_weight]. A atualização efetiva é retornada para auditoria.

## 4. Aprendizado por recompensa

O estado mantém uma elegibilidade por peso e uma linha de base móvel da recompensa.

E(t) = lambda * E(t-1) + phi(t)

A vantagem é:

A(t) = r(t) - b(t)

O peso é atualizado por:

theta(t+1) = clip_W(theta(t) + clip_U(eta * A(t) * E(t)))

A linha de base é atualizada por:

b(t+1) = b(t) + beta * (r(t) - b(t))

A recompensa é um sinal externo fornecido pelo chamador. Esta regra não define por si só uma política de ações, não garante causalidade e não impede reward hacking em sistemas reais. A origem, escala e legitimidade da recompensa precisam ser verificadas em camadas superiores.

## 5. Aprendizado autônomo por previsão

A regra autônoma usa o próximo valor observado como alvo auto-supervisionado:

e_pred(t) = s(t+1) - y_hat(t)

A atualização usa a mesma regra LMS, mas o alvo vem da sequência observada, não de um rótulo manual. Portanto, o mecanismo aprende uma previsão escalar de um passo; não equivale a descoberta geral de conceitos ou compreensão semântica.

## 6. Limites e estabilidade

A configuração define taxa de aprendizado positiva e finita, decaimento de elegibilidade em [0,1), taxa de atualização da linha de base em (0,1], limite absoluto de peso, limite absoluto de atualização por peso e passo e limite absoluto para alvos e recompensas.

Entradas não finitas, dimensões incompatíveis, estados inválidos e sinais fora dos limites são rejeitados. Os estados são imutáveis. O mecanismo é determinístico para os mesmos parâmetros, estado e entrada.

Os limites impedem explosão ilimitada dos pesos por uma única transição, mas não provam convergência nem qualidade. Taxas, escalas e desempenho precisam de experimentos e baselines.

## 7. Separação entre regras

As três regras são funções explícitas sobre um mesmo estado de leitura adaptativa. Elas não devem ser somadas cegamente no mesmo passo. Uma política experimental superior deverá definir qual sinal está disponível, qual regra será aplicada e como comparar resultados sem misturar alvos incompatíveis.

## 8. Não objetivos

A v0.4 não implementa backpropagation através da rede ANA, otimização de matrizes de conexão, plasticidade estrutural, escolha autônoma de objetivos, aprendizado por linguagem natural, replay episódico ou garantia contra reward hacking. Não demonstra inteligência geral nem melhoria cognitiva.

## 9. Critérios de aceitação

1. Erro supervisionado zero não altera pesos.
2. Erro supervisionado não nulo atualiza pesos na direção do alvo.
3. Aprendizado autônomo prevê o próximo valor observado e atualiza por erro.
4. Recompensa altera pesos por vantagem e elegibilidade.
5. A linha de base de recompensa acompanha a média móvel definida.
6. Peso e atualização permanecem dentro dos limites.
7. Estados anteriores não são mutados.
8. Entradas inválidas são rejeitadas.
9. Os resultados são determinísticos e testados.

## 10. Próximas etapas

- ANA v0.5: estudar plasticidade/conexões dinâmicas com experimentos comparativos e limites.
- ANA 1.0: definir interfaces para integração controlada com o Cognitive Core.

Nenhuma alegação de aprendizado útil deve ser feita sem métricas, conjuntos de teste, baselines e resultados reproduzíveis.