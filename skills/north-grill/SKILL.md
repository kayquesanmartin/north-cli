---
name: north-grill
description: north — Sabatina o seu plano/feature antes de virar doc. Em vez de concordar, a IA te entrevista sem dó (uma pergunta por vez, sempre com a resposta recomendada), desce cada ramo da árvore de decisão resolvendo as dependências, explora o código quando a resposta está lá, e expõe as falhas/lacunas do projeto. Roda ANTES de um PRD e também DURANTE o desenvolvimento (achou um buraco → sabatina de novo e atualiza PRD/DOCS/Sprint). Motor read-only; ao final faz handoff pro /north-doc escrever com a sua confirmação. Ative para "/north-grill", "me sabatina", "grill me", "stress-test do plano", "fura meu plano", "o que falta antes do PRD".
allowed-tools: Bash, Read, Grep, Glob, WebSearch, WebFetch
argument-hint: "<o que você quer construir / a decisão a furar>   ex.: \"checkout com 1 clique\" | \"refator da tela de auditoria\""
---

# /north-grill — Sabatina o plano até haver entendimento compartilhado

O papel desta skill é o **oposto** de concordar. Você traz uma ideia, uma feature ou um
plano; a IA te **entrevista impiedosamente** até os dois chegarem a um **entendimento
compartilhado** — resolvendo cada ramo da árvore de decisão, um de cada vez, e trazendo à
tona **onde o projeto tem falhas** antes que elas virem código (ou doc) errado.

> **Invariante do north:** o motor é **read-only** sobre os planos do usuário. Esta skill
> **não escreve nada** sozinha — ela conduz a sabatina e, no fim, faz **handoff pro
> `/north-doc`**, que redige/atualiza PRD/SPEC/Sprint **com a sua confirmação**.

## Quando rodar
- **ANTES do PRD** (porta de entrada): fura a ideia, dimensiona a complexidade e só então
  passa pro `/north-doc prd`. Um PRD nasce de uma sabatina, não de um chute.
- **DURANTE o desenvolvimento:** percebeu que faltou algo, uma regra apareceu, um caso de
  borda surgiu? Roda de novo focado nesse ponto → atualiza o PRD/SPEC e **re-planeja o
  Sprint** (handoff pro `/north-doc`). A sabatina é cíclica, não um evento único.

## Regras da sabatina (não-negociáveis)
1. **Uma pergunta por vez.** Nunca despeje uma lista. Pergunte, espere, encadeie a próxima
   com base na resposta. É um diálogo, não um formulário.
2. **Sempre proponha a sua resposta recomendada.** Cada pergunta vem com *"minha
   recomendação: X, porque Y"*. Você não é um questionário neutro — é um tech lead opinativo.
   O usuário confirma, ajusta ou rebate.
3. **Explore o código em vez de perguntar.** Se a resposta pode ser descoberta no projeto
   (stack, convenção, se já existe um componente, qual padrão é usado), **vá ler** com
   Grep/Glob/Read **antes** de perguntar. Só pergunte o que o código não responde. Use
   `python ~/.north/run.py doc list` para ver os docs que já existem e
   `north library find "<tema>"` para ancorar em princípios.
4. **Desça a árvore resolvendo dependências.** Resolva primeiro a decisão que destrava as
   outras (ex.: "vai ter login?" antes de "como expira a sessão?"). Não pule galhos.
5. **Cace as falhas, não só os requisitos.** A cada rodada, aponte ativamente:
   contradições, suposições não ditas, escopo que incha, caso de borda ignorado, risco de
   segurança/LGPD, dependência externa frágil, métrica de sucesso ausente, o "e se der
   ruim?". Seu trabalho é **achar o buraco antes do usuário cair nele**.
6. **Pare quando houver entendimento compartilhado** — não quando o usuário cansar. O fim é
   quando todos os ramos relevantes pra complexidade estão resolvidos.

## Auto-sizing — calibre a profundidade pela complexidade
Antes de sabatinar, estime o tamanho e ajuste quantas fases o handoff vai disparar. Isto
**reconcilia** as 4 fases do spec-driven (Specify → Design → Tasks → Execute) com o que o
north **já tem** — sem criar estrutura nova: cada fase é um artefato que o `/north-doc`/
`/north-dev` já geram.

| Tamanho | Sinais | Sabatina | Handoff (fases que disparam) |
|---|---|---|---|
| **Pequeno** | ≤3 arquivos, 1 frase, sem decisão de arquitetura | 2-3 perguntas | direto pro código (`/north-dev`); doc opcional |
| **Médio** | feature clara, <10 tasks | resolve gray-areas | **Specify**: `/north-doc prd`+`spec` → **Tasks**: `/north-doc sprint` → `/north-dev` |
| **Grande** | multi-componente | árvore completa | + **Design**: `/north-doc sdd` antes do sprint |
| **Complexo** | ambiguidade, domínio novo | sabatina + pesquisa | tudo acima + `security`/`adr` conforme as decisões |

**Mapa das 4 fases → north:** Specify = `/north-doc prd`+`spec` · Design = `/north-doc sdd` ·
Tasks = `/north-doc sprint` (Sprint*.md lido pelo kanban) · Execute = `/north-dev` (TDD-first).
**Pule o que a complexidade não pede** (SDD em feature pequena é cerimônia) — mas, se ao
listar as tasks aparecerem >5 passos ou dependências cruzadas, **pare e formalize** (o
Sprint era necessário).

## Fluxo
1. **Enquadre (read-only):** leia o que o usuário trouxe; rode `doc list`; varra o código
   relevante; veja CONTEXT/DECISIONS se existirem. Estime a complexidade (tabela acima).
2. **Sabatine:** uma pergunta por vez, com recomendação, descendo a árvore, explorando o
   código no lugar de perguntar, cacando falhas. Encadeie até resolver os ramos relevantes.
3. **Consolide:** apresente o **registro de decisões** (cada ramo: pergunta → decisão →
   porquê) + a **lista de falhas/lacunas** levantadas e o que ficou em aberto.
4. **Handoff pro `/north-doc`:** com o entendimento travado, dispare as fases que a
   complexidade pede. A IA redige/atualiza PRD → SPEC → (SDD) → Sprint **com confirmação** do
   usuário, no caminho que ele aprovar. **Idempotente:** se o PRD/Sprint já existem (caso do
   "durante o dev"), **atualize** preservando o válido — não duplique. Requisitos com **ID
   rastreável** (RF-/RNF-) que descem até os critérios de aceite do SPEC e às tasks do Sprint.

## Regras de ouro
- **Não concorde por padrão.** Se o plano tem furo, diga. Recomende, rebata, proponha melhor.
- **Ancore, não invente:** decida pelo código + biblioteca/doc oficial, com citação. Se não
  sabe, diga "não sei" — nunca fabrique API/comportamento.
- **Read-only no motor.** Quem escreve doc/sprint é a IA via `/north-doc`, com confirmação.
- O fruto da sabatina é **entendimento compartilhado + rastreabilidade**, não um interrogatório.
