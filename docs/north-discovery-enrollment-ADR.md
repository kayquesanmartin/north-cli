# ADR — Modelo de descoberta de projetos: enrollment opt-in (não auto-scan)

> **Status:** Aceito (direção) — 2026-06-09 · pendente de implementação.
> **Base:** north-cli v0.9.1 · **Decisor:** dono (Kayque) + Tech Lead.
> **Relacionado:** `docs/north-sprint-planning-STUDY.md` (§4.1 granularidade de `plan-build`),
> [[north-platform-vision]] (marker para Teams), [[north-readonly-invariant]].

---

## Contexto

Hoje o north descobre projetos por **auto-scan opt-out**: `scan_roots` aponta pastas e o motor
varre tudo, rastreando **todo** projeto com `plan-build/`/`.planning` (`discovery.py:33`,
`discover_projects` :678). Já existe config por-projeto (`enabled` default **True**, alias,
cor, ordem, source — `config.py:92-109`) e auto-cura de fantasmas. A instalação ainda **semeia
um `scan_root` default e já varre** no primeiro uso.

**Problema (relatado pelo dono):** o default "aparece tudo, você desliga o que não quer" gera
**bagunça** — projetos que ele não quer acompanhar entram no painel e, pior, vazam pro
`/north-morning` e `/north-wrap-up`. Ele quer **plugar o north no projeto** e ter um track
**direcionado**, só do que escolheu.

## Decisão

**Inverter o modelo para enrollment opt-in, híbrido, e tirar o scan do momento da instalação.**

1. **Um verbo só: `north init`** (rodado na raiz = "plugar o north neste projeto"). Default novo
   = `enrolled`. **Default do `north init` = registry em `~/.north`**: registra o **caminho
   absoluto** numa lista de enrolled no `projects.json`. O north passa a rastrear **apenas** o que
   foi plugado. **Nada é escrito dentro do projeto** → invariante read-only intacto.
2. **A instalação não varre mais.** Remove a semeadura do `scan_root` default + a auto-descoberta
   no install. Pós-install, o north começa **vazio** e ensina: *"rode `north init` na raiz do
   projeto que quer acompanhar"*. (Migração abaixo cobre quem já usa.)
3. **`north init --shared` (modo Teams) = marker `.north` no projeto.** A MESMA verb, com a flag,
   grava um `.north` versionado na raiz (como `.git`/`.vscode`) — **viaja com o repo**, então o
   time herda o tracking + o `board_profile`/taxonomia de tags do estudo de sprint. É a opção
   **futura, da fase Teams** ([[north-platform-vision]]); **só ela exige o carve-out do
   invariante** (ver Consequências). O `north init` puro (sem flag) nunca escreve no projeto.
4. **`discovery_mode` configurável: `enrolled` (default) | `scan` (legado).** Quem gosta do
   auto-scan mantém com um setting; não quebramos ninguém.
5. **Unidade de rastreio = unidade de `plan-build`.** O que você pluga define o board: plugar a
   raiz de um monorepo → um `plan-build` segregado por feature group (já existe); plugar cada
   microsserviço → um projeto cada. Resolve a §4.1 do estudo de sprint de forma unificada.

## Migração (não quebrar quem já usa)

- Na atualização, se houver `scan_roots`/projetos `enabled`, o north **oferece** (opt-in):
  *"encontrei N projetos já ativos — quer enrolar todos e mudar para o modo `enrolled`?"*.
- Quem recusar continua em `scan` (legado). Idempotente; nada é apagado sem confirmação.

## Consequências

**Positivas**
- `/north-morning` e `/north-wrap-up` passam a mostrar **só o que você plugou** — mata o ruído
  na origem (o pedido do dono).
- Track direcionado, previsível; install limpo (sem varrer o HD do usuário no primeiro uso).
- A unidade de enrollment unifica a granularidade de `plan-build` (§4.1).
- O marker futuro habilita o **enrollment compartilhado do Teams** sem retrabalho de modelo.

**Custos / riscos**
- É **um passo a mais** (plugar) — perde a mágica do zero-config. Mitiga com onboarding claro
  pós-install e com `north init` assumindo o diretório atual por default.
- **Invariante read-only — atenção ao `--shared` (item 3):** o `north init` puro (registry) é
  **limpo** (escreve só em `~/.north`). O **`--shared` grava o marker `.north` no projeto**,
  o que fere a *letra* do invariante (*"nenhuma feature pode escrever dentro dos projetos
  descobertos"* — CLAUDE.md §1). Posição: é **config de ferramenta do north** (como `.git`),
  escrita **só** sob `north init --shared` explícito, **nunca** toca os planos do usuário — fere a
  letra, não o espírito. **Quando o `--shared` for implementado**, ratificar um carve-out no
  CLAUDE.md ("o marker opt-in do north, criado só por `north init --shared`, não viola o
  read-only"). Até lá, **só registry**, e o invariante segue intacto.

## Touch points (quando implementar)

| Onde | O quê |
|---|---|
| `install.py` | parar de semear `scan_root` default + não auto-varrer; onboarding "rode `north init`" |
| `config.py` | `discovery_mode` (`enrolled`/`scan`); lista de **enrolled paths**; migração |
| `discovery.py` | em `enrolled`, restringir a descoberta aos paths plugados (não varrer `scan_roots`) |
| `cli.py` + skills | `north init` (registry; aceita o diretório atual) + `north untrack`/`north forget`; `--shared` (marker) na fase Teams; **paridade nos 3 runtimes** via CMDSPEC (nova entrada `init`) |
| `rituals.py` | morning/wrap-up já respeitam os projetos rastreados — passam a refletir os enrolled |

## Alternativas consideradas

- **Só registry (sem marker nunca):** mais simples e 100% invariante-limpo, mas o enrollment não
  viaja com o repo → ruim para Teams. Rejeitado como destino final; **adotado como Fase 1**.
- **Só marker no projeto:** "pluga de verdade" e viaja com o repo, mas escreve no projeto já no
  Solo e força a discussão do invariante cedo demais. Rejeitado como default inicial.
- **Manter auto-scan, só facilitar o opt-out:** menor esforço, mas mantém o ruído por default —
  não resolve a dor. Rejeitado.
