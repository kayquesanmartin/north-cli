# Estudo — Planejamento de Sprints, Kanban e Estimativa por Aprendizado

> **Status:** estudo/design para discussão — nada aqui é compromisso de implementação.
> **Base:** north-cli v0.9.1 · **Data:** 2026-06-09 · **Autor:** Tech Lead (sessão north)
> **Objetivo:** desenhar como o north passa de *ler* sprints para também *ajudar a planejá-las*
> — com um modelo de kanban próprio, taxonomia de tags, geração de sprint/entregável a partir
> dos docs, e **estimativa de prazo aprendida do trabalho real**. Tudo respeitando o invariante
> read-only.

---

## 0. Princípio que não muda

**north é read-only sobre os planos do usuário.** Ele *lê* git e planos; *escreve* só na casa
dele (`~/.north`, dashboard, inbox) e em arquivos novos **com confirmação** do usuário (como o
`north-doc` já faz). Nada aqui pode editar plano existente do usuário sem ele mandar. Toda
"geração" é *scaffolding que você confirma*, nunca edição silenciosa.

---

## 1. Estado atual (o que o estudo de código encontrou)

- **O north NÃO planeja sprints hoje — ele só lê.** Não há gerador nem template de sprint no
  `north-doc` (que cobre PRD/SPEC/SDD/TDD/ADR/SECURITY). O kanban é 100% derivado dos
  `Sprint*.md`/`Progress.md` que o usuário escreve.
- **Kanban atual = 4 colunas** (`src/painel/parsers.py:23-34`), mapeadas por
  `classify_status()` (`parsers.py:108-135`):
  `📋 Planejado` · `⚡ Em Andamento` · `🟢 Código Completo` · `✅ Concluído`.
- **IMPEDIMENTO já é flag, não coluna** — task bloqueada fica no estágio e ganha borda/⛔
  (`blocked=True`). ✅ Vamos manter assim.
- **Tags por task NÃO existem.** Só há tag de *feature* (pasta) e de *sprint*, coloridas por
  hash (`render.py:949-955`). Não há extração de `[TAG]` do título.
- **Touch points** (já mapeados): `parsers.py` (colunas + classificação), `discovery.py`
  (montagem da task, ~460-473), `render.py` (JSON + HTML/CSS/JS do kanban), `gsd.py` (adapter).

---

## 2. Modelo de colunas proposto (4 de fluxo + flag de impedimento)

Confirmado com o dono: **IMPEDIMENTO = flag** (mantém o estágio). Logo, **4 colunas de fluxo**:

| # | Coluna | Significado | Mapeia do estado atual |
|---|---|---|---|
| 1 | **DESENVOLVER** | a fazer / backlog priorizado, não começou | `Planejado` |
| 2 | **FASE DE DESENVOLVIMENTO** | em codificação ativa (WIP) | `Em Andamento` |
| 3 | **FASE DE TESTES** | código pronto, em teste/review/QA | `Código Completo` |
| 4 | **CLIENTE** | entregue ao / em validação pelo cliente | `Concluído` (≈) |
| — | **⛔ IMPEDIMENTO** | *flag* ortogonal: bloqueada, fica no estágio, realçada | `blocked=True` (já existe) |

**Decisão de arquitetura importante — colunas viram PERFIL configurável, não hardcode.**
O north tem muitos usuários; impor *este* fluxo a todos quebra "defaults sensatos, config
opcional". Proposta: um **profile de board** em config (`board_profile`), com o atual como
default e este modelo como alternativa selecionável. Mapeamento status→coluna fica orientado
a dados (tabela), não regex espalhado.

### Questões em aberto (precisam de você — "estudar melhor")
- **Q1.** `CLIENTE` é terminal (= entregue/aceito) ou precisamos de um passo *depois* (ex.:
  `ACEITO`/`CONCLUÍDO`) para distinguir "com o cliente" de "aprovado pelo cliente"? Isso afeta
  onde o ciclo de vida termina — e **onde a estimativa de prazo "para o relógio"** (§5).
- **Q2.** "Em validação pelo cliente" e "entregue ao cliente" são o mesmo estágio ou dois?
- **Q3.** Como o usuário sinaliza `CLIENTE` no `.md`? (status textual `cliente`/`validação`,
  emoji próprio, ou seção?) — define a regra de detecção read-only.

---

## 3. Taxonomia de tags (estudar com cuidado — pedido do dono)

Tags do dono: `[ANALISE]` · `[API]` · `[FRONTEND/UI/UX]` · `[PESQUISA]`. São tags de
**disciplina/tipo de trabalho** — e têm uma sinergia ótima: **a tag sugere o squad** que ataca
(já que `/north-focus` "sugere o squad"). Proposta de design:

- **Conjunto default curado + extensível.** Os 4 do dono são o default; o usuário pode
  adicionar os próprios em config (`task_tags`). Não travar num enum fixo.
- **Onde vivem:** **prefixo no título da task** — `[API] Implementar endpoint de cotação`.
  É legível por humano, fácil de escrever e trivial de parsear read-only.
  Regex candidata: `^\s*((?:\[[A-Z][\w\-\/ ]*\]\s*)+)`.
- **Múltiplas por task:** permitido (`[API][ANALISE] …`), mas incentivar **uma primária**.
- **Normalização de aliases:** `FRONT`, `UI`, `UX`, `FRONTEND` → uma tag canônica
  `FRONTEND/UI/UX`. Tabela de aliases em um só lugar.
- **Mapa tag → squad** (sugestão, não regra):
  `[API]→Backend` · `[FRONTEND/UI/UX]→Frontend/UIUX` · `[ANALISE]→Arquitetura/GP` ·
  `[PESQUISA]→Pesquisa`.
- **Render:** chip colorido por tag (paleta estável, como features/sprints já fazem).

### Questões em aberto
- **Q4.** Tag é só *visual/filtro*, ou também **alimenta a sugestão de squad** no `/north-focus`?
- **Q5.** Cor por tag: paleta fixa por nome (determinística) ou herda da feature?
- **Q6.** Tag conflita com a tag de *feature* já existente no card? (espaço visual no card)

---

## 4. Geração: do doc à sprint e ao entregável (north-doc estendido)

Hoje o `north-doc` para no doc. A ideia é **continuar o fluxo**: depois do PRD/SPEC, o north
**ajuda a quebrar em sprints e a definir entregáveis** — escrevendo um arquivo de plano de
sprint **com sua confirmação** (motor read-only; a IA redige sob sua direção).

```
PRD ─▶ SPEC ─▶ [novo] PLANO DE SPRINT ─▶ tasks com entregável + critério de aceite + tag
                     │
                     └─ scaffolding na convenção (4 colunas + taxonomia de tags),
                        que o dashboard depois LÊ de volta no kanban (loop fechado)
```

- **Novo tipo de doc `sprint`** no `north-doc` (template em `references/doc-templates/sprint.md`),
  com **paridade nos 3 runtimes** (CMDSPEC é a fonte de verdade — vira skill em Claude/Codex/Gemini).
- O template já nasce no formato que o `parsers.py` sabe ler: tabela de tasks com
  `id · descrição (com [TAG]) · entregável · critério de aceite · status · responsável`.
- **Definição de entregável** ancorada no que o north já extrai (`Builder entrega:` /
  `Evaluator valida:` — `parsers.py:318-364`), então o gerado e o lido falam a mesma língua.

### Questões em aberto
- **Q7.** O plano de sprint gerado grava onde por default? (`plan-build/` vs `docs/` vs
  perguntar) — é a mesma decisão #4 em aberto da visão; vale fechar junto.
- **Q8.** A IA propõe a quebra em tasks a partir do SPEC, ou o usuário lista e a IA estrutura?

---

## 5. Estimativa de prazo aprendida do trabalho real (o que o dono lembrou)

> "ele aprender conforme nosso desenvolvimento e entregas e ele mesmo definir um tempo/prazo"

Isto é **o diferencial da plataforma aplicado ao planejamento**: em vez de chutar prazo, o
north **mede o seu ritmo real** e estima com base nele. Tudo read-only (git + ledger).

**Sinais que o north já pode derivar (sem nada novo de dado):**
- **Cycle time:** do 1º commit que toca uma task até o commit que a marca concluída
  (o north já liga task↔commit via `find_commit()`).
- **Throughput:** tasks concluídas por semana (datas de commit/autoria — já lidas).
- **Duração histórica de sprint:** quanto sprints parecidas levaram de fato.
- **Sinal por tag/disciplina:** `[API]` leva, em média, X; `[FRONTEND]`, Y.
- **Ledger de aprendizado** ([[north-learning-ledger]]): gotchas/bugs recorrentes que
  inflam estimativa naquele tipo de trabalho.

**Como devolve (honesto, sem falsa precisão):**
- Faixa, não número mágico: *"tasks `[API]` parecidas levaram 3–6 dias (mediana 4); esta sprint
  tem 5 delas → ~3–4 semanas, P50 3.2sem"*.
- Sempre com a base: *"baseado em N tasks reais dos últimos 90 dias"*. Pouca amostra ⇒ diz que
  é palpite fraco. **Nunca finge precisão que não tem.**
- Sugere, o humano decide (igual ao foco/squad). Não "trava" prazo.

**Onde vive:** começa **simples no CLI** (estatística básica de git+ledger, stdlib) e fica
**rico na plataforma** (Fase 2+: histórico agregado, comparação entre projetos, forecasting).
Casa com [[north-platform-vision]] e [[north-learning-cert-layer]].

### Questões em aberto
- **Q9.** Unidade de estimativa: tempo de calendário (dias) ou esforço (tasks/pontos)? Calendário
  sofre com férias/paralelo; esforço é mais estável mas exige tradução p/ prazo.
- **Q10.** "Concluída" para fim de cronômetro = chega em `CLIENTE` ou em `FASE DE TESTES`? (liga na Q1)
- **Q11.** Amostra mínima para o north arriscar uma estimativa (ex.: < 5 tasks ⇒ só mostra dado bruto)?

---

## 6. Onde cada parte vive (read-only vs confirma-pra-escrever vs plataforma)

| Parte | Natureza | Casa |
|---|---|---|
| Colunas (perfil) + tags no kanban | **ler/render** read-only | `north-cli` (parsers/discovery/render) |
| Geração de plano de sprint + entregáveis | **escreve com confirmação** | `north-cli` (north-doc estendido) |
| Estimativa básica (git + ledger) | **ler/calcular** read-only | `north-cli` |
| Board interativo (arrastar card, atribuir tag/coluna) | **escreve estado** | **plataforma** (Fase 2 Solo web) — não cabe no CLI read-only |
| Forecasting agregado entre projetos | **escreve estado / nuvem** | **plataforma** |

---

## 7. Proposta de implementação faseada (quando você aprovar a §2–§5)

| Fatia | Entrega | Risco | Depende |
|---|---|---|---|
| **A** | Perfil de board configurável + 4 colunas (mapeamento orientado a dados) | baixo | Q1–Q3 |
| **B** | Extração + render de tags `[TAG]` no card (read-only) + normalização/aliases | baixo | Q4–Q6 |
| **C** | Template/gerador de sprint no `north-doc` (3 runtimes, confirma-pra-escrever) | médio | Q7–Q8, A |
| **D** | Estimativa básica (cycle time/throughput de git+ledger) exibida no plano/painel | médio | Q9–Q11, A |
| **E** | (plataforma) board interativo + forecasting agregado | alto | A–D, nuvem |

**Sequência:** fechar dúvidas Q1–Q11 → A → B → C → D. E fica para a plataforma.

---

## 8. Decisões que destravam o próximo passo

1. Responder Q1–Q11 (ou as que você tiver opinião; o resto eu recomendo um default).
2. Confirmar que colunas são **perfil configurável** (não hardcode que troca pra todos).
3. Confirmar gravação do plano de sprint (Q7) — junto da decisão #4 em aberto da visão.

Quando isso fechar, eu monto o **plano de execução por squad** (Arquitetura → Backend/engine →
QA → docs) com paridade nos 3 runtimes. Dogfooding sugerido: gerar este próprio fluxo com o
`north-doc` quando o tipo `sprint` existir.
