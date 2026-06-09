# Estudo — Sistema de Memória + Pesquisa do north

> **Status:** estudo/design para discussão — nada aqui é compromisso de implementação.
> **Base:** north-cli v0.9.1 · **Data:** 2026-06-09 · **Autor:** Tech Lead (sessão north)
> **Objetivo:** desenhar como o north **aprende** (do usuário e do desenvolvimento), **pesquisa**
> (que fontes, além das referências do usuário), e **cria/guarda memórias sobre tudo que importa**
> — unificando o que hoje são 3 ilhas separadas, sem quebrar local-first / read-only / stdlib.

---

## 0. Resposta à pergunta do dono: "já travamos isso?"

**Não.** Existem hoje **três surfaces de memória separadas e estreitas**, e **nenhuma pesquisa**
(o motor não faz chamada de rede; o único `fetch` é `git fetch` p/ sync awareness):

| Surface | Arquivo | Guarda | Limite |
|---|---|---|---|
| **Ledger** | `learnings.py` | decisões/bug/padrão/gotcha por projeto (JSONL) | append; sem dedup/decay; só por projeto |
| **Taught** | `insights.py` | conceitos ensinados por linguagem + agendador (repetição espaçada) | só conceitos de código |
| **Library** | `library.py` | referências consultáveis (keyword search, sem ML) | passivo; só o que o usuário trouxe |

**O princípio que já está no código** (`insights.py`): *"o north NÃO detecta conceitos — quem
identifica e ranqueia é a IA do runtime; este motor é a MEMÓRIA e o AGENDADOR."* O sonho do dono
é **generalizar esse princípio** numa coisa só.

---

## 1. Princípio (a régua que não muda)

**O motor é a MEMÓRIA + o ORQUESTRADOR; a IA do runtime é a COGNIÇÃO (pesquisa + raciocínio).**

- O north (stdlib) **não** crawleia a web nem roda ML; é **offline por default** e qualquer
  fetch do motor é **opt-in + transparente** (M1). Ele **decide o que lembrar, quando relembrar,
  e como organizar** — e **pede** à IA que pesquise/redija, guardando o resultado com proveniência.
- Tudo read-only sobre o código/planos do usuário; escreve só na casa dele (`~/.north`).
- **Memória ≠ "tudo".** "Salvar memória sobre tudo que for necessário" tem que ser **bounded**:
  salva o que é **não-óbvio e reutilizável**; **não** salva o que git/repo já registram; triagem
  na captura; corrige/expira o que envelhece. "Necessário" ≠ "tudo" — senão vira ruído + risco.

**Precedente provado (dogfooding):** o sistema de memória de um agente de código (frontmatter
`type: user|feedback|project|reference` + um `MEMORY.md` índice + links `[[nome]]`) é exatamente
o modelo-alvo. Não inventar; adotar o que já funciona.

---

## 2. Modelo de memória unificado (funde as 3 ilhas)

Um formato só, com **tipos** (herda o ledger/taught/library como casos particulares):

| Tipo | O que é | Hoje |
|---|---|---|
| **user** | perfil: nível (jr→sr), stack, preferências de trabalho | espalhado em config; não é memória |
| **feedback** | como o usuário gosta que se trabalhe (correções, padrões aprovados) | **não existe** — lacuna |
| **project** | decisões/ADRs/padrões/gotchas de um projeto | = Ledger (`learnings.py`) |
| **concept** | o que já foi ensinado (e o nível) | = Taught (`insights.py`) |
| **reference** | ponteiros pra fontes (lib do usuário, docs oficiais, links) | = Library (`library.py`) |

- **Índice de recall** (estilo `MEMORY.md`): uma linha por memória pra decidir relevância rápido,
  sem carregar tudo. Stdlib (JSONL + um índice .md/.json).
- **Links** entre memórias (`[[slug]]`) pra navegar contexto relacionado.
- **Escopo duplo:** memórias **por projeto** *e* um **"cérebro do usuário" cross-project**
  (seu nível, suas pegadinhas recorrentes em qualquer projeto, suas preferências). Hoje só há o
  por-projeto.

### Ciclo de vida da memória
`capturar (triagem/confirma) → guardar (estruturado, dedup) → relembrar (contextual: morning/
focus/dev) → atualizar/superseder (corrige o errado, expira o obsoleto) → esquecer (decay)`.

Hoje só temos *capturar* (append) e *relembrar*. **Faltam dedup, correção e decay** — sem isso a
memória apodrece. É a maior lacuna técnica.

---

## 3. Pesquisa: quem faz, e que fontes (a pergunta do dono)

**Quem faz:** a **IA do runtime** (tem web search, docs oficiais/vendor, context7…). O motor
**orquestra e guarda** — não busca sozinho.

**Hierarquia de fontes (ordem de confiança):**
1. **Memória do próprio north** — *checa primeiro*; se já aprendeu, não re-pesquisa.
2. **Library/referências do usuário** (já faz, citando) — o que você curou tem prioridade.
3. **Compêndio bundlado** (`references/compendium/`) — princípios curados.
4. **Docs oficiais / vendor** (context7, docs da Microsoft, AWS/OCI…) — autoridade.
5. **Web aberta** — **opt-in**, **sempre citada**, **nunca confiada cega** (verificação
   adversarial, estilo deep-research: refutar antes de aceitar). É a fonte "além das que você
   colocou" que você perguntou.

**Proveniência obrigatória:** toda memória pesquisada carrega **fonte + data + confiança**.
Claim da web sem verificação não vira "fato". É a espinha anti-alucinação (human-in-the-loop).

**Postura de rede (DECIDIDO — M1):** o **motor pode** fazer fetch, mas **opt-in e transparente**
(desligado por default; um `north research`/modo explícito liga; um log mostra **exatamente o que
saiu**, estilo `north sync status`). Continua **não sendo crawler nem ML** — fetch pontual via
`urllib` (stdlib), sempre com proveniência. A maior parte da pesquisa ainda é da IA; o motor busca
só quando faz sentido (ex.: refrescar um doc cacheado, validar um link). **Salvaguardas:** opt-in
radical, transparência do tráfego, LGPD/minimização (guardar resumo/conceito, não payload cru — M7),
nada quebra o "100% local por default".

---

## 4. Onde isto vive (e por que é a fundação de tudo)

| Camada | Natureza | Casa |
|---|---|---|
| Memória local (capturar/guardar/relembrar) | escreve só em `~/.north` | `north-cli` |
| Pesquisa (IA pesquisa, motor guarda c/ proveniência) | IA externa + motor offline | `north-cli` + runtime |
| Sync de memória pra nuvem | **stream de consentimento próprio** (não junto do metadado) | **plataforma** (Solo) |
| Flywheel longitudinal / agregação | nuvem | **plataforma** |

**Memória é o substrato dos outros features já decididos:**
- a **estimativa aprendida** (estudo de sprint §5) *lê* memória de cycle-time/gotchas;
- a **plataforma de aprendizado + cert** ([[north-learning-cert-layer]]) é *construída sobre*
  memória — trilhas e prova saem do que foi aprendido/registrado;
- o **diferencial defensável** da visão ([[north-platform-vision]]) — "aprender do trabalho
  real" — **é** o ledger longitudinal de memória. **Sem memória boa, não há moat.**

Cross-links: [[north-learning-ledger]] · [[north-readonly-invariant]] · [[north-sprint-planning-direction]].

---

## 5. Decisões (DECIDIDAS em 2026-06-09 + em aberto)

**Fechadas com o dono:**
- **M1 — Rede no motor: ✅ o motor PODE fazer fetch, opt-in e transparente** (não offline-puro).
  Implica: modo de pesquisa explícito + log do que saiu + `urllib` stdlib + salvaguardas de
  privacidade (ver §3 e M7). Não vira crawler/ML.
- **M2 — Escopo: ✅ projeto + "cérebro do usuário" cross-project** (perfil/nível/pegadinhas
  recorrentes além das memórias por projeto).
- **M3 — Captura: ✅ triagem por default + auto-save só de baixo risco** e proveniência clara
  (ex.: conceito ensinado entra sozinho; decisão/gotcha pede confirmação).
- **M4 — Web como fonte: ✅ permitida, mas opt-in (off por default), sempre citada e verificada**
  (decorre do M1).

**Ainda em aberto:**
- **M5 — Dedup/decay:** quão agressivo? superseder no conflito; expirar após N dias sem uso;
  marcar "stale" e pedir reconfirmação? (é a maior lacuna técnica — §2.)
- **M5 — Dedup/decay:** quão agressivo? superseder no conflito; expirar após N dias sem uso;
  marcar "stale" e pedir reconfirmação? (é a maior lacuna técnica — §2.)
- **M6 — Sync de memória:** memória sobe pra nuvem (Solo) como **stream de consentimento próprio**
  (recomendado, alinhado à tensão #2 da visão) — confirma?
- **M7 — Privacidade do conteúdo:** memória pode conter trechos de código/decisões sensíveis.
  Guardar **resumo/conceito** em vez do código cru? Redação/minimização por default?

---

## 6. Proposta de implementação faseada (quando o design fechar)

| Fatia | Entrega | Risco |
|---|---|---|
| **M-A** | Modelo de memória unificado + índice + tipos (funde ledger/taught/library por baixo) | médio |
| **M-B** | Dedup + correção + decay (curar a memória, não só acumular) | médio |
| **M-C** | "Cérebro do usuário" cross-project (perfil/nível/pegadinhas) | médio |
| **M-D** | Protocolo de pesquisa (hierarquia de fontes + proveniência + verificação), IA-driven | médio |
| **M-E** | Web search opt-in como fonte, citada e verificada | médio |
| **M-F** | (plataforma) sync de memória (stream próprio) + flywheel agregado | alto |

**Sequência:** fechar M1–M7 → M-A → M-B → (M-C ∥ M-D) → M-E → M-F (plataforma).

> Tudo respeita: motor stdlib/offline-by-default, read-only sobre código/planos, IA faz a
> cognição, memória bounded e com proveniência, privacidade por design.
