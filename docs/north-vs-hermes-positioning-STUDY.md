# Estudo — north × Hermes: ferramenta viva, sim — mas qual camada?

> **Status:** estudo/design para discussão — nada aqui é compromisso de implementação.
> **Base:** north-cli v0.9.1 · **Data:** 2026-06-09 · **Autor:** Tech Lead (sessão north)
> **Origem:** dúvida do dono — "tô viajando em querer o north vivo, que aprende, que É o
> agente de IA, que pesquisa e faz o que puder, como o Hermes? Criar Solo e Team/Enterprise
> como o Hermes?" + o estudo do Squad Jedi (`agentes-ia-invista_1.pdf`).

---

## 0. Resposta direta: você NÃO está viajando — mas a pergunta certa é outra

A visão de **ferramenta viva que aprende** está **certa**, e o Hermes a **valida**: o recurso
nº1 que tornou o Hermes popular é exatamente **memória persistente + autoaperfeiçoamento** ("o
agente que não esquece quem você é"). É a mesma aposta do north (memória, [[north-growth-thesis]]).

**Mas há um fork de identidade — e é a coisa mais importante deste documento:**

> A pergunta não é *"o north vira um agente como o Hermes?"*.
> É *"o north vira a **CAMADA que governa os agentes** (inclusive o Hermes)?"*.

O Hermes **é um agente autônomo** (roda num servidor, executa comandos, tem poderes amplos na
máquina, auto-instala deps, multicanal). O north **é a camada que lê, lembra, governa e ensina
em cima de agentes** — read-only, local-first, stdlib, dentro do runtime (Claude/Codex/Gemini).
**São camadas diferentes.** Confundi-las é a armadilha.

---

## 1. Por que o north NÃO deve virar "um Hermes"

Se o north tentar **ser o agente autônomo** (executar, ter poderes amplos, auto-skills,
auto-install), ele:

- **Quebra o invariante read-only** ([[north-readonly-invariant]]) — execução autônoma = agir/
  escrever no ambiente do usuário.
- **Quebra stdlib-only / "motor não raciocina"** — precisaria *ser* ou embutir um LLM.
- **Herda toda a superfície de ataque do Hermes** — que o próprio estudo da Invista gasta **5
  páginas** dizendo ser **inadequada para ambiente financeiro/LGPD**: injeção de prompt via
  memória, skill maliciosa de marketplace, leitura ampla de arquivos (chaves/credenciais),
  fronteira de confiança do MCP, o padrão root/YOLO dos tutoriais.

Para um produto cuja bandeira é **"privacidade por design"** ([[north-platform-vision]]),
virar um agente autônomo de poderes amplos é andar **na direção oposta** da marca. O estudo
da Invista é literal: rodar o agente "cru" é **risco inaceitável**; o valor está em **arquitetar
em volta de dados hostis** — gateway separado da execução, não-root, aprovação ativa, memória
isolada. north não quer estar do lado "execução"; quer estar do lado **governança**.

---

## 2. O reframe: north é a CAMADA que o próprio estudo da Invista pede

O estudo do Squad Jedi, na **seção 05**, diz que vários agentes por setor **só funcionam com
uma camada acima deles** para *visualizar, governar e controlar custo* — senão viram
"caixas-pretas espalhadas". Essa camada tem três funções concretas — e **todas são o north**:

| O que o estudo pede (seção 05) | Como o north já é/seria isso |
|---|---|
| **Dashboard de custo por setor** | north é painel multi-projeto; estende p/ custo de IA por projeto/setor |
| **Gestão de artefatos persistentes** (docs "se perdem no chat"; repositório central, auditável, versionado) | **north JÁ detecta/linka docs read-only** (PRD/SDD/ADR… e agora CONTEXT/DECISIONS). É exatamente "o que o agente produziu e quando", rastreável |
| **Delegação de modelo por tarefa** (modelo caro só onde precisa) | observabilidade de qual runtime/modelo fez o quê |

E a **Rota C (Híbrido)** do estudo descreve o north quase ao pé da letra: *"usar o Hermes como
camada de planejamento e aprendizado (memória, skills) sobre ferramentas que a empresa já
controla"*. north é essa **camada de aprendizado + governança**, agnóstica de agente —
funciona sobre Claude Code, Codex, Gemini **e** um Hermes endurecido.

> ⛔ **O que o estudo manda NÃO replicar — e o north também recusa:** o "dreaming" (um agente
> varrendo autônomo, sem supervisão, todo o seu histórico entre plataformas). Em ambiente
> regulado é a superfície de risco a evitar. A memória/pesquisa do north é **opt-in, escopada,
> com aprovação** — nunca autônoma e transversal sem consentimento (M1/M3/M7 do
> [[north-memory-research-direction]]).

---

## 3. north × Hermes, camada por camada

| Camada | Hermes | north |
|---|---|---|
| **Inteligência (LLM)** | provider-agnostic, ele orquestra o modelo | **não é LLM**; vive dentro do runtime que o usuário já usa |
| **Execução / ações** | autônoma, poderes amplos na máquina | **read-only**; quem executa é o runtime/o humano (com aprovação) |
| **Memória** | MEMORY.md/USER.md **bounded** + FTS5 + extração na conversa + auto-skills | mesma filosofia (bounded, curada) — ver §4. north ADOTA o padrão |
| **Governança/observabilidade** | precisa de painel externo (a comunidade criou) | **é isso nativamente** (painel, custo, artefatos auditáveis) |
| **Postura** | self-hosted, sem telemetria (mas poderes amplos) | local-first, read-only, stdlib, privacidade por design |
| **Público** | quem quer um agente que age 24/7 | quem quer **entender, governar e crescer** sobre o que os agentes fazem |

**Conclusão:** não competir com o Hermes na camada de execução. **Complementar**, sendo a
camada de memória + governança + aprendizado **por cima** dele e dos outros agentes.

---

## 4. Hermes é um presente para o design de memória do north

O modelo de memória do Hermes resolve, na prática, a **maior lacuna técnica** que tínhamos em
aberto (M5 — dedup/decay, [[north-memory-research-direction]]):

- **Teto de tamanho intencional** em `MEMORY.md`/`USER.md` → **força curadoria**, remove o
  irrelevante, evita o "inchaço" que deixa agentes lentos. (É exatamente o "bounded" que o
  ledger do north já mirava — a nota antiga dizia *"ledger estilo Hermes — bounded"*.)
- **Extração durante a conversa**, não só no fim. → north pode capturar no fluxo, não só no wrap-up.
- **Busca full-text (FTS5) + sumarização por LLM** sobre histórico. → recall do north.
- **Skills auto-geradas** (memória procedural: tarefa resolvida vira skill reutilizável). →
  north poderia, com confirmação, transformar um padrão repetido numa skill/atalho.

É **MIT, auditável e forkável** — referência legítima para ancorar (não copiar) o design.
**Decisão derivada:** M5 (dedup/decay) adota o padrão "teto + curadoria" do Hermes.

---

## 5. Solo + Team/Enterprise "como o Hermes"? Sim, mas com OUTRO wedge

A demanda enterprise é real (o estudo confirma: agente por setor é "aposta acertada") — **mas
gated por segurança**. O erro seria o north entrar como **"mais um agente por setor"** (o jogo
do Hermes, lotado e arriscado). O wedge do north é o que o estudo diz que **falta**:

- **north Solo** — já é o dev individual; ganha memória/aprendizado vivo (o que o Hermes
  provou ser o killer feature), mas read-only e sem virar executor autônomo.
- **north Teams/Enterprise** — **a camada de governança de uma org cheia de agentes**: custo de
  IA por setor, **repositório auditável e versionado de artefatos** (o que o estudo diz ser
  *requisito de governança, não luxo*), memória isolada por setor, visibilidade de qual
  agente/modelo produziu o quê. Casa com a arquitetura endurecida (seção 09) **sem o north ser
  o ponto de execução** — ele é o ponto de **auditoria e aprendizado**.

Isso é **mais defensável** que competir com frameworks de agente: ninguém está fazendo a camada
de *observabilidade + aprendizado + governança, com privacidade por design*, sobre o trabalho
real dos agentes. É a tese de [[north-platform-vision]] aplicada a um mundo multi-agente.

---

## 6. Decisão para o dono

- **D-H1 — Identidade:** confirmar que o north é a **camada de governança/memória/aprendizado
  sobre agentes** (read-only), **não** um agente autônomo de execução estilo Hermes. (recomendo
  **sim** — preserva invariante, marca e diferencial; e é o que o estudo da Invista pede.)
- **D-H2 — Hermes como referência de memória:** ancorar o design de memória (M5 dedup/decay +
  extração no fluxo + skills auto-geradas com confirmação) no padrão Hermes (MIT). (recomendo **sim**.)
- **D-H3 — Wedge enterprise:** o Teams/Enterprise é a **camada de governança multi-agente**
  (custo/setor + artefatos auditáveis + memória isolada), **não** "um agente por setor". (recomendo **sim**.)
- **D-H4 — Interop com Hermes:** tratar um Hermes endurecido como **mais um agente que o north
  observa/governa** (como já faz com Claude/Codex/Gemini), não como concorrente. (em aberto: prioridade.)

> Se as 3 primeiras forem "sim", isto **reforça** tudo que já decidimos (memória, pesquisa
> opt-in, tese de crescimento, dois produtos) — só dá um **nome de camada** preciso ao north e
> impede a deriva de identidade para "agente autônomo". Threadar em [[north-platform-vision]].
