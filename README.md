# AMA — Autonomous Money AI

O **AMA** é um projeto experimental para construir uma plataforma própria de inteligência cognitiva e gestão de oportunidades legítimas de geração de renda.

A meta é desenvolver, em etapas verificáveis, um núcleo cognitivo independente de serviços externos de IA e, em uma linha de pesquisa separada, a **ANA (AMA Neural Architecture)**. A integração entre os dois só ocorrerá quando houver componentes testados e interfaces definidas.

> **Estado atual:** Foundation v0.1 e Cognitive Core v0.2 integrados à `main`. A ANA v0.1 (unidade neural isolada) está em revisão no PR #4. A ANA v0.2, que tratará da dinâmica entre unidades, permanece em uma etapa separada e não faz parte deste PR. O AMA ainda não é um sistema autônomo de geração de renda e não deve ser usado para movimentar dinheiro, publicar conteúdo ou assumir compromissos externos.

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
│   ├── ana/            # unidade neural experimental (v0.1)
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
| ANA v0.1 — especificação matemática e unidade isolada | Em revisão no PR #4 |
| ANA v0.2 — dinâmica e propagação entre unidades | Próxima etapa; fora do PR #4 |
| Linguagem natural livre | Não implementada |
| Aprendizado cognitivo/neural | Pesquisa futura |
| Organização empresarial e agentes | Futuro |
| Operação de negócios e integrações | Futuro, sujeita à governança |

## Limites atuais

O Cognitive Core manipula observações estruturadas e regras determinísticas; não interpreta linguagem natural livre. A ANA v0.1 implementa uma transição numérica para uma unidade isolada; não implementa redes, propagação entre unidades, treinamento ou aprendizado. Nenhum desses componentes executa negócios ou ações externas.

Consulte [docs/ROADMAP.md](docs/ROADMAP.md) para a sequência de desenvolvimento.
