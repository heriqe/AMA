# ANA — Arquitetura Neural Modular

**Projeto:** AMA — Autonomous Money AI  
**Componente:** ANA — AMA Neural Architecture  
**Documento:** arquitetura-alvo e decisão arquitetural  
**Estado:** proposta arquitetural aprovada para orientar o desenvolvimento  
**Data:** 2026-11-02

## 1. Decisão

A ANA será desenvolvida como uma **arquitetura neural modular**: um sistema central composto por módulos especializados, coordenados por interfaces explícitas e trabalhando sobre representações e estados compatíveis.

A ANA será a base cognitiva compartilhada das futuras IAs do AMA. As IAs funcionárias (CEO, contabilidade, pesquisa, programação e outras) não deverão exigir uma cópia completa e independente da rede neural. Cada uma será criada pela IA Contratante como uma instância especializada que utiliza a ANA e recebe configuração profissional, objetivos, permissões, ferramentas e memória de trabalho próprios.

Esta decisão define a direção arquitetural. Não significa que a ANA já possua inteligência geral, linguagem natural, aprendizagem contínua ou desempenho comprovado.

## 2. Objetivos

1. Construir primeiro a ANA; o desenvolvimento das IAs funcionárias depende de uma base neural validada.
2. Permitir que módulos sejam desenvolvidos, testados e substituídos separadamente.
3. Compartilhar capacidades fundamentais entre especializações profissionais.
4. Evitar duplicação desnecessária de parâmetros e custos de treinamento.
5. Permitir aprendizado controlado, mensurável, reproduzível e reversível.
6. Preservar conhecimentos anteriores e reduzir esquecimento catastrófico.
7. Manter isolamento de memória, permissões e dados entre funcionários.
8. Integrar a ANA ao Cognitive Core do AMA somente por interfaces explícitas e depois de validação.

## 3. Modelo conceitual

A arquitetura é organizada em quatro níveis:

- **Núcleo neural:** unidades, estados, parâmetros e operações matemáticas compartilhadas.
- **Módulos cognitivos:** componentes especializados que transformam e combinam sinais.
- **Coordenação:** define a ordem de execução, roteamento, fusão de resultados e tratamento de falhas.
- **Perfis de especialização:** configurações profissionais usadas pelas futuras IAs funcionárias.

Os módulos não precisam ser redes independentes. Um módulo pode ser um conjunto de operações, uma sub-rede, uma memória especializada ou um mecanismo de avaliação. A decisão sobre quais componentes serão efetivamente neurais ou não neurais deverá ser justificada por experimentos.

## 4. Módulos candidatos

Os módulos abaixo são uma decomposição inicial para pesquisa. Seus limites, dimensões e interfaces ainda precisam ser especificados matematicamente.

| Módulo | Responsabilidade pretendida |
|---|---|
| Percepção e codificação | Converter entradas estruturadas em representações numéricas internas. |
| Estado e integração | Manter e combinar o estado corrente da ANA. |
| Memória temporal | Reter sinais e contexto em diferentes escalas temporais. |
| Raciocínio e relações | Processar relações entre representações e produzir inferências experimentais. |
| Aprendizado | Aplicar regras de atualização treináveis sob um protocolo controlado. |
| Adaptação | Ajustar respostas a mudanças observadas sem ultrapassar limites definidos. |
| Avaliação | Medir erro, estabilidade, retenção e desempenho em tarefas de validação. |
| Decisão e saída | Converter representações internas em saídas estruturadas, sem conceder permissões de execução. |

A coordenação entre módulos deve ser explícita. Não se deve presumir que a simples existência de módulos produz raciocínio ou inteligência.

## 5. Contrato de comunicação entre módulos

Cada módulo deve declarar:

- identificador e versão;
- formato e dimensão das entradas;
- formato e dimensão das saídas;
- estado interno necessário;
- parâmetros treináveis e parâmetros fixos;
- limites numéricos e validações;
- dependências de outros módulos;
- política de inicialização;
- comportamento determinístico esperado;
- métricas e testes de aceitação.

As conexões devem ser tipadas e validadas. Dimensões incompatíveis, valores não finitos, módulos ausentes ou versões incompatíveis devem produzir erros explícitos, nunca resultados silenciosamente inválidos.

A coordenação deverá registrar quais módulos foram executados e quais sinais foram utilizados para produzir cada saída, permitindo rastreabilidade experimental.

## 6. Relação com a linha de versões existente

A arquitetura modular é uma direção de longo prazo e **não substitui nem renomeia retroativamente** as versões matemáticas já definidas.

- **ANA v0.1:** unidade neural isolada, com estado, memória temporal, contexto, modulação e saída.
- **ANA v0.2:** rede de unidades, topologia e propagação síncrona.
- **ANA v0.3:** memória temporal multiescala e contexto.
- **ANA v0.4:** regras iniciais de aprendizado controlado.
- **ANA v0.5:** plasticidade e experimentos de adaptação da conectividade.

A situação de integração de cada versão deve ser verificada no README, roadmap, branches e pull requests do repositório. Este documento não declara nenhuma versão experimental como integrada à `main`.

A arquitetura modular deverá ser construída sobre componentes que tenham sido revisados e integrados, ou em branches de pesquisa explicitamente dependentes deles. Não se deve criar uma segunda implementação incompatível das unidades ou da propagação.

## 7. Estratégia de treinamento

O treinamento da ANA será progressivo. Cada experimento deve declarar hipótese, dados, tarefa, baseline, métrica, sementes, parâmetros treináveis, parâmetros congelados e critério de aprovação.

### 7.1 Aprendizado supervisionado

Usar exemplos com alvos conhecidos para testar se um componente aprende relações específicas. Começar com tarefas pequenas e sintéticas, depois avançar para conjuntos de dados mais variados e devidamente licenciados.

### 7.2 Aprendizado auto-supervisionado

Treinar representações para prever partes ocultas ou valores futuros de entradas estruturadas. Comparar sempre com baselines simples, como persistência, média e modelos lineares.

### 7.3 Aprendizado por recompensa

Introduzir somente depois de existir avaliação confiável. A recompensa deve ser calculada por avaliadores controlados; não deve ser aceita diretamente de um agente que esteja tentando otimizar a própria pontuação. Recompensas não concedem autorização para executar ações externas.

### 7.4 Atualizações seguras

Toda atualização de parâmetros deve ser versionada e feita fora da inferência normal. Exigir avaliação antes/depois, conjunto de regressão, limites de atualização, checkpoint, possibilidade de rollback e registro do conjunto de dados utilizado.

Não atualizar automaticamente a ANA em produção a partir de toda experiência de um funcionário.

## 8. Especialização das futuras IAs funcionárias

Quando a ANA estiver validada, a IA Contratante poderá criar uma instância de funcionário a partir de:

1. uma versão aprovada da ANA;
2. um perfil profissional e seus objetivos;
3. adaptadores ou parâmetros específicos da especialização, quando comprovadamente úteis;
4. uma memória de trabalho isolada;
5. ferramentas e permissões mínimas necessárias;
6. testes de competência adequados à função.

Exemplos de perfis: CEO, contabilidade, pesquisa de oportunidades, programação, marketing e operações.

A especialização não deve copiar nem alterar automaticamente os parâmetros centrais da ANA. Atualizações compartilhadas devem passar por avaliação global para evitar que uma função prejudique as demais.

## 9. Memória e compartilhamento de experiências

Devem existir três escopos distintos:

- **Estado neural compartilhado:** estado transitório necessário ao processamento da ANA.
- **Memória de trabalho do funcionário:** dados e experiências privados daquela instância.
- **Conhecimento aprovado compartilhável:** experiências que passaram por validação, remoção de dados privados quando aplicável e avaliação de utilidade.

Um funcionário não deve escrever diretamente nos parâmetros centrais da ANA. O fluxo recomendado é: registrar experiência → avaliar qualidade e origem → testar em ambiente controlado → aprovar ou rejeitar → criar conjunto de treinamento versionado → treinar em experimento → validar regressões → publicar nova versão se aprovada.

## 10. Segurança, governança e limites

- A ANA não concede permissões de negócio, financeiras ou de sistema.
- Nenhum módulo neural pode alterar suas próprias permissões.
- Saídas neurais são sugestões ou dados; decisões sensíveis exigem validação por regras determinísticas e políticas do AMA.
- A ANA não deve executar pagamentos, publicar conteúdo ou assumir compromissos externos.
- Dados de treinamento devem ter origem, licença e finalidade registradas.
- Dados pessoais e segredos não devem ser usados como exemplos de treinamento sem base legal e controles apropriados.
- Resultados negativos também devem ser preservados no histórico experimental.

## 11. Restrições de infraestrutura

O desenvolvimento deve considerar inicialmente o hardware limitado disponível no ambiente do projeto. Portanto:

- começar com dimensões pequenas e tarefas de baixo custo;
- separar experimentos de treinamento de inferência;
- medir tempo, memória e uso de armazenamento;
- permitir execução de testes unitários sem treinamento pesado;
- evitar assumir que treinamento local de modelos grandes será possível;
- projetar interfaces que permitam mover experimentos para hardware mais forte sem alterar os contratos matemáticos.

A limitação de hardware orienta o tamanho dos experimentos, mas não deve justificar conclusões sobre capacidade cognitiva.

## 12. Critérios de validação da arquitetura

A ANA modular só deverá ser considerada funcional quando houver evidência reproduzível de:

1. contratos e dimensões validados entre módulos;
2. execução determinística quando o protocolo exigir;
3. estabilidade numérica em sequências de teste;
4. ganho mensurável sobre baselines relevantes;
5. generalização em dados não utilizados no treinamento;
6. retenção de capacidades anteriores após atualização;
7. isolamento entre memórias e perfis de funcionários;
8. rastreabilidade de dados, parâmetros e resultados;
9. rollback para uma versão previamente aprovada;
10. testes completos passando na CI.

Não utilizar expressões como "inteligência geral", "compreensão" ou "autonomia cognitiva" como conclusões sem protocolos e evidências adequados.

## 13. Próximas etapas recomendadas

1. Revisar e integrar as versões ANA pendentes na ordem de dependência definida pelos PRs.
2. Consolidar uma especificação de interfaces entre unidade, rede, memória e aprendizado.
3. Criar um protótipo de coordenador modular sem adicionar treinamento complexo.
4. Definir tarefas de benchmark pequenas e reproduzíveis para cada módulo.
5. Comparar arquitetura modular com baselines monolíticos simples.
6. Somente depois ampliar dimensões, tarefas e mecanismos de treinamento.
7. Adiar a criação das IAs funcionárias até que a ANA tenha interfaces estáveis e capacidades demonstradas.

## 14. Decisão final

O AMA adotará a arquitetura modular como direção de desenvolvimento da ANA. A ANA será a base neural compartilhada das futuras IAs, enquanto cada funcionário terá especialização, memória de trabalho, objetivos e permissões próprios.

O foco de desenvolvimento permanece na ANA. A IA CEO, a IA Contratante e os demais funcionários são consumidores futuros dessa base, não prioridades de implementação neste estágio.
