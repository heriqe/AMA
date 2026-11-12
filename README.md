# AMA — Autonomous Money AI

O **AMA** é um projeto experimental para construir uma plataforma própria de inteligência cognitiva e gestão de oportunidades legítimas de geração de renda.

A meta é desenvolver, em etapas verificáveis, um núcleo cognitivo independente de serviços externos de IA e, em uma linha de pesquisa separada, a **ANA (AMA Neural Architecture)**. A integração entre os dois só ocorrerá quando houver componentes testados e interfaces definidas.

> **Estado atual:** Foundation v0.1, Cognitive Core v0.2 e ANA v0.1–v0.3 estão integrados à `main`. A ANA v0.4 está proposta na [PR #27](https://github.com/heriqe/AMA/pull/27), com mecanismos experimentais isolados, testes e documentação; permanece aguardando revisão e aprovação humana, sem integração. O Cognitive Core v0.3 (decisão multicritério) ainda não está implementado. O AMA ainda não é um sistema autônomo de geração de renda e não deve ser usado para movimentar dinheiro, publicar conteúdo ou assumir compromissos externos.

## Princípios

- **Inteligência própria:** o funcionamento central não depende de APIs ou modelos de IA externos.
- **Evolução incremental:** cada capacidade deve ter especificação, testes, métricas e histórico de versões.
- **Autonomia governada:** permissões são explícitas; o sistema não pode ampliar as próprias permissões.
- **Segurança financeira:** valores simulados nunca são apresentados como dinheiro real. Pagamentos, transferências e compromissos legais exigem aprovação humana.
- **Escopo amplo:** investigar oportunidades em diferentes categorias, sempre validando legalidade, regras das plataformas, custos e viabilidade no Brasil.
- **Transparência:** decisões, execuções e resultados precisam ser auditáveis.

## Estrutura atual

```text
AMA/
├── .github/workflows/tests.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── GOVERNANCE.md
│   ├── ROADMAP.md
│   └── ana/            # especificações e arquitetura modular da ANA
├── src/ama/
│   ├── ana/            # unidade v0.1, rede v0.2, memória v0.3 e módulos v0.4 em revisão
│   ├── core/           # contratos e pipeline cognitivo
│   ├── knowledge/      # fatos, política de validade/conflito e SQLite
│   ├── memory/         # registros persistentes
│   ├── perception/     # validação de entradas estruturadas
│   ├── planning/       # planos e dependências de tarefas
│   └── reasoning/      # regras e rastreabilidade de inferências
├── tests/
└── pyproject.toml
```

## Requisitos

- Python 3.11 ou superior
- SQLite (incluído na biblioteca padrão do Python)

## Instalação para desenvolvimento

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

## Situação das capacidades

| Componente | Estado |
|---|---|
| Fundação e empacotamento Python | Integrado |
| Cognitive Core v0.2 — fatos, política, inferências e pipeline | Integrado |
| Cognitive Core v0.3 — decisão multicritério | Não implementado; o planejador ordena dependências e regras de orçamento funcionam como gates, não como classificação de alternativas |
| ANA v0.1 — unidade neural isolada | Integrada |
| ANA v0.2 — grafo recorrente e propagação síncrona | Integrada |
| ANA v0.3 — memória temporal multiescala | Integrada |
| ANA v0.4 — readout supervisionado, recompensa e protótipos | Em revisão na PR #27; não integrada |
| Linguagem natural livre | Não implementada |
| Aprendizado neural integrado à rede recorrente | Não implementado; v0.4 contém mecanismos isolados em revisão |
| Organização empresarial e agentes | Futuro |
| Operação de negócios e integrações | Futuro, sujeita à governança |

## Limites atuais

O Cognitive Core manipula observações estruturadas e regras determinísticas; não interpreta linguagem natural livre. Seu planejador atual ordena tarefas por dependências e as regras de orçamento funcionam como condições de autorização, não como decisão multicritério entre alternativas. Na `main`, a ANA v0.1 implementa uma unidade isolada, a v0.2 propaga sinais em uma rede recorrente com topologia e pesos fixos, e a v0.3 mantém traços temporais multiescala. A PR #27 propõe readout supervisionado, atualização por recompensa e descoberta incremental de protótipos, mas esses mecanismos ainda são experimentais, não estão integrados à rede recorrente e aguardam revisão/aprovação. Nenhuma dessas versões executa negócios ou ações externas, nem demonstra inteligência geral.

Consulte [docs/ROADMAP.md](docs/ROADMAP.md) para a sequência de desenvolvimento.
