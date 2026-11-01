# Arquitetura do AMA

**Versão do documento:** 0.2  
**Status:** arquitetura inicial em implementação.

## 1. Visão geral

O AMA será desenvolvido como um monólito modular no início. Os módulos terão fronteiras claras e interfaces testáveis; separar serviços só será considerado quando houver necessidade operacional comprovada.

O desenvolvimento da inteligência própria começa pelo **Cognitive Core**. A **ANA** será uma linha de pesquisa independente e será integrada depois, por uma interface explícita.

## 2. Camadas

- **Percepção:** valida e normaliza entradas estruturadas. A implementação atual não interpreta linguagem natural livre.
- **Conhecimento:** representa fatos explícitos, origem, confiança informada e validade temporal opcional.
- **Memória:** armazena experiências e registros com origem e data. Persistência não é, por si só, aprendizado.
- **Raciocínio:** aplica regras explícitas e inferências verificáveis.
- **Planejamento:** decompõe objetivos em tarefas e dependências; o planejador atual valida ciclos e produz uma ordem topológica.
- **Decisão:** futuramente compara alternativas sob restrições, orçamento e permissões.
- **Execução:** futuramente executa somente ações autorizadas, com validação e registro.
- **Aprendizado:** futuramente avalia resultados e propõe atualizações controladas.
- **ANA:** pesquisa independente de unidades neurais, dinâmica, conexões e aprendizado próprios.

## 3. Fluxo conceitual

```text
Entrada estruturada
        |
    Percepção ------> Conhecimento <----> Memória
        |                  |
        +--------------> Raciocínio
                             |
                         Planejamento
                             |
                          Decisão <---- Governança
                             |
                    Execução autorizada
                             |
                     Resultado e auditoria
                             |
                    Avaliação / aprendizado

ANA (linha independente de pesquisa)
        |
integração futura por interface testada
```

## 4. Decisões técnicas iniciais

- Python 3.11+ como linguagem principal do núcleo.
- SQLite para persistência local inicial.
- Biblioteca padrão sempre que possível.
- Pytest para testes automatizados.
- NumPy poderá ser introduzido nos experimentos da ANA quando necessário; não é dependência do núcleo inicial.
- React será considerado posteriormente para um painel, não como dependência do núcleo.
- Nenhuma chamada a LLM externo será necessária para executar os componentes desta fundação.

## 5. Limites atuais

O motor lógico manipula fatos explícitos e aplica regras cadastradas. A percepção valida estruturas de dados; não extrai significado de texto livre. A confiança de um fato é um metadado fornecido pela origem, não uma probabilidade calibrada nem prova de veracidade.

O planejador ordena tarefas e detecta dependências inválidas; ele não avalia sozinho se um objetivo é economicamente viável. A memória atual é armazenamento persistente simples; armazenar dados não significa que o sistema aprendeu com eles.

## 6. Evolução

Mudanças de arquitetura devem atualizar este documento e, quando relevantes, registrar uma decisão em `docs/decisions/`. Cada etapa precisa de testes e critérios de aceitação antes de avançar.
