# AMA — Autonomous Money AI

O **AMA** é um projeto experimental para construir uma plataforma própria de inteligência cognitiva e gestão de oportunidades legítimas de geração de renda.

A meta é desenvolver, em etapas verificáveis, um núcleo cognitivo independente de serviços externos de IA e, em uma linha de pesquisa separada, a **ANA (AMA Neural Architecture)**. A integração entre os dois só ocorrerá quando houver componentes testados e interfaces definidas.

> **Estado atual:** Foundation v0.1 e base do Cognitive Core v0.2 integradas à `main`; complementos do Cognitive Core estão em revisão no PR #3. A especificação e o primeiro protótipo isolado da ANA v0.1 estão em desenvolvimento no PR #4. O AMA ainda não é um sistema autônomo de geração de renda e não deve ser usado para movimentar dinheiro, publicar conteúdo ou assumir compromissos externos.

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
│   ├── ana/            # especificações da ANA
│   └── decisions/
├── src/ama/
│   ├── ana/            # protótipos da unidade neural
│   ├── core/           # contratos compartilhados
│   ├── knowledge/      # fatos, origem, confiança e SQLite
│   ├── memory/         # registros persistentes
│   ├── perception/     # validação de entradas estruturadas
│   ├── planning/       # planos e dependências de tarefas
│   └── reasoning/      # regras determinísticas
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
| Fundação e empacotamento Python | Implementado |
| Tipos básicos de entrada e resultado | Implementado |
| Memória SQLite simples | Implementado |
| Motor lógico determinístico mínimo | Implementado |
| Fatos estruturados com origem e confiança | Base implementada |
| Política de validade e conflito de fatos | Em revisão no PR #3 |
| Rastreabilidade de inferências e pipeline cognitivo | Em revisão no PR #3 |
| ANA v0.1: especificação matemática da unidade | Em revisão no PR #4 |
| ANA v0.1: protótipo isolado e testes | Em revisão no PR #4 |
| Linguagem natural livre | Não implementada |
| Aprendizado cognitivo/neural | Pesquisa futura |
| Organização empresarial e agentes | Futuro |
| Operação de negócios e integrações | Futuro, sujeita à governança |

## Limites atuais

O Cognitive Core atual manipula observações estruturadas e regras determinísticas; não interpreta linguagem natural livre. A ANA v0.1 é um protótipo matemático isolado, não uma rede neural completa nem um sistema de aprendizado. Nenhum desses componentes executa negócios ou ações externas.

Consulte [docs/ROADMAP.md](docs/ROADMAP.md) para a sequência de desenvolvimento.
