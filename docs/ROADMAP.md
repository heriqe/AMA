# Roadmap do AMA

**Roadmap atualizado — 2026-11-11**

O roadmap é incremental. Datas são referências, não promessas de entrega.

## Foundation v0.1 — concluída

- [x] Estrutura inicial do repositório e empacotamento Python.
- [x] Tipos básicos do núcleo.
- [x] Persistência local SQLite.
- [x] Motor lógico determinístico mínimo.
- [x] Testes automatizados e GitHub Actions.
- [x] Integração na branch `main`.

## Cognitive Core v0.2 — integrada

- [x] Modelo explícito de fatos com origem, confiança e validade temporal opcional.
- [x] Persistência SQLite para conhecimento estruturado.
- [x] Normalização e validação de observações estruturadas.
- [x] Planejamento determinístico com dependências e detecção de ciclos.
- [x] Política explícita para fatos conflitantes, vencidos e de baixa confiança.
- [x] Rastreabilidade estruturada de inferências.
- [x] Pipeline percepção → conhecimento → raciocínio → memória.
- [x] Integração na `main` após revisão e testes.

## Cognitive Core v0.3

- [x] Decisão multicritério com orçamento, risco e incerteza — implementação integrada.
- [ ] Avaliação de resultados e registro de experiências.
- [ ] Execução em sandbox, sem ações externas por padrão.
- [ ] Auditoria e trilha de decisões.
- [ ] Interfaces explícitas de autorização e limites operacionais.

## ANA — linha de pesquisa independente

- [x] ANA v0.1: especificação e protótipo da unidade neural isolada, integrados à `main`.
- [x] ANA v0.2: grafo dirigido recorrente, conexões ponderadas e propagação síncrona, integrados à `main`.
- [x] ANA v0.3: memória temporal multiescala e contexto, integrados à `main` pelo PR #26.

### ANA v0.4 — em revisão na PR #27

- [x] Especificação matemática dos mecanismos supervisionado, por recompensa e descoberta incremental.
- [x] Implementação isolada dos três mecanismos, sem acoplamento automático à rede recorrente ou à memória.
- [x] Testes unitários determinísticos, incluindo baselines sintéticos e limites numéricos.
- [x] GitHub Actions #217: suíte completa aprovada no commit `e4d243c71621fa7664c8681aa23ddf5810f17776`.
- [x] Revisão automatizada Codex concluída sem findings no mesmo commit; não substitui revisão humana.
- [ ] Revisão humana, aprovação explícita e integração à `main`.

### Próximas versões

- [ ] ANA v0.5: plasticidade/conexões dinâmicas, sob limites e testes de estabilidade. Bloqueada até a v0.4 ser aprovada e integrada.
- [ ] ANA 1.0: interface experimental para integração com o Cognitive Core, após validação das etapas anteriores.

## Plataforma AMA

- [ ] Governança técnica e permissões por ação.
- [ ] Organização empresarial e gestão de agentes.
- [ ] Contabilidade gerencial, orçamento e conciliação.
- [ ] Descoberta e avaliação de oportunidades em múltiplas categorias.
- [ ] Integrações externas permitidas e auditáveis.
- [ ] Painel web React, quando o núcleo estiver estável.

## Critérios para avançar

Nenhuma fase é considerada concluída apenas porque os arquivos existem. Exigir testes automatizados, documentação atualizada, limites conhecidos, revisão e evidência reproduzível de funcionamento. A v0.4 permanece proposta até a aprovação humana e integração; o sucesso de CI e a revisão automatizada não autorizam merge.
