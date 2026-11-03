# Roadmap do AMA

**Roadmap atualizado — 2026-11-02**

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

- [x] ANA v0.1: especificação matemática da unidade neural.
- [x] ANA v0.1: protótipo de transição de uma unidade isolada.
- [x] ANA v0.1 integrada à `main`.
- [ ] ANA v0.2: grafo dirigido recorrente, conexões ponderadas e propagação síncrona (PR #7 em revisão).
- [ ] ANA v0.3: memória temporal multiescala e contexto agregado (PR #8 dependente do #7).
- [ ] ANA v0.4: regras de aprendizado supervisionado, por recompensa e previsão auto-supervisionada (PR #9 dependente do #8).
- [ ] ANA v0.5: estudar plasticidade e conexões dinâmicas, com experimentos comparativos e limites.
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
