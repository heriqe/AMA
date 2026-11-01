# Cognitive Core v0.3 — Decisão determinística sob restrições

**Estado:** protótipo experimental  
**Módulo:** `ama.decision`

## Objetivo

Avaliar alternativas usando estimativas declaradas, orçamento disponível, risco, qualidade da evidência e necessidade de aprovação humana. O componente produz uma recomendação auditável ou se abstém. Ele não executa tarefas, não gasta dinheiro e não transforma estimativas em fatos.

## Dados de entrada

Cada alternativa contém:
- identificador e descrição;
- receita projetada (não realizada);
- custo estimado;
- moeda ISO de três letras;
- risco declarado em ([0,1]);
- confiança da evidência em ([0,1]), fornecida pela origem e não calibrada como probabilidade;
- indicador de necessidade de aprovação humana.

O orçamento representa um limite informado para planejamento. Não representa saldo bancário verificado nem permissão para gastar.

Valores monetários usam `Decimal`; valores `float` são rejeitados para evitar imprecisão binária em dinheiro.

## Restrições duras

Uma alternativa não é elegível quando:
1. moeda difere da moeda do orçamento;
2. custo estimado supera o orçamento;
3. risco excede o máximo da política;
4. confiança da evidência está abaixo do limiar;
5. valor líquido projetado está abaixo do mínimo;
6. exige aprovação humana explícita.

A avaliação não escolhe a alternativa "menos ruim" quando todas falham. Nesse caso, retorna `abstained=true`.

## Pontuação

Para candidatos elegíveis:

[
N_i=R_i-C_i
]

[
S_i=\frac{N_i}{\max(B,1)}-\lambda\,Q_i
]

Onde:
- (R_i): receita projetada;
- (C_i): custo estimado;
- (B): orçamento disponível na moeda declarada;
- (Q_i): risco informado entre 0 e 1;
- (\lambda): peso de penalização de risco entre 0 e 1;
- (N_i): valor líquido projetado;
- (S_i): pontuação normalizada, sem unidade monetária.

O sistema escolhe a maior pontuação elegível. Empates são resolvidos pelo ID em ordem lexicográfica, garantindo determinismo.

Esta pontuação é uma heurística transparente, não uma probabilidade de sucesso, previsão estatística calibrada ou garantia de lucro. O motor não tenta estimar receitas ou custos por conta própria.

## Saída

Para cada alternativa, retorna status, justificativa, valor líquido projetado e pontuação (quando elegível). O resultado informa a alternativa selecionada ou a abstenção.

## Limites de segurança

- Nenhuma compra, transferência, contratação, publicação ou compromisso externo é executado.
- Não existe acesso bancário ou a carteiras.
- A decisão não altera orçamento nem permissões.
- Estimativas precisam de fonte e evidência fora deste componente.
- Antes de uso operacional, será necessário integrar uma camada de autorização, trilha de auditoria, validação humana e verificação de resultados reais.
