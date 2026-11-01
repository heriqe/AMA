# Arquitetura do AMA

**Versão do documento:** 0.3  
**Status:** arquitetura inicial em implementação.

## 1. Visão geral

O AMA será desenvolvido como um monólito modular no início. Os módulos terão fronteiras claras e interfaces testáveis; separar serviços só será considerado quando houver necessidade operacional comprovada.

O desenvolvimento da inteligência própria começa pelo **Cognitive Core**. A **ANA** será uma linha de pesquisa independente e será integrada depois, por uma interface explícita.

## 2. Camadas

- **Percepção:** valida e normaliza entradas estruturadas. A implementação atual não interpreta linguagem natural livre.
- **Conhecimento:** representa fatos explícitos, origem, confiança informada e validade temporal opcional. A política classifica fatos como aceitos, conflitantes, expirados ou de baixa confiança.
- **Memória:** armazena observações, avaliações e rastros de inferência com origem e data. Persistência não é, por si só, aprendizado.
- **Raciocínio:** aplica regras explícitas e produz rastros estruturados contendo regra, premissas e conclusão.
- **Planejamento:** decompõe objetivos em tarefas e dependências; o planejador atual valida ciclos e produz uma ordem topológica.
- **Decisão:** avalia alternativas declaradas sob orçamento, moeda, risco, evidência e requisitos de aprovação. O motor v0.3 recomenda ou se abstém; não executa.
- **Execução:** futuramente executa somente ações autorizadas, com validação, sandbox e registro.
- **Aprendizado:** futuramente avalia resultados e propõe atualizações controladas.
- **ANA:** pesquisa independente de unidades neurais, dinâmica, conexões e aprendizado próprios.

## 3. Fluxo cognitivo

```text
Observação estruturada
        |
    Percepção
        |
  Conhecimento e política
        |
  Raciocínio determinístico
        |
  Memória e rastreabilidade
        |
  Planejamento de tarefas
        |
  Decisão sob restrições
        |
  (futura execução autorizada)
```

O pipeline cognitivo v0.2 processa observações estruturadas e registra fatos, avaliações e inferências. O mecanismo de decisão v0.3 é um componente puro separado: recebe alternativas e orçamento declarados e produz avaliações sem executar ações.

## 4. Decisões técnicas

- Python 3.11+ como linguagem principal do núcleo.
- SQLite para persistência local inicial.
- Biblioteca padrão sempre que possível.
- Pytest para testes automatizados.
- ANA permanece independente do Cognitive Core até existir interface testada.
- React será considerado posteriormente para um painel, não como dependência do núcleo.
- Nenhuma chamada a LLM externo é necessária para executar os componentes atuais.

## 5. Limites atuais

A percepção valida estruturas de dados; não extrai significado de texto livre. A confiança de um fato é metadado fornecido pela origem, não probabilidade calibrada. O planejador ordena tarefas e detecta dependências inválidas; não avalia sozinho viabilidade econômica.

O motor de decisão usa somente projeções fornecidas. Sua pontuação é heurística, não previsão estatística nem garantia de lucro. A moeda precisa coincidir; dinheiro é representado por `Decimal`. Orçamento é limite de planejamento, não saldo bancário nem autorização para gastar. Candidatos que exigem aprovação humana não são selecionados automaticamente.

Nenhum componente atual publica conteúdo, contrata serviços, transfere dinheiro ou assume compromissos externos.

## 6. Evolução

Mudanças de arquitetura devem atualizar este documento e, quando relevantes, registrar uma decisão em `docs/decisions/`. Cada etapa precisa de testes, critérios de aceitação e limites conhecidos antes de avançar.
