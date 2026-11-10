# Roadmap do AMA

**Roadmap atualizado — 2026-11-10**

O roadmap é incremental. Datas são referências, não promessas de entrega. Uma capacidade só é considerada integrada após revisão, testes e merge aprovado na `main`.

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

## Cognitive Core v0.3 — parcial

- [x] Decisão multicritério com orçamento, risco e incerteza — implementação integrada.
- [ ] Avaliação de resultados e registro de experiências.
- [ ] Execução em sandbox, sem ações externas por padrão.
- [ ] Auditoria e trilha de decisões.
- [ ] Interfaces explícitas de autorização e limites operacionais.

## ANA — linha de pesquisa independente

- [x] ANA v0.1: especificação matemática da unidade neural.
- [x] ANA v0.1: protótipo de transição de uma unidade isolada.
- [x] ANA v0.1 integrada à `main`.
- [x] ANA v0.2: grafo dirigido recorrente, conexões ponderadas e propagação síncrona.
- [x] ANA v0.2 integrada à `main` pelo PR #7.
- [ ] ANA v0.3: memória/contexto em múltiplas escalas — próxima etapa da sequência.
- [ ] ANA v0.4 e versões seguintes: desenvolver e validar estritamente conforme suas especificações e dependências aprovadas.
- [ ] ANA 1.0: interface experimental para integração com o Cognitive Core, somente após critérios de estabilidade e validação.

### Regra de integração da ANA

O desenvolvimento das versões v0.3 até v0.8 deve ocorrer sequencialmente, uma versão por vez, na branch operacional designada. Cada versão precisa de auditoria, testes e proposta de PR. A branch `main` permanece protegida: nenhuma integração automática é permitida e todo merge exige aprovação humana explícita. Não integrar uma versão posterior enquanto a anterior não estiver validada e aprovada.

## Plataforma AMA

- [ ] Governança técnica e permissões por ação.
- [ ] Organização empresarial e gestão de agentes.
- [ ] Contabilidade gerencial, orçamento e conciliação.
- [ ] Descoberta e avaliação de oportunidades em múltiplas categorias.
- [ ] Integrações externas permitidas e auditáveis.
- [ ] Painel web React, quando o núcleo estiver estável.

## Política de versionamento do pacote

A versão declarada em `pyproject.toml` identifica a distribuição Python do projeto, não substitui as versões internas de Foundation, Cognitive Core ou ANA. A versão do pacote deve ser atualizada somente quando houver uma política de release definida e uma mudança de distribuição correspondente; não inferir a versão do pacote a partir da versão de um componente.

## Critérios para avançar

Nenhuma fase é considerada concluída apenas porque os arquivos existem. Exigir testes automatizados, documentação atualizada, limites conhecidos e evidência reproduzível de funcionamento. A CI deve executar nos pushes das branches de desenvolvimento relevantes e nos pull requests direcionados à `main`.
