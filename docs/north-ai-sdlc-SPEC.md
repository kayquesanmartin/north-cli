# SPEC — north como copiloto de SDLC com IA

> Status: **DRAFT para aprovação** · Autor: tech-lead session · Data: 2026-06-08
> Escopo: evolução do north de "painel + rituais" para um copiloto que ajuda a
> **planejar, documentar, testar e aprender** ao longo do desenvolvimento com IA.

Este documento consolida o pedido original do #4 (fábrica de docs) + três ideias
novas: **TDD-first obrigatório**, **base de conhecimento curada** e **aprendizado
contínuo (estilo Hermes)**.

---

## 0. Invariantes que NADA pode violar (contrato do produto)

1. **READ-ONLY sobre os planos/código do usuário.** O *engine* (`src/painel/`) só
   lê. Toda **escrita** (docs, testes, código) é feita pela **IA do runtime** (skill),
   sob direção e consentimento do usuário — nunca pelo motor. O motor só escreve na
   casa dele (`~/.north`) e na inbox.
2. **Engine stdlib-only, Python 3.8+, zero dependências.** Sem vector DB, sem
   embeddings, sem ML no motor. "Conhecimento" e "aprendizado" = arquivos
   estruturados (md/json) + recuperação simples; a *inteligência* é da IA do runtime.
3. **IA-first, paridade multi-runtime.** Toda capability nova é skill nos 3 runtimes
   (Claude/Codex/Gemini) e registrada no `CMDSPEC`. Terminal é caminho secundário.
4. **Sem material protegido por copyright embutido.** Nada de texto de livros. Só
   princípios **destilados em linguagem própria** + links/ferramentas de doc oficial.

---

## Pilar A — Fábrica de docs (`/north-doc`)

Ajuda a **criar e manter** os artefatos do SDLC, ancorado no contexto real do projeto.

### Tipos
PRD · SPEC · SDD · **TDD** · SECURITY · UML (Mermaid) · SPRINT · ADR.

### Comando
- `/north-doc` → menu + detecta o que já existe no `plan-build/`.
- `/north-doc <tipo> [alvo]` → ex.: `/north-doc tdd checkout`, `/north-doc adr "banco"`.
- Terminal (read-only): `north doc list` — lista docs detectados por projeto.

### Fluxo (por doc)
1. **Contexto (engine, read-only):** reúne planos, stack, docs irmãos (SDD lê PRD/SPEC).
2. **Entrevista curta:** a skill pergunta só o que falta (infere o resto).
3. **Rascunho** seguindo template do tipo + padrões do projeto + princípios (Pilar C).
4. **Revisão guiada:** checklist de qualidade do tipo.
5. **Grava onde o usuário decidir** (default `plan-build/<tipo>-<alvo>.md`). Idempotente.

### Fatia segura imediata (read-only, sem gerador)
north **detecta e linka** PRD/SDD/TDD/SPEC/SECURITY existentes no painel + "pré-leitura"
no modal da sprint. (Os planos do usuário já têm esses arquivos — valor instantâneo.)

---

## Pilar B — TDD-first (sempre oferecer, testes antes)

**Regra de produto:** sempre que o usuário for desenvolver uma task, o north
**pergunta se quer codar com TDD** (default recomendado), e conduz o ciclo
**red → green → refactor** com os testes escritos **antes** do código.

### Por que casa com o que já existe
Os **critérios de aceite** que o north já extrai (`Evaluator valida:` / DoD) **são**
a fonte dos testes. O loop fica: SPEC/aceite → escrever teste que falha → implementar
até passar → refatorar. O dev fica preso ao teste e ao contexto real.

### Comando / gate
- Skill `/north-dev [task]` (ou gate no `/north-focus` e `/north-morning`):
  > "Vai mexer na S3B-2. Codar com **TDD**? (recomendado) — escrevo os testes a
  > partir dos critérios de aceite primeiro." [S/n]
- Se sim: a IA gera os testes a partir do aceite → roda (devem falhar) → guia a
  implementação → roda até verde → sugere refactor. Stack de teste detectada do projeto
  (xUnit/.NET aqui; pytest/jest conforme o repo).
- **Opt-out / config:** `north config set tdd_default off` (não nag). Default on.
- **Read-only:** os testes/código são escritos pela IA no projeto, com consentimento.

### As 3 leis do TDD (referência do Pilar C)
1. Não escreva código de produção sem um teste que falhe.
2. Não escreva mais do teste do que o suficiente para falhar.
3. Não escreva mais código do que o suficiente para passar.

---

## Pilar C — Base de conhecimento curada (princípios, não livros)

Moldar o "conhecimento" do north sem violar copyright nem o stdlib-only.

### O que entra
- `references/*.md` **destilados em linguagem própria**: SOLID, Clean Architecture
  (camadas/dependências), heurísticas de Clean Code (nomes, funções, comentários,
  duplicação), 3 leis do TDD, OWASP Top 10 resumido, LGPD essencial, 12-factor.
- Bundladas com as skills que usam (mentor, doc-factory, TDD, code-review).
- **Doc viva via plugins já habilitados:** context7 (libs), microsoft-docs (.NET/Azure).

### O que NÃO entra
- Texto de livros (Clean Code/Arch são protegidos). Nada de PDF/corpus pirateado.
- Vector DB / embeddings / RAG pesado no engine (fere stdlib-only). Se um dia precisar
  de busca semântica, fica num plugin/skill opcional, fora do motor.

### Como é usado
As skills **citam** o princípio relevante ao orientar (ex.: TDD cita as 3 leis;
doc-SDD cita as regras de dependência de Clean Arch; code-review cita heurísticas).

---

## Pilar D — Aprendizado contínuo (ledger por projeto, estilo Hermes — bounded)

north "aprende" enquanto você desenvolve — sem ML no motor.

### O que é
Um **ledger de aprendizado por projeto** em `~/.north/learnings/<projeto>.jsonl`
(casa do north — não viola read-only). Captura, conforme você trabalha:
- **Decisões** (o que/por quê) — alimenta futuros ADRs.
- **Bugs & fixes recorrentes** — "isso já quebrou antes; a causa foi X".
- **Padrões e convenções** descobertos no projeto.
- **Pegadinhas / gotchas** (ex.: "o proxy não envia X-User-Roles").

### Como captura (a IA escreve, o motor guarda)
- O `/north-wrap-up` já rascunha resumos — passa a também propor "aprendizados do dia".
- `/north-note` ganha tags `decisao|bug|padrao|gotcha` que roteiam pro ledger.
- Triagem como a inbox (nada entra sem curadoria — evita ruído).

### Como devolve (o valor)
- **Bom-dia/foco:** "lembrete: ao mexer em auth, o padrão do projeto é só X-Api-Key
  (gotcha registrado em 02/06)".
- **TDD/dev:** sugere casos de teste a partir de bugs passados ("já quebrou com CNPJ
  mascarado — cubra esse caso").
- **doc-factory:** ADR puxa as decisões já registradas.

### Limites honestos
- Não é agente autônomo; é memória estruturada + recuperação por projeto/tema.
- Complementa (não substitui) a memória do runtime; é **portátil entre runtimes** e
  **escopada ao projeto**. Stdlib: leitura/escrita JSONL + filtro simples.

---

## Sequenciamento proposto (incremental, cada fatia entrega valor sozinha)

| Fase | Entrega | Risco | Depende |
|---|---|---|---|
| **1** | A-fatia-segura: detectar+linkar docs existentes no painel | baixo | — |
| **2** | C: `references/` com princípios (SOLID/CleanArch/TDD/OWASP) | baixo | — |
| **3** | B: `/north-dev` TDD-first (gate + testes a partir do aceite) | médio | C |
| **4** | A-gerador: `/north-doc` (começa por SPEC, TDD, ADR) | médio | C |
| **5** | D: ledger de aprendizado (captura no wrap-up/note + devolve no morning) | médio | — |

Tudo respeita: engine read-only, stdlib-only/3.8, paridade 3 runtimes, sem copyright.

---

## Decisões (travadas com o dono em 2026-06-08)

1. **TDD default = ON**, com opt-out `north config set tdd_default off`. (Pilar B)
2. **Ledger = automático com triagem** (wrap-up propõe, nada entra sem confirmar). (Pilar D)
3. **Ordem de implementação:** **Fase 1 primeiro** (detectar + linkar docs no painel),
   depois 2 (references) → 3 (TDD-first) → 4 (gerador) → 5 (ledger).
4. _Em aberto:_ onde o `/north-doc` grava por padrão (`plan-build/` vs `docs/` vs perguntar)
   — decidir ao chegar na Fase 4.
