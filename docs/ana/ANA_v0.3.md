# ANA v0.3 — Memória Temporal e Contexto em Múltiplas Escalas

**Projeto:** AMA — Autonomous Money AI  
**Linha:** ANA — AMA Neural Architecture  
**Versão:** 0.3  
**Estado:** componente experimental isolado; integrado à `main` pelo PR #26

## 1. Objetivo

A ANA v0.1 definiu a memória local de cada unidade. A v0.2 organizou unidades em uma rede recorrente. A v0.3 introduz um mecanismo temporal separado, capaz de manter representações do sinal de entrada em diferentes escalas de retenção e combiná-las em um vetor de contexto.

A memória multiescala não substitui a memória local (m_i(t)) da unidade nem altera retroativamente as equações anteriores. A origem do sinal é definida pelo chamador. A integração automática desse contexto à rede é deliberadamente deixada para uma etapa posterior.

## 2. Sinal e escalas

Em cada passo discreto (t), o componente recebe um vetor finito (s(t) \in \mathbb{R}^{d_s}).

São definidas (K \geq 2) escalas, ordenadas da mais rápida à mais lenta. Cada escala (k) possui identificador estável (id_k), retenção \(\rho_k\) e peso de contribuição \(a_k\).

As retenções devem satisfazer:

\[
0 \leq \rho_1 < \rho_2 < \cdots < \rho_K < 1
\]

Os pesos devem ser finitos, não negativos e pelo menos um deve ser positivo.

## 3. Estado e atualização

O estado temporal é:

\[
M(t) = \{z_1(t), z_2(t), \ldots, z_K(t)\}
\]

Cada traço tem dimensão (d_s). Todas as escalas recebem o mesmo sinal atual e usam somente seu próprio estado anterior:

\[
z_k(t) = \rho_k z_k(t-1) + (1-\rho_k)s(t)
\]

A atualização é síncrona. Nenhuma escala utiliza o traço atualizado de outra escala no mesmo passo. Com estado inicial zero e entradas limitadas componente a componente por (B), cada traço permanece no intervalo limitado por (B), por ser uma combinação convexa do estado anterior e da entrada atual.

## 4. Construção do contexto

O contexto é a soma ponderada normalizada dos traços já atualizados:

\[
c_{multi}(t) =
\frac{\sum_{k=1}^{K} a_k z_k(t)}
{\sum_{k=1}^{K} a_k}
\]

O resultado tem dimensão (d_s). Pesos iguais representam contribuição uniforme; pesos diferentes expressam prioridade configurada, não aprendida. A implementação normaliza os pesos antes da combinação para evitar overflow na soma dos pesos finitos.

## 5. Contratos e invariantes

- Pelo menos duas escalas.
- IDs de escala únicos e não vazios.
- Retenções finitas em ([0,1)), estritamente crescentes.
- Pesos finitos, não negativos e pelo menos um positivo.
- Um vetor por escala, todos com a dimensão do sinal.
- Sinais e estados contêm apenas valores numéricos finitos.
- Transição pura: estado e parâmetros anteriores não são modificados.
- Entradas idênticas produzem resultados idênticos.
- Overflow aritmético é rejeitado em vez de propagar estado inválido.
- O componente não acessa rede, arquivos, relógio ou serviços externos.

## 6. Relação com v0.1 e v0.2

A memória local da unidade continua responsável pelo estado interno individual. A rede v0.2 continua responsável pela propagação relacional entre unidades. O módulo v0.3 mantém traços temporais paralelos de um sinal fornecido pelo chamador e produz um contexto agregado.

Não há acoplamento automático com a saída da rede, alteração dos estados das unidades ou retroalimentação nesta versão. Essa separação permite validar a dinâmica temporal isoladamente.

## 7. Não objetivos

A v0.3 não implementa aprendizado dos coeficientes, memória episódica simbólica, recuperação por consulta, atenção, esquecimento seletivo, associação semântica, linguagem natural ou consciência. Também não demonstra que as escalas escolhidas são cognitivamente adequadas.

## 8. Critérios de aceitação

1. Retenção zero acompanha imediatamente o sinal atual.
2. Retenções maiores preservam mais do histórico anterior.
3. Todas as escalas são atualizadas a partir do mesmo sinal atual.
4. O contexto é a média ponderada normalizada dos traços atualizados.
5. Dimensões inconsistentes, valores não finitos e parâmetros inválidos são rejeitados.
6. O estado anterior não é modificado.
7. Resultados determinísticos e testes automatizados cobrem os contratos.
