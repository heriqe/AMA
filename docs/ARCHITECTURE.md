# Arquitetura do AMA

**Versão do documento:** 0.1  
**Status:** arquitetura inicial; sujeita a revisão por decisões documentadas.

## 1. Visão geral

O AMA será desenvolvido como um monólito modular no início. Os módulos terão fronteiras claras e interfaces testáveis; separar serviços só será considerado quando houver necessidade operacional comprovada.

O desenvolvimento da inteligência própria começa pelo **Cognitive Core**. A **ANA** será uma linha de pesquisa independente e será integrada depois, por uma interface explícita.

## 2. Camadas planejadas

- **Percepção:** normalizar entradas e identificar informações relevantes.
- **Conhecimento:** representar fatos, conceitos, fontes e grau de confiança.
- **Memória:** armazenar experiências, fatos e registros com origem e data.
- **Raciocínio:** aplicar regras explícitas e inferências verificáveis.
- **Planejamento:** decompor objetivos em tarefas e dependências.
- **Decisão:** comparar alternativas sob restrições e permissões.
- **Execução:** executar somente ações autorizadas, com validação e registro.
- **Aprendizado:** avaliar resultados e propor atualizações controladas.
- **ANA:** pesquisa de unidades neurais, dinâmica, conexões e aprendizado próprios.

## 3. Fluxo conceitual

```text
Entrada
  |
Percepção -> Conhecimento <-> Memória
  |                         |
  +------> Raciocínio <-----+
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
     integração futura por interface
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

O motor lógico inicial não é um modelo de linguagem nem possui compreensão geral. Ele manipula estruturas explícitas e aplica regras cadastradas. Não deve ser descrito como equivalente a um sistema conversacional avançado.

A memória atual é armazenamento persistente simples; armazenar dados não significa que o sistema aprendeu com eles.

## 6. Evolução

Mudanças de arquitetura devem atualizar este documento e, quando relevantes, registrar uma decisão em `docs/decisions/`. Cada etapa precisa de testes e critérios de aceitação antes de avançar.
