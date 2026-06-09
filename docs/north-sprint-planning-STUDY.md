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

## 1.5. Decisões fechadas com o dono (2026-06-09)

> As perguntas Q1–Q11 e a §8 foram respondidas inline pelo dono. Resumo travado:

- **Colunas (Q1–Q3):** **sem `CLIENTE`.** As 4 colunas de fluxo são **DESENVOLVER ·
  FASE DE DESENVOLVIMENTO · FASE DE TESTES · CONCLUÍDO**; **IMPEDIMENTO = flag**. Uma task só
  chega a **CONCLUÍDO depois de passar pela FASE DE TESTES + code-review** (é o DoD da coluna).
- **Colunas = perfil configurável** (não hardcode que troca pra todos). ✔
- **Tags (Q4–Q6):** alimentam **filtro/visual E a sugestão de squad** no `/north-focus`;
  **paleta fixa determinística por nome**; **há conflito visual** com a tag de feature no card
  → o layout precisa resolver (não exibir as duas cruas; priorizar/compactar — ver §3).
- **Geração (Q7–Q8):** grava em **`plan-build/`** (cria se não existir), **sempre com destino
  explícito**; a IA propõe a quebra **a partir dos docs** (ou do SPEC, se houver). Granularidade
  de `plan-build` (um por projeto vs um por feature/microsserviço) é **sub-estudo aberto** (§4.1).
- **Estimativa (Q9–Q11):** unidade = **esforço (tasks/pontos)**, depois **traduzida p/ prazo**
  (calendário sofre com férias/paralelo); cronômetro tem **dois marcos** — chega em `FASE DE
  TESTES` e depois `CONCLUÍDO`; **amostra mínima ~5 tasks reais / 90 dias** antes de arriscar.
- **Princípio de rastreio (§9):** alteração fora da sprint **sempre** é trackeada — task na
  sprint atual ou **Quick Win**, conforme o tamanho/dificuldade.

> Relacionado: o **modelo de enrollment** (como o north sabe quais projetos rastrear) virou um
> ADR próprio — ver `docs/north-discovery-enrollment-ADR.md`. Ele define a *unidade de
> rastreio*, que é a mesma coisa que a granularidade de `plan-build` da §4.1.

---

## 2. Modelo de colunas proposto (4 de fluxo + flag de impedimento)

Confirmado com o dono: **IMPEDIMENTO = flag** (mantém o estágio). Logo, **4 colunas de fluxo**:

| # | Coluna | Significado | Mapeia do estado atual |
|---|---|---|---|
| 1 | **DESENVOLVER** | a fazer / backlog priorizado, não começou | `Planejado` |
| 2 | **FASE DE DESENVOLVIMENTO** | em codificação ativa (WIP) | `Em Andamento` |
| 3 | **FASE DE TESTES** | código pronto, em **testes + code-review** | `Código Completo` |
| 4 | **CONCLUÍDO** | entregue/finalizado — **só após testes + code-review aprovados** (DoD) | `Concluído` (≈) |
| — | **⛔ IMPEDIMENTO** | *flag* ortogonal: bloqueada, fica no estágio, realçada | `blocked=True` (já existe) |

**Decisão de arquitetura importante — colunas viram PERFIL configurável, não hardcode.**
O north tem muitos usuários; impor *este* fluxo a todos quebra "defaults sensatos, config
opcional". Proposta: um **profile de board** em config (`board_profile`), com o atual como
default e este modelo como alternativa selecionável. Mapeamento status→coluna fica orientado
a dados (tabela), não regex espalhado.

### Questões em aberto (precisam de você — "estudar melhor")
- **Q1.** `CLIENTE` é terminal (= entregue/aceito) ou precisamos de um passo *depois* (ex.:
  `ACEITO`/`CONCLUÍDO`) para distinguir "com o cliente" de "aprovado pelo cliente"? Isso afeta
  onde o ciclo de vida termina — e **onde a estimativa de prazo "para o relógio"** (§5). | RESPOSTA: não terá coluna `CLIENTE`, será `CONCLUÍDO`
- **Q2.** "Em validação pelo cliente" e "entregue ao cliente" são o mesmo estágio ou dois? | RESPOSTA: `CONCLUÍDO`
- **Q3.** Como o usuário sinaliza `CLIENTE` no `.md`? (status textual `cliente`/`validação`,
  emoji próprio, ou seção?) — define a regra de detecção read-only. | RESPOSTA: não terá coluna `CLIENTE`

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
- **Q4.** Tag é só *visual/filtro*, ou também **alimenta a sugestão de squad** no `/north-focus`? | RESPOSTA: ambos
- **Q5.** Cor por tag: paleta fixa por nome (determinística) ou herda da feature? | RESPOSTA: fixa
- **Q6.** Tag conflita com a tag de *feature* já existente no card? (espaço visual no card) | RESPOSTA: conflita

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
  perguntar) — é a mesma decisão #4 em aberto da visão; vale fechar junto. | RESPOSTA: `plan-build/`, se não tiver, ele cria e grava lá. SEMPRE definir explicitamente onde o plano deve ser salvo e não ter mais de um plan-build por projeto, exemplo um na raiz, um dentro de cada feature, etc. Deve segregar por feature/microsserviço. MAS podemos estudar isso, se é melhor um plan-build por projeto ou um por feature/microsserviço.
- **Q8.** A IA propõe a quebra em tasks a partir do SPEC, ou o usuário lista e a IA estrutura? | RESPOSTA: A partir dos docs (ou do SPEC, se disponível)

### 4.1. Sub-estudo: granularidade do `plan-build` (um por projeto vs por feature/microsserviço)

O dono quer **destino explícito e segregação por feature/microsserviço**, sem a bagunça atual
de `plan-build` espalhado de forma inconsistente. Há duas convenções, e a escolha **deve casar
com a unidade de rastreio do ADR de enrollment** (`docs/north-discovery-enrollment-ADR.md`) —
*o que você "pluga" é o que vira um board/projeto no north*:

| Convenção | Como fica | Bom para | Custo |
|---|---|---|---|
| **1 `plan-build` na raiz do projeto** | um board; o north já agrupa por subpasta = *feature group* | app único / monólito pequeno | tudo num board só |
| **1 `plan-build` por feature/microsserviço** | cada serviço plugado é um projeto/board próprio | microsserviços / deploys independentes | mais coisas pra plugar/gerir |

**Recomendação (a granularidade é consequência do que você pluga):** se você plugar a **raiz**
de um monorepo, o north usa **um `plan-build`** e segrega por subpasta (feature group — *já
existe* hoje, `discovery.py:66-95`). Se você plugar **cada microsserviço**, cada um é um
projeto com seu `plan-build`. Regra dura: **um `plan-build` por unidade de rastreio**, nunca
dois competindo dentro da mesma unidade. Continuar estudando, mas o mecanismo suporta os dois.

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
- **Ledger de aprendizado**: gotchas/bugs recorrentes que
  inflam estimativa naquele tipo de trabalho.

**Como devolve (honesto, sem falsa precisão):**
- Faixa, não número mágico: *"tasks `[API]` parecidas levaram 3–6 dias (mediana 4); esta sprint
  tem 5 delas → ~3–4 semanas, P50 3.2sem"*.
- Sempre com a base: *"baseado em N tasks reais dos últimos 90 dias"*. Pouca amostra ⇒ diz que
  é palpite fraco. **Nunca finge precisão que não tem.**
- Sugere, o humano decide (igual ao foco/squad). Não "trava" prazo.

**Onde vive:** começa **simples no CLI** (estatística básica de git+ledger, stdlib) e fica
**rico na plataforma** (Fase 2+: histórico agregado, comparação entre projetos, forecasting).
Casa com [visão da plataforma](north-platform-vision-v2.md) e a camada de aprendizado/cert.

### Questões em aberto
- **Q9.** Unidade de estimativa: tempo de calendário (dias) ou esforço (tasks/pontos)? Calendário
  sofre com férias/paralelo; esforço é mais estável mas exige tradução p/ prazo. | RESPOSTA: Esforço (tasks/pontos) é mais estável e exige tradução p/ prazo, mas calendário sofre com férias/paralelo.
- **Q10.** "Concluída" para fim de cronômetro = chega em `CLIENTE` ou em `FASE DE TESTES`? (liga na Q1) | RESPOSTA: primeiro `FASE DE TESTES`, depois `CONCLUIDA`.
- **Q11.** Amostra mínima para o north arriscar uma estimativa (ex.: < 5 tasks ⇒ só mostra dado bruto)? | RESPOSTA: acredito que seja o recomendado como o exemplo de 5 tasks reais dos últimos 90 dias.

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

**Sequência:** Q1–Q11 **fechadas** (§1.5) → A → B → C → D. Fatia **E** fica para a plataforma.
Falta só: o sub-estudo §4.1 (granularidade do `plan-build`, ligado ao ADR de enrollment) e
**A inclui a regra de Quick Win (§9)** na detecção do wrap-up.

---

## 8. Decisões que destravam o próximo passo

1. Responder Q1–Q11 (ou as que você tiver opinião; o resto eu recomendo um default). | RESPOSTA: respondido
2. Confirmar que colunas são **perfil configurável** (não hardcode que troca pra todos). | RESPOSTA: confirmado
3. Confirmar gravação do plano de sprint (Q7) — junto da decisão #4 em aberto da visão. | RESPOSTA: confirmado

Quando isso fechar, eu monto o **plano de execução por squad** (Arquitetura → Backend/engine →
QA → docs) com paridade nos 3 runtimes. Dogfooding sugerido: gerar este próprio fluxo com o
`north-doc` quando o tipo `sprint` existir.

## 9. Princípio de rastreio: nada de trabalho fora do radar (Quick Wins)

**Regra do dono:** qualquer alteração no projeto que **não** está traçada numa sprint, o north
**sempre** deve avisar e oferecer registrá-la — como **task na sprint atual** (se grande/no
escopo) ou como **Quick Win** (se pequena/avulsa). Nada de mudança não-rastreada.
*Exemplo:* Sprint 1 = "criar o front de X"; finalizou, mas precisou de um ajuste pequeno →
registra como Quick Win; ajuste grande → registra como task. O peso do registro segue a
dificuldade/tamanho da mudança.

**Como cabe no invariante read-only:**
- **Detectar (read-only):** o north já liga commits↔tasks e tem o sinal de git pessoal. No
  `/north-wrap-up` ele detecta commits/diffs do dia **que não batem com nenhuma task trackeada**
  e **cutuca**: *"você mexeu em `Foo.cs` que não está em nenhuma sprint — registrar como task na
  Sprint atual ou como Quick Win?"*.
- **Registrar (confirma-pra-escrever):** se você aceitar, o north **escreve com confirmação** —
  uma task/Quick Win no `plan-build/` (mesmo fluxo do gerador de sprint, §4). Nunca edita
  silenciosamente; é sempre a IA propondo e você aprovando.
- **Quick Win = entrada leve trackeada** para trabalho avulso/hotfix que não merece uma task
  cheia, mas precisa existir no histórico (e alimenta a estimativa da §5).

> Implicação: isto fecha o loop "plano ↔ realidade". A força do north é derivar do trabalho
> real — esta regra garante que o trabalho real que escapou do plano **volte** pro plano.
