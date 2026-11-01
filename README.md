# AMA — Autonomous Money AI

O **AMA** é um projeto experimental para construir uma plataforma própria de inteligência cognitiva e gestão de oportunidades legítimas de geração de renda.

A meta é desenvolver, em etapas verificáveis, um núcleo cognitivo independente de serviços externos de IA e, em uma linha de pesquisa separada, a **ANA (AMA Neural Architecture)**. A integração entre os dois só ocorrerá quando houver componentes testados e interfaces definidas.

> **Estado atual:** Foundation v0.1 integrada à `main`; Cognitive Core v0.2 em desenvolvimento no PR #2. O AMA ainda não é um sistema autônomo de geração de renda e não deve ser usado para movimentar dinheiro, publicar conteúdo ou assumir compromissos externos.

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
│   └── decisions/
├── src/ama/
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
| Fundação e empacotamento Python | Implementado |
| Tipos básicos de entrada e resultado | Implementado |
| Memória SQLite simples | Implementado |
| Motor lógico determinístico mínimo | Implementado |
| Fatos estruturados com origem e confiança | Implementado |
| Política para fatos vencidos, fracos e conflitantes | Implementada no PR v0.2 |
| Rastreabilidade estruturada de inferências | Implementada no PR v0.2 |
| Fluxo percepção → conhecimento → raciocínio → memória | Implementado no PR v0.2 |
| Linguagem natural livre | Não implementada |
| Aprendizado cognitivo | Pesquisa futura |
| ANA / unidade neural | Especificação e experimentos futuros |
| Organização empresarial e agentes | Futuro |
| Operação de negócios e integrações | Futuro, sujeita à governança |

### Limites do Cognitive Core atual

A percepção aceita apenas observações estruturadas; não interpreta linguagem natural. A política de conhecimento usa confiança como metadado fornecido pela fonte, não como probabilidade calibrada. Quando valores elegíveis de um mesmo predicado divergem, o pipeline não escolhe um vencedor: marca conflito e impede que esse predicado alimente as regras. Fatos expirados ou abaixo do limiar configurado também não são usados.

O pipeline registra observações, avaliações e disparos de regras na memória. Ele não executa tarefas, não verifica a verdade no mundo externo e não autoriza ações externas. O limite padrão de leitura do pipeline é de 10.000 fatos por ciclo.

Consulte [docs/ROADMAP.md](docs/ROADMAP.md) para a sequência de desenvolvimento.
