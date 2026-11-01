# Roadmap do AMA

**Roadmap atualizado — 2026-11-01**

O roadmap é incremental. Datas são referências, não promessas de entrega.

## Foundation v0.1 — concluída

- [x] Estrutura inicial do repositório e empacotamento Python.
- [x] Tipos básicos do núcleo.
- [x] Persistência local SQLite.
- [x] Motor lógico determinístico mínimo.
- [x] Testes automatizados e GitHub Actions.
- [x] Integração na branch `main`.

## Cognitive Core v0.2 — base integrada; complementos em revisão no PR #3

- [x] Modelo explícito de fatos com origem, confiança e validade temporal opcional.
- [x] Persistência SQLite para conhecimento estruturado.
- [x] Normalização e validação de observações estruturadas.
- [x] Planejamento determinístico com dependências e detecção de ciclos.
- [x] Política explícita para fatos conflitantes, vencidos e de baixa confiança.
- [x] Rastreabilidade estruturada de inferências.
- [x] Pipeline percepção → conhecimento → raciocínio → memória.
- [ ] Revisão e integração dos complementos na `main`.

## Cognitive Core v0.3 — decisão inicial em revisão no PR #6

- [x] Modelo de orçamento com moeda explícita.
- [x] Alternativas com receita projetada, custo estimado, risco e confiança de evidência.
- [x] Restrições duras para orçamento, moeda, risco, evidência e aprovação humana.
- [x] Pontuação normalizada e desempate determinístico.
- [x] Abstenção quando nenhuma alternativa é elegível.
- [ ] Avaliação de resultados reais e registro de experiências.
- [ ] Sandbox e execução autorizada.
- [ ] Auditoria persistente de decisões e limites operacionais.

## ANA — linha de pesquisa independente

- [x] ANA v0.1: unidade neural matemática e protótipo isolado (PR #4).
- [x] ANA v0.2: grafo dirigido recorrente e propagação síncrona (PR #5).
- [ ] Revisão e integração das etapas v0.1/v0.2.
- [ ] ANA v0.3: memória/contexto em múltiplas escalas.
- [ ] ANA v0.4: aprendizado supervisionado, por recompensa e descoberta de padrões.
- [ ] ANA v0.5: redes maiores e conexões dinâmicas com testes de estabilidade.
- [ ] ANA 1.0: interface experimental para integração com o Cognitive Core.

## Plataforma AMA

- [ ] Governança técnica e permissões por ação.
- [ ] Organização empresarial e gestão de agentes.
- [ ] Contabilidade gerencial, orçamento e conciliação.
- [ ] Descoberta e avaliação de oportunidades em múltiplas categorias.
- [ ] Integrações externas permitidas e auditáveis.
- [ ] Painel web React, quando o núcleo estiver estável.

## Critérios para avançar

Nenhuma fase é considerada concluída apenas porque os arquivos existem. Exigir testes automatizados, documentação atualizada, limites conhecidos e evidência reproduzível de funcionamento.
