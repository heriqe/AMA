# ANA v0.4 — Aprendizado Experimental e Descoberta de Padrões

**Projeto:** AMA — Autonomous Money AI  
**Linha:** ANA — AMA Neural Architecture  
**Versão:** 0.4  
**Estado:** especificação proposta; implementação e validação pendentes  
**Compatibilidade:** Python 3.11+, biblioteca padrão, sem serviço externo ou GPU

## 1. Objetivo

A v0.4 introduz três mecanismos de aprendizado pequenos, explícitos e avaliáveis:

1. **Aprendizado supervisionado:** ajustar um readout linear a partir de pares entrada/alvo.
2. **Aprendizado por recompensa:** ajustar preferências de ações usando recompensa escalar e traço de elegibilidade.
3. **Descoberta de padrões:** agrupar vetores em protótipos incrementais com limite fixo de memória.

Os três mecanismos são experimentos independentes. Não alteram automaticamente os pesos da rede recorrente v0.2, os coeficientes da memória temporal v0.3 ou os parâmetros da unidade v0.1. Uma integração posterior exigirá contrato explícito e avaliação própria.

## 2. Princípios e limites

- Aprendizado é uma operação explícita, separada da inferência.
- Os dados e recompensas são fornecidos pelo chamador; não há coleta externa.
- As transições são determinísticas para os mesmos dados, estado e parâmetros.
- Estados anteriores e parâmetros de entrada são imutáveis.
- Taxas de aprendizado, limites, dimensões e capacidade são configurados e validados.
- Nenhum módulo executa ações, acessa rede, arquivos, relógio ou contas.
- Não há treinamento em background, autoalteração de código ou ampliação de permissões.
- Resultados devem ser comparados a baselines simples e podem ser negativos.

## 3. Aprendizado supervisionado — readout linear

### 3.1 Modelo

Para um vetor de características finitas (x \in \mathbb{R}^{d}), o readout calcula:

\[
\hat y = W x + b
\]

Onde (W \in \mathbb{R}^{q\times d}), (b \in \mathbb{R}^{q}) e (\hat y \in \mathbb{R}^{q}). A primeira versão usa saída linear, sem função de ativação adicional.

### 3.2 Atualização

Para alvo (y\), erro (e=\hat y-y) e taxa (\eta>0\), a atualização por descida do gradiente da perda quadrática média por componente é:

\[
W' = W - \eta\frac{2}{q} e x^T
\]
\[
b' = b - \eta\frac{2}{q}e
\]

O chamador controla a ordem das amostras e o número de épocas. Não há embaralhamento implícito, divisão automática de dados ou parada baseada em acesso externo.

### 3.3 Contratos

- Dimensões de entrada, alvo, pesos e bias são consistentes.
- Taxa de aprendizado é finita e positiva.
- Entradas, alvos, parâmetros e resultados são finitos.
- Um limite configurado de magnitude dos parâmetros impede crescimento numérico sem controle; ultrapassá-lo rejeita a atualização, sem clipping silencioso.
- A inferência não altera parâmetros.

## 4. Aprendizado por recompensa — preferência linear com elegibilidade

### 4.1 Modelo

Para características (x_t \in \mathbb{R}^{d}) e (A\) ações discretas, cada ação recebe escore:

\[
s_t = W x_t, \qquad W \in \mathbb{R}^{A\times d}
\]

A política é determinística nesta versão: seleciona o maior escore, com desempate pelo menor índice. A exploração aleatória não faz parte do núcleo mínimo, garantindo reprodutibilidade.

### 4.2 Elegibilidade e atualização

O estado de elegibilidade é uma matriz (E_t \in \mathbb{R}^{A\times d}), uma linha por ação. Após o chamador informar a ação executada (a_t), o vetor de características e a recompensa (r_t), atualiza-se:

\[
E_t = \lambda E_{t-1}; \qquad
E_t[a_t,:] = E_t[a_t,:] + x_t^T
\]

A baseline escalar móvel é atualizada por:

\[
b_t = b_{t-1} + \beta(r_t-b_{t-1})
\]

A vantagem usa a baseline anterior:

\[
\delta_t = r_t-b_{t-1}
\]

A matriz de pesos é atualizada por:

\[
W' = W + \alpha\delta_t E_t
\]

Assim, as ações escolhidas recentemente acumulam elegibilidade com decaimento; todas as linhas com elegibilidade não nula podem ser atualizadas. O resultado retorna os novos pesos, a nova elegibilidade e a nova baseline. Não há gradiente através do ambiente.

### 4.3 Contratos

- Índice de ação dentro do intervalo ([0,A)).
- Recompensa finita.
- (0\leq\lambda<1), (0<\beta\leq1), (\alpha>0).
- Elegibilidade e pesos possuem dimensões corretas.
- Limite de magnitude de pesos e elegibilidade; overflow ou limite excedido rejeita a transição.
- O módulo não escolhe nem executa ações no ambiente; apenas calcula escores e atualiza parâmetros após feedback explícito.

## 5. Descoberta de padrões — protótipos incrementais limitados

### 5.1 Estado

O estado contém no máximo (K_{max}) protótipos. Cada protótipo armazena centroide (\mu_j\), contagem (n_j\) e identificador sequencial estável. A dimensão (d) é fixa.

### 5.2 Associação

Para uma observação (x\), calcula-se a distância euclidiana ao quadrado para cada centroide:

\[
d_j(x)=\sum_{i=1}^{d}(x_i-\mu_{j,i})^2
\]

Se não houver protótipo ou se a menor distância exceder o limiar configurado (\tau^2\), cria-se um novo protótipo quando houver capacidade. Se a capacidade estiver cheia, associa-se ao mais próximo, sem criar um novo. Empates são resolvidos pelo menor identificador.

### 5.3 Atualização

Para o protótipo escolhido (j\):

\[
n'_j=n_j+1, \qquad
\mu'_j=\mu_j+\frac{x-\mu_j}{n'_j}
\]

O resultado informa o ID associado, a distância e se um protótipo foi criado. A descoberta não atribui significado semântico aos grupos.

### 5.4 Contratos

- Dimensão fixa e vetores finitos.
- (K_{max}\geq1\), parâmetro `squared_distance_threshold` finito e não negativo.
- Contagens inteiras positivas.
- Número de protótipos nunca excede (K_{max}\).
- Atualização determinística e sem mutação do estado anterior.

## 6. Avaliação obrigatória

### 6.1 Supervisionado

- Comparar erro quadrático antes/depois em conjunto sintético determinístico.
- Demonstrar redução de erro em problema linear simples.
- Comparar com baseline constante (média dos alvos).
- Testar dimensão inválida, não finitos, taxa inválida e limite de parâmetros.

### 6.2 Recompensa

- Ambiente sintético determinístico de duas ações, com uma ação consistentemente melhor.
- Comparar recompensa média com baseline uniforme/determinístico sem aprendizado.
- Testar recompensa inválida, ação fora do intervalo, elegibilidade, limites e determinismo.
- Não afirmar convergência geral a partir de um único ambiente.

### 6.3 Padrões

- Dados sintéticos com grupos compactos conhecidos.
- Medir atribuição correta sob limiar previamente definido.
- Comparar com baseline de um único centroide.
- Testar capacidade máxima, empate, dimensões, não finitos e determinismo.

## 7. Arquitetura de software proposta

Manter três módulos independentes, com dataclasses imutáveis para parâmetros, estado e resultado. As funções de atualização recebem explicitamente estado, observação/feedback e parâmetros e retornam novo estado. Não adicionar dependência NumPy nesta versão inicial.

A API pública deve usar nomes distintos para evitar confundir inferência, seleção de ação, treinamento supervisionado e atualização por recompensa. A implementação deve manter os três métodos isolados e não acoplar aprendizado ao `step_network`.

## 8. Critérios de aceitação

1. Os três mecanismos possuem especificação, contratos e API pública independentes.
2. O readout supervisionado reduz erro em um problema linear sintético e é comparado ao baseline constante.
3. O mecanismo por recompensa melhora a recompensa média no ambiente sintético definido e é comparado ao baseline.
4. O descobridor identifica grupos sintéticos sob limiar e capacidade definidos, com baseline documentado.
5. Todos os estados e parâmetros são imutáveis; entradas inválidas são rejeitadas.
6. Testes determinísticos cobrem invariantes, limites e casos extremos.
7. A suíte completa do repositório passa.
8. Documentação declara limites, métricas e resultados reais, inclusive falhas.

## 9. Não objetivos

A v0.4 não implementa backpropagation através da rede recorrente, ajuste automático de todas as matrizes da ANA, aprendizado profundo, otimização de hiperparâmetros, exploração probabilística, memória semântica, linguagem natural, consciência, agentes autônomos ou operação financeira. Não é evidência de inteligência geral.

## 10. Próxima etapa

Após aprovação desta especificação, implementar e validar os três mecanismos em pequenos módulos isolados. Só depois dos testes e baselines poderá ser considerada a ANA v0.4 concluída. A v0.5 permanece bloqueada até aprovação e integração explícita da v0.4.