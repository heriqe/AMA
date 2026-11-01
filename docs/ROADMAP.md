# Roadmap do AMA

**Roadmap atualizado — 2026-11-01**

O roadmap é incremental. Datas são referências, não promessas de entrega.

## Foundation v0.1 — concluída

- [x] Estrutura inicial do repositório e empacotamento Python.
- [x] Tipos básicos do núcleo.
- [x] Persistência local SQLite.
- [x] Motor lógico determinístico mínimo.
- [x] Testes automatizados e GitHub Actions.
- [x] Integração na branch `main`; workflow da branch principal concluído com sucesso.

## Cognitive Core v0.2 — em desenvolvimento

- [x] Modelo explícito de fatos com origem, confiança e validade temporal opcional.
- [x] Persistência SQLite para conhecimento estruturado.
- [x] Normalização e validação de observações estruturadas.
- [x] Planejamento determinístico com dependências e detecção de ciclos.
- [ ] Raciocínio com rastreabilidade estruturada das inferências.
- [ ] Política explícita para fatos conflitantes, vencidos e de baixa confiança.
- [ ] Integração entre percepção, conhecimento, memória e raciocínio.
- [ ] Validar todos os testes na CI antes de integrar.

## Cognitive Core v0.3

- [ ] Decisão multicritério com orçamento, risco e incerteza.
- [ ] Avaliação de resultados e registro de experiências.
- [ ] Execução em sandbox, sem ações externas por padrão.
- [ ] Auditoria e trilha de decisões.

## ANA — linha de pesquisa independente

- [ ] ANA v0.1: especificação matemática da unidade neural.
- [ ] ANA v0.2: dinâmica e propagação.
- [ ] ANA v0.3: memória e contexto.
- [ ] ANA v0.4: mecanismos de aprendizado e adaptação.
- [ ] ANA v0.5: redes maiores e conexões dinâmicas.
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
