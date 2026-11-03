# ANA v0.3 — Memória Temporal e Contexto em Múltiplas Escalas

**Projeto:** AMA — Autonomous Money AI  
**Linha:** ANA — AMA Neural Architecture  
**Versão:** 0.3  
**Estado:** especificação e protótipo experimental

## 1. Objetivo

A ANA v0.1 definiu a memória local de cada unidade. A v0.2 organizou unidades em uma rede recorrente. A v0.3 introduz um mecanismo temporal separado, capaz de manter representações do sinal de entrada em diferentes escalas de retenção e combiná-las em um vetor de contexto.

A memória multiescala é um componente explícito e testável. Ela não substitui a memória local m_i(t) da unidade, nem altera retroativamente a equação da v0.1. A integração desse contexto à rede será uma etapa posterior, após validação do componente isolado.

## 2. Sinal e escalas

Em cada passo discreto t, o componente recebe um vetor finito s(t) em R^d_s.

São definidas K >= 2 escalas ordenadas da mais rápida à mais lenta. Cada escala k possui identificador estável id_k, retenção rho_k em [0,1) e peso de contribuição a_k >= 0.

As retenções devem ser estritamente crescentes: 0 <= rho_1 < rho_2 < ... < rho_K < 1.

## 3. Estado multiescala

O estado temporal é M(t) = {z_1(t), z_2(t), ..., z_K(t)}. Cada traço z_k(t) tem a mesma dimensão do sinal.

## 4. Atualização temporal

Cada escala recebe o mesmo snapshot do sinal atual:

z_k(t) = rho_k * z_k(t-1) + (1-rho_k) * s(t)

A atualização é síncrona: nenhum traço usa outro traço já atualizado no mesmo passo. Com estado inicial zero e sinal limitado componente a componente por B, cada traço permanece limitado por B.

## 5. Construção do contexto

O contexto multiescala é a combinação normalizada dos traços atualizados:

c_multi(t) = sum(a_k * z_k(t)) / sum(a_k)

O resultado tem dimensão d_s. Pesos iguais representam contribuição uniforme; pesos diferentes expressam prioridade explícita, não aprendida, entre escalas.

## 6. Inicialização

Todos os traços começam em zero. A escolha de retenções e pesos é configuração experimental. Esta versão não aprende esses valores.

## 7. Contratos e invariantes

- São necessárias pelo menos duas escalas.
- IDs de escala são únicos e não vazios.
- Retenções são finitas, pertencem a [0,1) e crescem da escala rápida para a lenta.
- Pesos são finitos, não negativos e pelo menos um é positivo.
- Cada escala possui exatamente um vetor com a dimensão do sinal.
- Sinais e estados devem conter apenas valores finitos.
- A transição é pura: não altera estado ou parâmetros anteriores.
- A mesma entrada, estado e parâmetros produzem o mesmo resultado.
- O componente não acessa rede, arquivos, relógio ou serviços externos.

## 8. Relação com v0.1 e v0.2

A memória local da unidade continua responsável pelo estado interno individual. A rede v0.2 continua responsável pela propagação relacional entre unidades. O módulo multiescala v0.3 mantém traços temporais paralelos de um sinal fornecido pelo chamador e produz um contexto agregado.

Nesta versão, a origem do sinal é externa ao módulo. Não há acoplamento automático com a saída da rede, alteração dos estados das unidades ou retroalimentação. Essa separação permite validar primeiro a dinâmica temporal sem misturar três mecanismos em uma única transição.

## 9. Não objetivos

A v0.3 não implementa aprendizado dos coeficientes, memória episódica simbólica, recuperação por consulta, atenção, esquecimento seletivo, associação semântica, linguagem natural ou consciência. Também não demonstra que as escalas escolhidas são cognitivamente adequadas.

## 10. Critérios de aceitação

1. Uma escala com retenção zero acompanha imediatamente o sinal atual.
2. Retenções maiores preservam mais do histórico anterior.
3. Todas as escalas são atualizadas a partir do mesmo sinal atual.
4. O contexto é a média ponderada normalizada dos traços atualizados.
5. Dimensões inconsistentes, valores não finitos e parâmetros inválidos são rejeitados.
6. A transição não modifica o estado anterior.
7. Os resultados são determinísticos e cobertos por testes.

## 11. Próximas etapas

- ANA v0.4: mecanismos de adaptação/aprendizado com objetivos, métricas e proteção contra instabilidade.
- ANA v0.5: conexões dinâmicas e integração experimental controlada dos componentes temporais.
- ANA 1.0: interface testada para integração com o Cognitive Core.

Resultados negativos e limitações devem ser documentados junto aos resultados positivos.