# Estudo — A tese de crescimento do north ("melhor, não só mais produtivo")

> **Status:** estudo/design para discussão — nada aqui é compromisso de implementação.
> **Base:** north-cli v0.9.1 · **Data:** 2026-06-09 · **Autor:** Tech Lead (sessão north)
> **Origem:** brainstorm do dono — 7 ideias "o que o north poderia ser além de um painel".
> **Objetivo:** elevar o fio condutor a **norte do produto**, e mapear cada ideia como
> *já existe / já decidido / genuinamente novo* — para não construir feature duplicada.

---

## 0. A tese-mãe (norte do produto)

> **"Você está ficando melhor ao longo do tempo, ou apenas mais produtivo?"**

Produtividade com IA é fácil de medir (tasks/velocidade) — e é o que **todo concorrente já
mede** (Copilot metrics, DX, LinearB). **Crescimento técnico** quase ninguém mede. O north está
em posição única porque **já lê seus projetos e já entende seu ritmo** — e a pesquisa de mercado
([[north-platform-vision]]) confirmou o gap: Workera/Pluralsight inferem skill de *provas*, não
do *trabalho real*; Copilot mede *uso*, não *crescimento*.

**Decisão proposta:** adotar isso como o **slogan/norte** do north — o diferencial que organiza
Solo, Teams e a camada de aprendizado/cert. "As outras ferramentas te deixam mais rápido; o
north te deixa melhor." Recomendo threadar isso no topo de [[north-platform-vision]].

---

## 1. As 7 ideias mapeadas (não reinventar o que já desenhamos)

| # | Ideia do dono | Status | Onde já vive / vai viver |
|---|---|---|---|
| 1 | **DECISIONS.md vivo** (o *porquê*, não o *quê*) | **Projeção nova de algo decidido** | memória `project` ([[north-memory-research-direction]]) + ledger (`learnings.py`) + ADR do `north-doc`. Novo = a **projeção em arquivo legível** que serve de contexto p/ IA e p/ você. |
| 2 | **/north-handoff + /north-resume** (sessão↔sessão) | **GENUINAMENTE NOVO** | memória de **continuidade de sessão** — não existe (north só tem morning/wrap-up). |
| 3 | **Modo de aprendizado** (resolve *com* você) + perfil de lacunas | **JÁ EXISTE + decidido** | `/north-learn` (mentor) + "cérebro do usuário" cross-project ([[north-memory-research-direction]]). |
| 4 | **Detector de dependência da IA** (espelho) | **GENUINAMENTE NOVO** | métrica nova; encarna a tese §0. Ver tensões §3. |
| 5 | **CONTEXT.md / briefing vivo** (stack, convenções, "não faça isso porque") | **Projeção nova de algo decidido** | mesma base do #1 (memória `project` projetada em arquivo); serve forte o **dev manual**. |
| 6 | **Estimativa honesta vs otimista** (fator de otimismo) | **ESTENDE o que está planejado** | estimativa aprendida (estudo de sprint §5) + **novo: loop estimativa-vs-real** (calibração pessoal). |
| 7 | **Code review p/ aprendizado** (trade-offs, não só erros) | **JÁ EXISTE + conexão nova** | `/north-review` (mentor) + **alimenta o perfil de lacunas** (#3/#4). |

**Leitura:** 4 das 7 já estão cobertas por fundações desenhadas (memória + estimativa) ou por
skills que existem (`/north-learn`, `/north-review`). O valor está em **conectá-las à tese** e em
**3-4 peças genuinamente novas** (§2), não em começar do zero.

---

## 2. O que é genuinamente novo (e como cabe nas fundações)

### 2.1. Handoff/Resume de sessão (#2)
Memória de continuidade: ao pausar, registra **o que eu tentava, o que falhou, o próximo passo**
(e o estado do que estava editando). Na volta, `/north-resume` entrega como contexto inicial —
**para a IA e para você** (segunda de manhã após 3 dias). O que o motor consegue **derivar
read-only** (git): working tree, branch, últimos commits, arquivos tocados. O que precisa de
**cognição/confirmação** (a IA escreve, você confirma): "o que eu tentava / o que não funcionou /
próximo passo". Guarda em `~/.north` (ou projeção em arquivo — ver §3). É um **caso do sistema de
memória** ([[north-memory-research-direction]]), não um subsistema novo.

### 2.2. Detector de dependência da IA (#4) — o mais original e o mais delicado
Espelho, não julgamento: ao longo do tempo, que **tipos de problema** você para e pede ajuda vs
resolve sozinho. É a métrica que materializa a tese §0. **Mas tem dois problemas honestos:**
- **Viabilidade de medição:** o north **não observa** sua sessão de IA sozinho. Ele infere de
  sinais — co-author em commits, ledger de insights/learn, ou sinal explícito (um hook). Precisa
  decidir **de onde vem o dado** (ver Q-G3). Sem isso, vira chute.
- **Espelho ≠ vigilância:** no **Solo** é um espelho **do dev, para o dev** (ótimo). No
  **Teams/Enterprise** isso **não pode** virar métrica de gestor — seria a vigilância que a visão
  promete não ser. Guardrail: **dado do dev, controlado pelo dev**; nunca exposto ao gestor sem
  consentimento explícito. É o princípio "crescimento, não monitoramento" ([[north-learning-cert-layer]]).

### 2.3. Calibração estimativa-vs-real (#6)
Estende a estimativa do estudo de sprint: pede uma estimativa **na criação da task**, mede o
**real** (gap início→conclusão via git), e aprende seu **fator de otimismo** por tipo de task
("frontend: você estima 2h, leva 6h"). Aparece como calibração na próxima estimativa, **sem
julgamento**. Guardar a estimativa em `~/.north` (motor read-only sobre o plano). **Folda na §5
do estudo de sprint**, não é feature separada.

### 2.4. Projeções legíveis da memória: DECISIONS.md / CONTEXT.md (#1, #5)
São **duas faces da mesma coisa**: a memória `project` projetada em **arquivos legíveis** que
servem de (a) contexto inicial pra IA, (b) briefing de 15 min pra um colega, (c) âncora pro dev
manual. `DECISIONS.md` = o *porquê* das escolhas; `CONTEXT.md` = stack/convenções/entidades/"não
faça isso porque". Candidatos a **novos tipos do `north-doc`** (`decisions`, `context`),
gerados/atualizados com confirmação. Decisão pendente: **onde gravam** (§3).

---

## 3. Tensões a resolver (Tech Lead não deixa passar)

- **T1 — Onde gravam (DECIDIDO: híbrido por tipo).** `DECISIONS.md`/`CONTEXT.md` → **no projeto**,
  via `north-doc` **confirma-pra-escrever** (versionados, viajam com o repo, contexto direto p/
  IA e colega). `handoff` de sessão → **em `~/.north`** (efêmero, pessoal, não viaja). **Nota de
  invariante:** escrever DECISIONS/CONTEXT no projeto **não exige carve-out novo** — segue o
  precedente já aceito do `north-doc` (escreve **arquivo novo com confirmação**; o invariante
  proíbe editar os *planos* do usuário em silêncio, não criar docs consentidos). Só o marker
  `.north` da [[north-discovery-enrollment]] (config de engine, silenciosa) é que pede o carve-out.
- **T2 — Espelho vs vigilância (#4).** Resolvido por princípio: Solo = espelho do dev; Teams =
  nunca métrica de gestor sem consentimento. Ratificar junto da decisão M7 (privacidade) do
  [[north-memory-research-direction]].
- **T3 — Viabilidade de medição (#4 e #6).** O north infere muito de git (commits, autoria,
  cycle-time) read-only — mas "pedi ajuda à IA" e "o que eu tentei" precisam de fonte explícita
  (hook/registro). Ser **honesto sobre o que é inferível vs o que precisa de sinal** — nunca
  fingir dado que não tem (mesma régua da estimativa: faixa + base).

---

## 4. Onde cada coisa aterrissa (sem doc novo pra cada ideia)

| Destino | Absorve |
|---|---|
| [[north-memory-research-direction]] (estudo de memória) | #1, #2, #4, #5, #7-perfil — todos são *memória* (projeto / sessão / cérebro do usuário) |
| Estudo de sprint §5 (estimativa) | #6 (calibração estimativa-vs-real) |
| Skills que já existem | #3 `/north-learn`, #7 `/north-review` — só ganham o gancho com o perfil |
| [[north-platform-vision]] | a **tese §0** como norte/headline |

Ou seja: o brainstorm **não cria 7 features** — ele **valida e enriquece 2 fundações + 2 skills**,
e dá ao produto um **norte**.

---

## 5. Prioridade recomendada (custo × valor × alcance)

1. **DECISIONS.md / CONTEXT.md (#1/#5)** — baixo custo, alto valor, **serve IA E dev manual**
   (alcance largo). Projeção da memória + tipo de doc. **Melhor primeiro passo "além do painel".**
2. **Handoff/Resume (#2)** — alto valor pra retomada; metade já é derivável do git.
3. **Calibração de estimativa (#6)** — entra de carona na estimativa já planejada.
4. **Dependência da IA (#4)** — o mais original e "vendável" da tese, mas **depende de resolver
   medição (T3) e o guardrail de vigilância (T2)**. Fazer por último, com cuidado.

---

## 6. Decisões em aberto (para o dono)

- **Q-G1 — Tese como norte: ✅ SIM, vira o headline do produto** (threadar no topo da visão).
- **Q-G2 — Projeções em arquivo (T1): ✅ híbrido por tipo** — DECISIONS/CONTEXT no projeto (via
  `north-doc`, confirma-pra-escrever, versionados); handoff de sessão em `~/.north` (efêmero).
- **Q-G3 — Fonte do dado de dependência (#4):** inferir de git/ledger (aproximado) ou exigir um
  sinal explícito (hook/registro de sessão)? quanto a IA pode/deve reportar?
- **Q-G4 — Dependência no Teams:** o espelho fica **só Solo** por ora (recomendado), ou já
  pensamos no caso empresa com consentimento do colaborador?
