# ANA v0.5 — Plasticidade e Conexões Dinâmicas Controladas

**Projeto:** AMA — Autonomous Money AI  
**Linha:** ANA — AMA Neural Architecture  
**Versão:** 0.5  
**Estado:** implementação experimental preparada na branch openhands/ana-development; revisão e integração pendentes  
**Compatibilidade:** Python 3.11+, biblioteca padrão, sem GPU ou serviço externo

## 1. Objetivo

Investigar adaptação limitada da conectividade da rede. A versão recebe um conjunto explícito, finito e imutável de pares candidatos. O mecanismo pode ajustar pesos de conexões ativas, ativar candidatas após coativação persistente e desativar conexões persistentemente fracas.

A v0.5 valida uma regra local de plasticidade. Não afirma que a regra melhora o desempenho cognitivo nem que garante estabilidade global da rede.

## 2. Modelo de candidatos

Cada candidato dirigido contém:

- identificador de origem e destino;
- peso escalar;
- estado ativo/inativo;
- contador de passos consecutivos de coativação;
- contador de passos consecutivos abaixo do limiar de poda.

O conjunto de pares é definido pelo chamador na inicialização e permanece fixo durante a execução. A v0.5 não cria unidades nem inventa novos pares. O limite inicial é de 100.000 candidatos, compatível com o limite de conexões da rede v0.2.

Pares ordenados devem ser únicos. Auto-conexões são permitidas porque a API de rede v0.2 não as proíbe; a plasticidade não deve restringir uma topologia já válida.

## 3. Atualização de peso

Para uma conexão ativa (i → j), com atividades finitas a_i(t) e a_j(t):

w_raw(t+1) = w(t) + η a_i(t)a_j(t) − λw(t)

w(t+1) = clip(w_raw(t+1), −W_max, W_max)

O termo de coativação é Hebbiano; o decaimento reduz persistência sem suporte. O clipping mantém cada peso dentro do limite configurado. Overflow aritmético é rejeitado explicitamente, não convertido silenciosamente em estado inválido.

## 4. Ativação de candidatas

Uma candidata inativa é considerada coativa quando |a_i(t)| ≥ θ_a e |a_j(t)| ≥ θ_a.

O contador consecutivo aumenta quando a condição é verdadeira e volta a zero quando falha. Ao atingir K passos consecutivos, a conexão é ativada com o peso inicial configurado. O peso inicial é atribuído nesse passo; a atualização Hebbiana começa no passo seguinte.

## 5. Poda de conexões

Depois da atualização de peso, uma conexão ativa cujo peso satisfaça |w(t+1)| < θ_p incrementa o contador de fraqueza.

Se o contador atingir P passos consecutivos, a conexão é desativada, seu peso é zerado e os contadores são reiniciados. Se o peso deixar de estar abaixo do limiar, o contador de poda volta a zero. Um limiar de poda igual a zero desabilita a poda.

## 6. Parâmetros e limites

- η: taxa de plasticidade finita e positiva.
- λ: decaimento finito em [0, 1].
- W_max: limite absoluto de peso, finito e positivo.
- A_max: limite absoluto de atividade, finito e positivo.
- θ_a: limiar de ativação em (0, A_max].
- K: número inteiro positivo de passos para ativação.
- θ_p: limiar de poda em [0, W_max).
- P: número inteiro positivo de passos para poda.
- w_init: peso inicial não nulo, finito e dentro de [-W_max, W_max].

IDs vazios, pares duplicados, atividades ausentes, números não finitos, dimensões/estados inválidos e limites excedidos são rejeitados. Contadores são inteiros não negativos e permanecem abaixo do respectivo limiar enquanto a conexão está no estado correspondente.

## 7. Estado e interface

A transição recebe explicitamente estado, mapa de atividades e parâmetros e retorna um novo estado imutável. Coleções recebidas do chamador são copiadas para tuplas; mutações posteriores nas listas originais não podem alterar snapshots já criados.

PlasticityState.active_connections() retorna as conexões ativas em ordem estável, usando o tipo Connection da rede v0.2. O chamador deve construir uma nova NetworkDefinition explicitamente. A plasticidade não modifica uma rede existente por efeitos colaterais.

## 8. Estabilidade e limites científicos

O limite absoluto garante apenas que os pesos individuais produzidos por este mecanismo permanecem limitados. Isso não prova estabilidade das ativações, convergência, ausência de oscilações, robustez geral a ruído ou benefício cognitivo. O experimento ruidoso em cinco sementes documenta apenas o protocolo específico descrito em ANA_v0.5_experiments.md; a avaliação em rede completa continua necessária.

## 9. Critérios de aceitação

1. Pesos ativos seguem a regra Hebbiana com decaimento e clipping.
2. Pesos nunca excedem o limite absoluto configurado.
3. Candidatas ativam somente após K passos consecutivos de coativação.
4. Uma quebra de coativação reinicia o contador.
5. Conexões fracas são podadas somente após P passos consecutivos.
6. O estado anterior permanece imutável, inclusive para entradas originalmente mutáveis.
7. Mesmas entradas, estado e parâmetros produzem resultados idênticos.
8. IDs, candidatos, contadores, atividades e parâmetros inválidos são rejeitados.
9. Conexões ativas podem ser convertidas para a API de rede v0.2.
10. Testes de estresse confirmam limites locais e ausência de valores não finitos ao longo de muitas transições.
11. O benchmark ruidoso usa fluxos compartilhados por variante, sementes explícitas e limites de carga para manter o experimento reproduzível e finito.

## 10. Plano de implementação

- Unidade 1: parâmetros, candidatos, estado imutável e transição pura.
- Unidade 2: integração explícita por active_connections() e testes de compatibilidade com NetworkDefinition.
- Unidade 3: benchmark sintético contra topologia fixa e plasticidade apenas de peso.
- Unidade 4: benchmark com ruído uniforme limitado e múltiplas sementes, executado e documentado; avaliação em rede completa permanece pendente.

## 11. Não objetivos

A v0.5 não cria unidades, não aprende pares candidatos, não altera automaticamente a definição de rede, não modifica parâmetros internos das unidades, não implementa backpropagation através da rede, não integra automaticamente o readout v0.4, não executa ações externas e não demonstra inteligência geral.
