# ANA v0.2 — Dinâmica e Propagação em Redes

**Projeto:** AMA — Autonomous Money AI  
**Linha:** ANA — AMA Neural Architecture  
**Versão:** 0.2  
**Estado:** especificação e protótipo experimental em revisão

## 1. Objetivo

A ANA v0.1 formalizou uma unidade isolada. A v0.2 define como várias unidades formam um grafo dirigido recorrente e como sinais são propagados entre elas ao longo do tempo.

A rede não é limitada a camadas feed-forward. Ela admite múltiplas entradas, múltiplas saídas, ciclos, recorrência e unidades sem conexões. A topologia e os pesos das conexões são fixos nesta versão.

## 2. Estrutura da rede

Defina uma rede no instante (t):

[
\mathcal{N}(t)=(V,E,\Theta,S(t))
]

Onde:

- (V) é um conjunto finito de unidades identificadas por IDs únicos;
- (E\subseteq V\times V\times\mathbb{R}) é o conjunto de conexões dirigidas e ponderadas;
- (\Theta) associa a cada unidade seus parâmetros locais;
- (S(t)) contém o estado dinâmico de todas as unidades.

Uma conexão (e_{ji}=(j,i,w_{ji})) transmite a saída da unidade (j) para a entrada relacional da unidade (i), com peso escalar (w_{ji}).

### 2.1 Compatibilidade dimensional

Para permitir a soma dos sinais recebidos, todas as unidades de uma rede devem possuir a mesma dimensão relacional (d_r). Nesta versão, a dimensão de saída de cada unidade deve ser igual a (d_r).

As dimensões de entrada externa e estado interno podem variar por unidade. Isso permite unidades especializadas sem alterar a regra de propagação.

## 3. Estado global

O estado da rede é uma associação entre cada ID de unidade e seu estado local:

[
S(t)=\{(i,U_i(t))\mid i\in V\}
]

Cada unidade mantém os componentes definidos na ANA v0.1:

[
U_i(t)=(x_i(t),m_i(t),c_i(t),g_i(t),y_i(t))
]

## 4. Propagação de sinais

A propagação é síncrona. Todos os sinais relacionais do passo (t) são calculados usando exclusivamente as saídas do estado anterior (t-1).

Para cada unidade de destino (i):

[
r_i(t)=\sum_{j:(j,i,w_{ji})\in E}w_{ji}y_j(t-1)
]

Se a unidade não possui conexões de entrada, (r_i(t)=\mathbf{0}).

A soma é vetorial e exige que as saídas de origem tenham dimensão (d_r). Conexões paralelas entre o mesmo par de unidades são proibidas nesta versão para evitar duplicidade acidental.

## 5. Transição global

Cada unidade recebe:
- sua entrada externa (u_i(t)), fornecida pelo ambiente;
- o sinal relacional agregado (r_i(t));
- seu estado anterior (U_i(t-1));
- seus parâmetros locais (\theta_i).

A atualização local é a transição ANA v0.1:

[
U_i(t)=F_{v0.1}(U_i(t-1),u_i(t),r_i(t);\theta_i)
]

A atualização global é:

[
S(t)=\{(i,F_{v0.1}(U_i(t-1),u_i(t),r_i(t);\theta_i))\mid i\in V\}
]

Como toda propagação usa (S(t-1)), ciclos são permitidos sem depender da ordem de iteração das unidades. Um ciclo de comprimento (k) propaga sua influência ao longo de pelo menos (k) passos discretos.

## 6. Ordem e determinismo

- IDs de unidades e conexões são tratados como identificadores, não como prioridade de execução.
- A soma dos sinais de entrada é calculada em ordem determinística.
- Todas as unidades são atualizadas a partir do mesmo snapshot anterior.
- A mesma topologia, parâmetros, estado anterior e entradas externas devem produzir o mesmo próximo estado.
- A transição não modifica a rede, os parâmetros, o estado anterior nem as entradas fornecidas.

## 7. Limites e invariantes

- IDs de unidades devem ser únicos e não vazios.
- Toda conexão deve referenciar unidades existentes.
- Pesos de conexão devem ser números finitos.
- A dimensão de saída de cada unidade deve coincidir com a dimensão relacional comum.
- Cada unidade deve receber exatamente uma entrada externa válida por passo.
- Estados e entradas não finitos ou com dimensões incorretas são rejeitados pela transição local.
- A rede é limitada a 10.000 unidades e 100.000 conexões por instância no protótipo, para impedir alocações acidentais sem limite.
- Não há aprendizagem de pesos, criação/remoção automática de conexões, atenção, roteamento adaptativo ou execução de ações externas.

## 8. Critérios de aceitação

1. Uma rede de uma unidade equivale à transição isolada v0.1 com sinal relacional zero.
2. Uma conexão transmite a saída anterior da origem, multiplicada pelo peso.
3. Uma rede com ciclo atualiza sem depender da ordem dos IDs.
4. Uma rede com várias entradas soma os sinais recebidos.
5. Unidades desconectadas recebem vetor relacional zero.
6. IDs duplicados, conexões inválidas, dimensões incompatíveis e pesos não finitos são rejeitados.
7. A transição global não muta estado nem parâmetros anteriores.

## 9. Não objetivos

A v0.2 não implementa aprendizagem, plasticidade, formação de topologia, otimização, memória global, linguagem natural ou consciência. A topologia fixa é uma escolha experimental para validar primeiro a propagação síncrona.

## 10. Próximas etapas

- **ANA v0.3:** memória/contexto em múltiplas escalas e mecanismos globais explicitamente definidos.
- **ANA v0.4:** aprendizagem supervisionada, por recompensa e descoberta de padrões, com métricas e baselines.
- **ANA v0.5:** conexões dinâmicas, sob limites e testes de estabilidade.
- **ANA 1.0:** integração experimental com o Cognitive Core, mantendo fronteiras entre inferência lógica e processamento neural.

A avaliação deverá incluir redes pequenas com soluções esperadas, análise de estabilidade, sensibilidade a pesos e comparação com baselines simples.
