# Governança e limites de autonomia

**Versão:** 0.1

A autonomia do AMA é limitada por permissões explícitas, orçamento autorizado, políticas legais e regras de cada plataforma. A capacidade técnica de executar uma ação não significa autorização para executá-la.

## Níveis de autonomia

- **A0 — Pesquisa:** coletar informações, comparar oportunidades e produzir análises.
- **A1 — Preparação:** criar arquivos, protótipos e testes em ambiente isolado.
- **A2 — Operação autorizada:** publicar ou operar somente em contas e plataformas previamente autorizadas, respeitando limites específicos.
- **A3 — Administração limitada:** administrar recursos dentro de tetos, escopos e regras expressamente aprovados.

O nível deve ser concedido por um responsável humano. Um componente do AMA não pode elevar o próprio nível nem conceder permissões a si mesmo.

## Aprovação humana obrigatória

Até que exista um processo formal, as ações abaixo permanecem proibidas para execução autônoma:

- transferir dinheiro, realizar pagamentos, contratar crédito ou movimentar contas;
- assumir obrigações jurídicas, aceitar contratos ou fazer declarações legais;
- alterar credenciais, permissões ou controles de segurança;
- publicar ou enviar comunicações externas sem autorização específica;
- exceder orçamento, escopo ou limites aprovados.

## Regras financeiras

- Separar dinheiro real, valores simulados, previsões e metas.
- Registrar receita somente com evidência verificável.
- Calcular resultado considerando taxas, custos, reembolsos, tributos e reservas aplicáveis.
- Não tratar empréstimos, transferências internas ou aportes como lucro operacional.
- Manter trilha de auditoria para cada lançamento e decisão financeira.

## Supervisão e bloqueio

A futura camada de governança deverá validar ações fora do agente que as solicita. A supervisão deve poder bloquear uma ação e registrar o motivo. Prompts ou instruções em linguagem natural não substituem controles determinísticos no código.

## Segurança por padrão

- Sem execução de comandos arbitrários por padrão.
- Sem armazenamento de senhas, tokens ou cookies em texto puro.
- Segredos devem permanecer fora do repositório.
- Integrações devem usar o menor conjunto de permissões necessário.
- Ações externas devem ser registradas e, quando possível, idempotentes e reversíveis.
