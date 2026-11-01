# ANA v0.1 — Especificação Matemática da Unidade Neural

**Projeto:** AMA — Autonomous Money AI  
**Linha:** ANA — AMA Neural Architecture  
**Versão:** 0.1  
**Estado:** especificação inicial e protótipo matemático isolado

## 1. Objetivo e escopo

A ANA é uma arquitetura neural experimental própria. A v0.1 define uma unidade neural como um sistema dinâmico com estado, memória temporal, contexto, modulação e saída. Ela não é apenas uma função de ativação aplicada a uma soma ponderada.

Esta versão especifica e implementa somente a transição de **uma unidade isolada**. Não define rede, topologia, propagação entre várias unidades, treinamento, otimização de parâmetros ou aprendizagem autônoma. Esses temas pertencem às versões seguintes.

A arquitetura é uma hipótese de pesquisa: as equações precisam ser avaliadas empiricamente. A especificação não afirma superioridade nem equivalência a arquiteturas existentes.

## 2. Convenções

- (t\in\mathbb{N}) representa um passo discreto.
- Vetores são colunas; matrizes são aplicadas pela esquerda.
- (\odot) é o produto elemento a elemento.
- (\tanh) é aplicada elemento a elemento.
- (\mathbf{1}) é o vetor unitário de dimensão interna.
- Todos os valores numéricos devem ser finitos.
- Os parâmetros são fixos durante a transição v0.1.

Dimensões:

| Símbolo | Significado | Dimensão |
|---|---|---:|
| (u_t) | entrada externa | (d_u) |
| (r_t) | sinal relacional recebido | (d_r) |
| (x_t) | estado instantâneo | (d) |
| (m_t) | memória temporal persistente | (d) |
| (c_t) | contexto interno | (d) |
| (g_t) | modulação interna | (d) |
| (y_t) | saída | (d_y) |

Na v0.1, os quatro estados internos usam a mesma dimensão (d) para simplificar a implementação e os testes. Isso é uma restrição inicial, não uma exigência para versões futuras.

## 3. Definição formal da unidade

A unidade no instante (t) é:

[
U(t)=(x_t,m_t,c_t,g_t,y_t)
]

O conjunto de parâmetros é:

[
\Theta=\{W_{xx},W_{xm},W_{xc},W_{xu},W_{xr},b_x,
W_{cc},W_{cx},W_{cr},b_c,
W_{gx},W_{gc},W_{gm},b_g,
W_{mx},W_{mc},W_{mu},b_m,
W_{yx},W_{ym},W_{yc},b_y,\rho,\eta,\gamma\}
]

Os parâmetros permanecem constantes durante uma chamada de transição. A ANA v0.1 não os treina.

## 4. Equações de transição

A transição usa o estado anterior e as entradas atuais. A ordem abaixo é parte da definição, pois evita dependências circulares dentro do mesmo passo.

### 4.1 Estado instantâneo

Primeiro, calcula-se a combinação de sinais:

[
p^x_t=W_{xx}x_{t-1}+W_{xm}m_{t-1}+W_{xc}c_{t-1}
+W_{xu}u_t+W_{xr}r_t+b_x
]

A modulação anterior atua sobre o novo estado:

[
x_t=\tanh(g_{t-1}\odot p^x_t)
]

Assim, a unidade carrega influência temporal da modulação sem calcular (g_t) antes de (x_t).

### 4.2 Contexto

O contexto combina o contexto anterior, o novo estado e o sinal relacional atual:

[
c_t=\tanh(W_{cc}c_{t-1}+W_{cx}x_t+W_{cr}r_t+b_c)
]

O contexto é uma representação interna atualizada a cada passo. Na v0.1, não há mecanismo de atenção ou seleção dinâmica de unidades.

### 4.3 Modulação

A modulação é recalculada depois do estado e do contexto:

[
g_t=\mathbf{1}+\gamma\tanh(W_{gx}x_t+W_{gc}c_t+W_{gm}m_{t-1}+b_g)
]

Com (0\leq\gamma\leq1), cada componente de (g_t) fica no intervalo ([1-\gamma,1+\gamma]), portanto em ([0,2]). A modulação altera a intensidade de sinais internos; não representa uma decisão ou autorização.

### 4.4 Memória temporal

Calcula-se um candidato de conteúdo:

[
q^m_t=\tanh(W_{mx}x_t+W_{mc}c_t+W_{mu}u_t+b_m)
]

A memória é atualizada por retenção e incorporação modulada:

[
m_t=\rho m_{t-1}+\eta(g_t\odot q^m_t)
]

Restrições iniciais: (0\leq\rho<1) e (\eta\geq0). (\rho) controla retenção; (\eta) controla a intensidade de incorporação. Como (q^m_t\in[-1,1]^d) e (g_t\in[0,2]^d), a memória permanece limitada para parâmetros válidos e estado inicial finito, com limite conservador por componente de ( |m|\leq |m_0|+2\eta/(1-\rho)).

### 4.5 Saída

Por último, a unidade produz a saída observável:

[
y_t=\tanh(W_{yx}x_t+W_{ym}m_t+W_{yc}c_t+b_y)
]

A saída depende do estado, da memória atualizada e do contexto atual.

## 5. Inicialização

A inicialização de referência usa:

[
x_0=m_0=c_0=y_0=\mathbf{0},\qquad g_0=\mathbf{1}
]

Pesos zero são usados somente em testes de infraestrutura. Uma inicialização útil para experimentos precisará ser definida e avaliada separadamente.

## 6. Restrições de integridade

- Dimensões de matrizes e vetores devem coincidir com as dimensões declaradas.
- Entradas, estados e parâmetros devem conter somente números finitos.
- (\rho\), (\eta\) e (\gamma\) devem obedecer aos intervalos definidos.
- Uma transição é uma função pura: não altera o estado anterior nem os parâmetros.
- A unidade não executa ações externas, não acessa rede, arquivos ou relógio.
- Nenhum parâmetro é atualizado durante a inferência da unidade.
- Uma implementação futura de aprendizado deverá ser separada da transição e possuir testes, versões e rollback.

## 7. O que esta versão não afirma

A ANA v0.1 não é uma rede neural completa, não aprende automaticamente e não possui linguagem natural, consciência ou compreensão humana. A unidade apenas transforma sinais numéricos estruturados segundo as equações especificadas.

## 8. Critérios de aceitação

1. As dimensões são verificadas antes da transição.
2. Valores não finitos e parâmetros fora dos limites são rejeitados.
3. A mesma entrada, estado e parâmetros produzem a mesma saída.
4. O estado anterior permanece inalterado.
5. A memória respeita a equação de retenção e incorporação.
6. Os testes cobrem entrada, relação, memória, contexto, modulação e saída.

## 9. Próximas versões

- **ANA v0.2:** dinâmica entre unidades, propagação e conexões.
- **ANA v0.3:** memória e contexto em múltiplas escalas, além da memória local da unidade.
- **ANA v0.4:** mecanismos de aprendizado supervisionado, por recompensa e descoberta de padrões.
- **ANA v0.5:** redes maiores e conexões dinâmicas.
- **ANA 1.0:** interface experimental e testada para integração com o Cognitive Core.

Cada versão deve comparar hipóteses com baselines simples e publicar resultados reproduzíveis, inclusive resultados negativos.
