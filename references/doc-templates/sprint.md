# Sprint-<N> — <título curto do objetivo>

> Plano de sprint no formato que o painel do north LÊ de volta (vira kanban + contrato
> de cada task). Grave em `plan-build/` (ou `plan-build/<feature>/`) — **um por
> feature/microsserviço**. A IA quebra em tasks a partir dos docs (PRD/SPEC); o motor é
> read-only (escreve com sua confirmação).

## Meta do Sprint
- **Objetivo:** <o resultado ÚNICO deste sprint — orientado a outcome, não a lista de tickets>
- **Entregável:** <o que estará pronto e demonstrável ao fim>
- **Por que agora:** <a justificativa — por que este é o próximo passo de maior valor>

## O que NÃO entra (fora do escopo)
- <itens explicitamente fora — protege o foco quando a realidade aperta>

## Tasks

| TASK | Descrição | Status | Responsável | Dependências |
|---|---|---|---|---|
| TASK-01 | [API] <o que fazer, em uma linha> | Planejado | squad-backend | — |
| TASK-02 | [FRONTEND/UI/UX] <…> | Planejado | squad-frontend | TASK-01 |
| TASK-03 | [PESQUISA] <…> | Planejado | squad-pesquisa | — |

> **Status válidos** (o painel mapeia p/ o kanban): `Planejado` · `Em Andamento` ·
> `Código Completo` · `Concluído` · `⛔ Bloqueada`. O **impedimento é uma flag** — a task
> bloqueada **fica no estágio** e é realçada, não vira coluna.
> **Tags de disciplina** no início da descrição: `[ANALISE]` `[API]` `[FRONTEND/UI/UX]` `[PESQUISA]`
> (sugerem o squad; uma primária por task).

## Contrato das tasks (entregável + critério de aceite)

**TASK-01 — <título>**
- **Builder entrega:** <o que será construído / o que fazer>
- **Evaluator valida:** <critério de aceite **testável e inequívoco**>

**TASK-02 — <título>**
- **Builder entrega:** <…>
- **Evaluator valida:** <…>

## Definição de Pronto (DoD do sprint)
- Uma task só vai a **`Concluído`** depois de passar pela **FASE DE TESTES + code-review**.
- <outros critérios de qualidade: sem regressão, doc atualizada onde aplica…>

## Pré-leitura / referências
- <PRD/SPEC/SDD/ADR que embasam este sprint — o painel linka como "pré-leitura">

---
*Gerado com `/north-doc sprint`. Ancore no PRD/SPEC reais do projeto; cada `Evaluator valida:`
deve ser verificável. Estimativa de prazo: o north aprende do histórico (git + ledger) — não
chute. Read-only: a IA escreve com sua confirmação, no `plan-build/` que você aprovar.*
