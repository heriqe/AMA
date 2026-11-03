# ANA v0.5 — Plasticidade e Conexões Dinâmicas Controladas

**Projeto:** AMA — Autonomous Money AI  
**Linha:** ANA — AMA Neural Architecture  
**Versão:** 0.5  
**Estado:** protótipo experimental

## 1. Objetivo

A v0.5 investiga adaptação da conectividade sem alterar livremente a arquitetura. A rede recebe um conjunto explícito e finito de conexões candidatas. O mecanismo pode fortalecer/enfraquecer conexões ativas, ativar candidatas após coativação persistente e remover conexões persistentemente fracas.

## 2. Estado estrutural

Cada conexão candidata dirigida mantém origem, destino, peso escalar, estado ativo/inativo, contador consecutivo de coativação e contador consecutivo de fraqueza. O conjunto de pares candidatos é fixado na inicialização. A v0.5 não cria pares arbitrários nem adiciona unidades.

## 3. Plasticidade de peso

Para uma conexão ativa i → j, com atividades a_i e a_j:

w_ij(t+1) = clip_W(w_ij(t) + eta * a_i(t) * a_j(t) - rho * w_ij(t))

O termo de coativação é Hebbiano. O decaimento limita persistência de pesos sem suporte. A regra é uma hipótese experimental simples; não é evidência de aprendizado útil por si só.

## 4. Formação de conexão

Para conexão inativa, coativação ocorre quando |a_i| e |a_j| atingem o limiar. O contador aumenta em passos consecutivos e zera quando a condição falha. A conexão é ativada após K passos consecutivos de coativação, recebendo um peso inicial pequeno e limitado.

## 5. Remoção de conexão

Para conexão ativa, se |w_ij| permanecer abaixo do limiar de poda por P passos consecutivos, ela é desativada e seu peso é zerado. Se o peso superar o limiar, o contador é zerado. A histerese temporal evita decisões estruturais com base em um único passo.

## 6. Limites e determinismo

- Conjunto candidato explícito, fixo e finito.
- IDs e pares únicos; auto-conexões não são aceitas nesta versão.
- Atividades e pesos devem ser finitos e respeitar limites.
- Peso é limitado a [-W, W].
- Ativação e poda usam contadores inteiros e limiares configuráveis.
- Estado imutável e ordem de saída estável.
- Nenhuma mutação da definição de rede ocorre implicitamente.

Os limites evitam crescimento ilimitado de pesos por passo, mas não provam estabilidade global, convergência ou benefício cognitivo. A escolha de limiares exige avaliação empírica.

## 7. Interface com a rede

`PlasticityState.active_connections()` converte conexões ativas para os objetos de conexão usados pela rede v0.2. O chamador deve construir uma nova definição de rede explicitamente. A plasticidade não altera a rede em execução por efeitos colaterais.

## 8. Não objetivos

A v0.5 não cria unidades, não aprende quais candidatos devem existir, não modifica parâmetros internos das unidades, não treina a rede recorrente ponta a ponta, não implementa backpropagation, atenção, linguagem natural ou aprendizado semântico geral.

## 9. Critérios de aceitação

1. Pesos ativos aumentam/diminuem conforme coativação e decaimento.
2. Pesos respeitam limites absolutos.
3. Candidatas só ativam após coativação consecutiva suficiente.
4. Uma quebra de coativação zera o contador.
5. Conexões fracas só são removidas após persistência configurada.
6. O estado anterior permanece imutável.
7. Mesmas entradas produzem mesmo estado.
8. Candidatas, IDs e atividades inválidas são rejeitadas.
9. Conexões ativas podem ser convertidas para a API de rede.

## 10. Avaliação experimental necessária

Comparar, em sequências sintéticas reproduzíveis: topologia fixa sem plasticidade; plasticidade apenas de peso; plasticidade com ativação e poda; sensibilidade a ruído, limiares e taxas; estabilidade dos pesos, densidade da rede e erro preditivo em tarefa definida. Nenhuma alegação de melhoria deve ser feita sem baselines e métricas.

## 11. Próximas etapas

ANA 1.0 deverá avaliar integração entre unidade, rede, memória temporal, aprendizado e plasticidade por interfaces explícitas e versionadas.