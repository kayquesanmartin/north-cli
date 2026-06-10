---
name: north-doc
description: north — Gera docs de SDLC (PRD, SPEC, SDD, TDD, ADR, SECURITY), docs vivos (CONTEXT, DECISIONS) e planos de sprint (Sprint*.md lido pelo kanban) ancorado no contexto real do projeto e na biblioteca de referências. A IA redige sob sua direção; o motor é read-only. Ative para "/north-doc", "gera o PRD", "escreve a spec", "cria um ADR", "documenta a arquitetura (SDD)", "plano de testes (TDD)", "modelo de ameaças", "cria o CONTEXT", "registra a decisão (DECISIONS)", "planeja o sprint", "quebra em tasks (sprint)".
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, WebSearch, WebFetch
argument-hint: "<tipo> [alvo]   ex.: spec checkout | adr \"escolha do banco\""
---

# /north-doc — Fábrica de documentos de SDLC

Ajuda a **criar e manter** os artefatos de engenharia (PRD · SPEC · SDD · TDD · ADR ·
SECURITY) com qualidade consistente. **A IA redige; você dirige.** O motor do north é
**read-only** — quem escreve o arquivo é você (a IA), com o consentimento do usuário.

## Espinha spec-driven (4 fases → docs do north)
Os docs daqui não são avulsos: formam a espinha **Specify → Design → Tasks → Execute**,
calibrada pela complexidade (auto-sizing — pule o que a feature não pede).

| Fase | Doc/skill do north | Quando |
|------|--------------------|--------|
| **Specify** | `prd` (por quê) + `spec` (o quê, AC testáveis) | sempre (Médio+) |
| **Design** | `sdd` (como) | só Grande/Complexo |
| **Tasks** | `sprint` (Sprint*.md lido pelo kanban) | Médio+ |
| **Execute** | `/north-dev` (TDD-first, usa SPEC/TDD) | sempre |

**Antes do PRD, sabatine:** rode **`/north-grill`** para furar a ideia, dimensionar a
complexidade e resolver as gray-areas. O PRD nasce dessa sabatina (seção "Decisões da
sabatina" do template) — não de um chute. Durante o dev, re-sabatine e **atualize** PRD/SPEC/
Sprint (idempotente). **Rastreabilidade:** requisitos do PRD ganham **ID** (RF-/RNF-) que
descem aos critérios de aceite do SPEC (AC-N) e às tasks do Sprint.

## Tipos
**SDLC:** `prd` (por quê/para quem) · `spec` (o quê — contrato) · `sdd` (como — design) ·
`tdd` (plano de testes) · `adr` (decisão) · `security` (ameaças/controles).
**Vivos** (briefing + memória do projeto, gravados na **raiz**, viajam com o repo):
`context` (briefing de 15 min: stack/versões, convenções, entidades, "não faça isso porque") ·
`decisions` (log vivo do **porquê** das escolhas — mais leve que ADR). Servem de **contexto
inicial** pra uma sessão de IA e pro dev manual. Um por projeto/unidade de rastreio.
**Planos:** `sprint` — gera um `Sprint*.md` **no `plan-build/`** (um por feature/microsserviço),
no formato que o **painel lê de volta** (vira kanban + contrato de cada task). Quebra em tasks a
partir dos docs (PRD/SPEC). Ver o fluxo dedicado abaixo.

Sem tipo? Mostre os gaps do projeto e pergunte qual:
```bash
python3 ~/.north/run.py doc list        # detectados vs faltando, por projeto
# Windows: python "%USERPROFILE%\.north\run.py" doc list
```

## Fluxo (por doc)
1. **Contexto (read-only):** entenda o projeto e os docs irmãos já existentes.
   - `python3 ~/.north/run.py doc list` (o que já existe / falta).
   - Leia com Read os planos/docs relacionados (um **SDD** lê o PRD/SPEC; um **TDD** lê o SPEC;
     um **ADR** lê o contexto da decisão). Use `north library find "<tema>"` e cite princípios.
2. **Pegue o esqueleto** do tipo:
   ```bash
   python3 ~/.north/run.py doc template <tipo>
   ```
   (Esqueletos em `references/doc-templates/`. Siga as seções; não invente estrutura.)
3. **Entrevista curta:** pergunte SÓ o que não dá pra inferir do projeto (não interrogue).
4. **Rascunhe** preenchendo o template com o contexto real + padrões do projeto.
   Diagramas em **Mermaid** (SDD/UML). Cite as referências consultadas no rodapé.
5. **Revisão guiada (checklist do tipo):**
   - SPEC: cada critério de aceite é **testável e inequívoco**.
   - SDD: respeita a regra de dependência (Clean Arch); alternativas registradas.
   - TDD: um caso por critério de aceite do SPEC; cobre bordas/negativos.
   - SECURITY: cobre OWASP Top 10 + LGPD; checklist de saída.
   - ADR: decisão + alternativas + consequências; status/data.
6. **Grave onde o usuário decidir** (confirme o caminho):
   - SDLC (prd/spec/sdd/tdd/adr/security): ao lado dos planos — `plan-build/<TIPO>-<alvo>.md` (ou `docs/`).
   - **Vivos (context/decisions): na RAIZ do projeto** — `CONTEXT.md` / `DECISIONS.md` (ou `docs/`),
     **um por projeto**, pra ficarem visíveis e versionados (o painel os detecta na raiz/docs).
   - **Idempotente:** se já existe, **atualize** preservando o que é válido; não duplique.
     `DECISIONS.md` é append vivo (decisão nova no topo); `CONTEXT.md` é mantido enxuto e atual.
   - Cross-link: SDD referencia PRD/SPEC; TDD referencia SPEC; mencione ADRs. O `/north-wrap-up`
     pode propor atualizar `CONTEXT.md`/`DECISIONS.md` quando surgir convenção/decisão nova.

## Fluxo do `sprint` (planejar a partir dos docs)
Depois dos docs, o `/north-doc sprint` ajuda a **quebrar o trabalho em um sprint** que o painel
lê de volta (kanban + contrato de cada task):
1. **Ancore nos docs:** leia o **SPEC** (se houver) ou o PRD/SDD para derivar o escopo. A IA
   **propõe** a quebra em tasks; o usuário ajusta.
2. **Esqueleto:** `python3 ~/.north/run.py doc template sprint` — siga o formato (Meta/Objetivo,
   tabela de tasks, contrato `Builder entrega:`/`Evaluator valida:`, DoD, pré-leitura).
3. **Convenções (lidas pelo painel):** status válidos `Planejado · Em Andamento · Código
   Completo · Concluído · ⛔ Bloqueada` (impedimento é **flag**, não coluna); **tags de
   disciplina** no início da descrição (`[ANALISE] [API] [FRONTEND/UI/UX] [PESQUISA]` — sugerem o
   squad). Cada `Evaluator valida:` deve ser **testável**. **DoD:** uma task só vai a `Concluído`
   após **testes + code-review**.
4. **Grave em `plan-build/`** (ou `plan-build/<feature>/`), **um por feature/microsserviço** —
   nunca dois competindo na mesma unidade. Confirme o caminho. Idempotente: atualize sem duplicar.
5. **Estimativa de prazo:** não chute — o north aprende do histórico real (git + ledger). Ofereça
   faixa honesta quando houver amostra; senão, diga que é palpite fraco.

## Encadeamento natural
**`/north-grill`** (sabatina + auto-sizing) → PRD → SPEC → (SDD + TDD) → **sprint** (quebra em
tasks) → código (`/north-dev`, TDD-first usa o SPEC/TDD) → SECURITY/ADR conforme decisões.

## Regras de ouro
- **Read-only sobre os planos do usuário** no nível do MOTOR; o arquivo novo é escrito por
  você (IA) **com confirmação** do usuário, no caminho que ele aprovar.
- **Ancore, não invente:** contexto real do projeto + biblioteca/doc oficial, com citação.
- Conciso e específico ao projeto — nada de doc genérico de template vazio.
