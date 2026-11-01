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

- [ ] Decisão multicritério com orçamento, risco e incerteza.
- [ ] Avaliação de resultados e registro de experiências.
- [ ] Execução em sandbox, sem ações externas por padrão.
- [ ] Auditoria e trilha de decisões.
- [ ] Interfaces explícitas de autorização e limites operacionais.

## ANA — linha de pesquisa independente

- [x] ANA v0.1: especificação matemática da unidade neural.
- [x] ANA v0.1: protótipo de transição de uma unidade isolada.
- [ ] Revisão e integração da ANA v0.1 na `main` (PR #4).
- [ ] ANA v0.2: dinâmica entre unidades, conexões e propagação síncrona.
- [ ] ANA v0.3: memória/contexto em múltiplas escalas.
- [ ] ANA v0.4: aprendizado supervisionado, por recompensa e descoberta de padrões.
- [ ] ANA v0.5: redes maiores e conexões dinâmicas, com testes de estabilidade.
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
