# AMA — Autonomous Money AI

O **AMA** é um projeto experimental para construir uma plataforma própria de inteligência cognitiva e gestão de oportunidades legítimas de geração de renda.

A meta é desenvolver, em etapas verificáveis, um núcleo cognitivo independente de serviços externos de IA e, em uma linha de pesquisa separada, a **ANA (AMA Neural Architecture)**. A integração entre os dois só ocorrerá quando houver componentes testados e interfaces definidas.

> **Estado atual:** Foundation v0.1 integrada à `main`; complementos do Cognitive Core v0.2 estão em revisão no PR #3; a ANA v0.1 está em revisão no PR #4 e a ANA v0.2 está em revisão no PR #5; o mecanismo de decisão do Cognitive Core v0.3 está em revisão no PR #6. O AMA ainda não é um sistema autônomo de geração de renda e não deve ser usado para movimentar dinheiro, publicar conteúdo ou assumir compromissos externos.

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
│   ├── decisions/
│   └── ana/
├── src/ama/
│   ├── ana/            # unidade neural e rede experimental
│   ├── core/           # contratos e pipeline cognitivo
│   ├── decision/       # avaliação determinística de alternativas
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
| Cognitive Core v0.2 — fatos, política, inferências e pipeline | Em revisão no PR #3 |
| ANA v0.1 — unidade matemática e protótipo | Em revisão no PR #4 |
| ANA v0.2 — rede recorrente e propagação síncrona | Em revisão no PR #5 |
| Cognitive Core v0.3 — decisão sob orçamento e risco | Em revisão no PR #6 |
| Linguagem natural livre | Não implementada |
| Aprendizado cognitivo/neural | Pesquisa futura |
| Organização empresarial e agentes | Futuro |
| Operação de negócios e integrações | Futuro, sujeita à governança |

## Limites atuais

O Cognitive Core manipula observações estruturadas e regras determinísticas; não interpreta linguagem natural livre. O mecanismo de decisão v0.3 apenas compara estimativas fornecidas, com restrições explícitas, e não executa ações. A ANA v0.1/v0.2 é uma implementação experimental de unidade e propagação numérica; não implementa aprendizado ou linguagem natural. Nenhum desses componentes opera negócios ou movimenta dinheiro.

Consulte [docs/ROADMAP.md](docs/ROADMAP.md) para a sequência de desenvolvimento.
