# AMA — Autonomous Money AI

O **AMA** é um projeto experimental para construir uma plataforma própria de inteligência cognitiva e gestão de oportunidades legítimas de geração de renda.

A meta é desenvolver, em etapas verificáveis, um núcleo cognitivo independente de serviços externos de IA e, em uma linha de pesquisa separada, a **ANA (AMA Neural Architecture)**. A integração entre os dois só ocorrerá quando houver componentes testados e interfaces definidas.

> **Estado atual:** Foundation v0.1, Cognitive Core v0.2 e ANA v0.1 estão integrados à `main`. ANA v0.2 está em revisão no PR #7; ANA v0.3 depende do PR #7 e está em revisão no PR #8; ANA v0.4 depende do PR #8 e está em revisão no PR #9; ANA v0.5 depende do PR #9 e está em revisão no PR #10; o benchmark sintético está em revisão no PR #11, dependente do #10; a extensão de robustez a ruído e múltiplas sementes está em revisão no PR #12, dependente do #11; o benchmark de previsão temporal com a rede completa está em revisão no PR #13, dependente do #12; a agregação multi-semente está em revisão no PR #14, dependente do #13; o experimento de mudança de regime está em revisão no PR #15, dependente do #14; a agregação multi-semente da mudança de regime está em revisão no PR #16, dependente do #15. O AMA ainda não é um sistema autônomo de geração de renda e não deve ser usado para movimentar dinheiro, publicar conteúdo ou assumir compromissos externos.

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
│   ├── ana/            # especificações e experimentos da ANA
│   └── decisions/
├── src/ama/
│   ├── ana/            # unidade, rede, memória temporal, aprendizado e plasticidade experimental
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
| Experimento sintético de plasticidade v0.5 | Em revisão no PR #11 (dependente do #10) |
| Robustez a ruído e múltiplas sementes | Em revisão no PR #12 (dependente do #11) |
| Previsão temporal com a rede completa | Em revisão no PR #13 (dependente do #12) |
| Agregação multi-semente da previsão | Em revisão no PR #14 (dependente do #13) |
| Adaptação após mudança de regime | Em revisão no PR #15 (dependente do #14) |
| Agregação multi-semente da mudança de regime | Em revisão no PR #16 (dependente do #15) |
| Linguagem natural livre | Não implementada |
| Aprendizado cognitivo/neural | Protótipos experimentais ANA v0.4/v0.5 |
| Organização empresarial e agentes | Futuro |
| Operação de negócios e integrações | Futuro, sujeita à governança |

## Limites atuais

O Cognitive Core manipula observações estruturadas e regras determinísticas; não interpreta linguagem natural livre. A ANA v0.1 implementa uma transição numérica para uma unidade isolada. A ANA v0.2 conecta unidades em um grafo dirigido e propaga sinais sincronamente usando o estado anterior; a topologia e os pesos permanecem fixos. A ANA v0.3 mantém traços temporais em diferentes escalas e produz contexto agregado, ainda sem integração automática à rede. A ANA v0.4 adiciona regras experimentais de ajuste supervisionado, por recompensa e previsão auto-supervisionada em um vetor de pesos de saída escalar; ainda não treina a rede recorrente inteira. A ANA v0.5 pesquisa plasticidade limitada em um conjunto explícito de conexões candidatas, com fortalecimento, ativação e poda controlados; não cria unidades nem pares arbitrários. Os experimentos de plasticidade medem rastreamento de peso em uma sequência sintética; o benchmark de previsão executa uma rede de duas unidades e avalia um readout linear em um segmento temporal separado; o PR #14 agrega resultados em múltiplas sementes e o PR #15 testa adaptação após mudança de regime e o PR #16 agrega esse teste em múltiplas sementes, mas ainda não treina os parâmetros internos da rede nem demonstra inteligência ou generalização para dados reais. Nenhum desses componentes executa negócios ou ações externas.

Consulte [docs/ROADMAP.md](docs/ROADMAP.md) para a sequência de desenvolvimento e os documentos em [docs/ana](docs/ana/) para protocolos e resultados experimentais.
