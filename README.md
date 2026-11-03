# AMA — Autonomous Money AI

O **AMA** é um projeto experimental para construir uma plataforma própria de inteligência cognitiva e gestão de oportunidades legítimas de geração de renda.

A meta é desenvolver, em etapas verificáveis, um núcleo cognitivo independente de serviços externos de IA e, em uma linha de pesquisa separada, a **ANA (AMA Neural Architecture)**. A integração entre os dois só ocorrerá quando houver componentes testados e interfaces definidas.

> **Estado atual:** Foundation v0.1, Cognitive Core v0.2 e ANA v0.1 estão integrados à `main`. ANA v0.2 está em revisão no PR #7; ANA v0.3 depende do PR #7 e está em revisão no PR #8; ANA v0.4 depende do PR #8 e está em revisão no PR #9; ANA v0.5 depende do PR #9 e está em desenvolvimento no PR #10. O AMA ainda não é um sistema autônomo de geração de renda e não deve ser usado para movimentar dinheiro, publicar conteúdo ou assumir compromissos externos.

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
│   ├── ana/            # unidade, rede, memória temporal e aprendizado experimental
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
| ANA v0.1 — unidade neural isolada | Integrada |
| ANA v0.2 — grafo recorrente e propagação síncrona | Em revisão no PR #7 |
| ANA v0.3 — memória temporal multiescala | Em revisão no PR #8 (dependente do #7) |
| ANA v0.4 — aprendizado limitado | Em revisão no PR #9 (dependente do #8) |
| ANA v0.5 — plasticidade dinâmica limitada | Em revisão no PR #10 (dependente do #9) |
| Linguagem natural livre | Não implementada |
| Aprendizado cognitivo/neural | Protótipo ANA v0.4 em revisão |
| Organização empresarial e agentes | Futuro |
| Operação de negócios e integrações | Futuro, sujeita à governança |

## Limites atuais

O Cognitive Core manipula observações estruturadas e regras determinísticas; não interpreta linguagem natural livre. A ANA v0.1 implementa uma transição numérica para uma unidade isolada. A ANA v0.2 conecta unidades em um grafo dirigido e propaga sinais sincronamente usando o estado anterior; a topologia e os pesos permanecem fixos. A ANA v0.3 mantém traços temporais em diferentes escalas e produz contexto agregado, ainda sem integração automática à rede. A ANA v0.4 adiciona regras experimentais de ajuste supervisionado, por recompensa e previsão auto-supervisionada em um vetor de pesos de saída escalar; ainda não treina a rede recorrente inteira. A ANA v0.5 pesquisa plasticidade limitada em um conjunto explícito de conexões candidatas, com fortalecimento, ativação e poda controlados; não cria unidades nem pares arbitrários. Nenhum desses componentes executa negócios ou ações externas.

Consulte [docs/ROADMAP.md](docs/ROADMAP.md) para a sequência de desenvolvimento.
