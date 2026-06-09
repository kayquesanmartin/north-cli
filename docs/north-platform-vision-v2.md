# north — Da CLI à Plataforma · Visão v2

> **Status:** proposta para discussão — nada aqui é compromisso de implementação.
> **Base:** north-cli **v0.9.1** · **Autor:** Tech Lead (sessão north) · **Data:** 2026-06-09
> **Antecede:** PDF `north-platform-vision.pdf` (v1, 2026-06-08) — esta v2 **incorpora pesquisa
> de mercado** e as camadas adicionadas pelo dono em 2026-06-09 (aprendizado, prova/cert,
> persona do dev manual). Confidencial.

---

## 0. O que mudou da v1 para a v2

A v1 (PDF) cravou a fundação: **local-first → nuvem opt-in, dois produtos (Solo + Teams/Enterprise),
open-core, stack alinhada ao time, roadmap em 5 fases.** Isso continua de pé.

A v2 muda **três coisas**, com base em pesquisa de mercado (fontes na §8):

1. **Reposiciona o diferencial.** "Derivar sprint/kanban do trabalho real" **não** é diferencial
   forte — Jellyfish/LinearB/Swarmia já fazem isso a partir de git+PM. O diferencial real e
   **ownable** é o **loop de aprendizado a partir do trabalho real**: Workera e Pluralsight
   **explicitamente não capturam skill do trabalho real, só de avaliações formais.** Ninguém
   transforma "o que você codou + o que a IA te ensinou na sessão" em trilha e prova de skill.
2. **Promove o aprendizado de feature a tese central.** Deixa de ser um add-on do Teams e vira
   o **núcleo do produto de plataforma** (Solo e Enterprise).
3. **Absorve as camadas novas** — plataforma de aprendizado, prova auditável + certificados,
   prep de certificação, e a persona do **dev manual (sem IA)** — cada uma com veredito de
   novidade/defensabilidade/comprador/risco.

---

## 1. A tese (v2)

**north é a camada de observabilidade *e aprendizado* do desenvolvimento — onde o que você
constrói vira plano, doc, teste, conhecimento e prova de skill, com privacidade por design.**

A fundação local já captura a matéria-prima certa (commits, planos, docs gerados, conceitos
ensinados, ledger de decisões/bugs/padrões). A nuvem **não inventa dado** — ela sincroniza,
agrega, visualiza, **devolve currículo** e **emite prova**. O ativo defensável é o **ledger
longitudinal de aprendizado** (flywheel de dados proprietário) somado à **postura de
privacidade** — não a tecnologia de geração (um Copilot/Cody consegue replicar a geração;
não consegue replicar o seu histórico nem a confiança da marca).

---

## 2. Uma fundação, dois produtos (e o aprendizado no centro)

```
                    NUVEM north (opt-in, criptografada)
        API .NET 8 · web Next.js · multi-tenant · auth · Postgres
                 ▲ sync granular, consentido, auditável
   ┌─────────────┴──────────────┐
   │  AGENTE LOCAL (a CLI evolui)│  discovery · git · docs · learnings · insights
   └─────────────┬──────────────┘
                 ▼ lê (read-only) — invariante sagrado, vale na nuvem também
        projetos do dev (plan-build / .planning / git)

   north SOLO (dev)                     north TEAMS / ENTERPRISE (empresa)
   • kanban + portfólio + timeline      • visão de time derivada do trabalho real
   • TRILHA DE APRENDIZADO pessoal       • SKILLS INVENTORY derivado do trabalho real
     (do ledger + insights)             • PROVA auditável + certificados (Open Badges 3.0)
   • map+gap de certificação            • acompanhamento por colaborador · RBAC · SSO
   • histórico que não se perde         • cert-readiness do time · self-host
```

### Os dois compradores (decisão estrutural)
A pesquisa deixa claro que são **dois bolsos diferentes**:
- **Observabilidade de engenharia** → comprador = **VP Eng / CTO** (budget de dev-tools;
  Jellyfish vende "board reporting"). É a **porta de entrada** (credibilidade do dado).
- **Upskilling com prova** → comprador = **L&D / People** (budget de treinamento; quer
  *outcome*, "as skills estão sendo aplicadas no trabalho?"). É a **expansão** (ticket maior).

**Recomendação:** *land* via Eng (o dado derivado do trabalho real é o que dá credibilidade),
*expand* para L&D (que tem o orçamento e a necessidade de acompanhamento/prova). A trilha/prova
é a **bandeira** do Enterprise; a observabilidade é a entrada.

---

## 3. As camadas novas (veredito da pesquisa)

| Camada | Novo? | Defensável? | Comprador | Maior risco |
|---|---|---|---|---|
| **Aprendizado do trabalho real** (commits + sessões → trilha) | **Sim** — ninguém produtiza o loop | Médio (moat = ledger longitudinal + privacidade, não a geração) | Eng (credib.) → L&D (budget) | Incumbente (GitHub/Sourcegraph) acoplar à distribuição que você não tem |
| **Prova + certificados** | Não o padrão, **sim como *fonte*** (prova vinda do trabalho real) | Médio-alto se virar *issuer* reconhecido | L&D / People (compliance, talento) | Aceitação: empresa precisa crer que "trabalho real = skill". Mitiga com **Open Badges 3.0 / W3C VC** + metodologia transparente |
| **Prep de cert mapeado do trabalho** (AWS/OCI/OWASP) | **Provável sim** (sem concorrente direto — confiança média) | Médio (vendors donos dos mapas de objetivo podem fechar) | Dev (self-serve) + EM (cert-readiness do time) | AWS/Azure estenderem o Skill Builder p/ ingerir trabalho real |
| **Dev manual (sem IA)** — `north scan` | Sim como posicionamento | **Baixo** isolado (fácil de copiar; nicho) | Dev avesso a privacidade/preço; empresa com restrição a IA | Confundir nicho com mercado; over-investir cedo |

### Implicações de design já decididas pela pesquisa
- **Não reivindicar "primeiro a derivar sprint automaticamente"** — não é verdade nem
  diferencial. Apoiar em **"plan-native + local-first + read-only + zero-config"**.
- **Não construir certificado caseiro (PDF).** Emitir como **Open Badges 3.0** (1EdTech,
  final jun/2024) sobre **W3C Verifiable Credentials** — assinado, verificável offline,
  portável. Padrão maduro, baixo risco.
- **Prep de cert começa barato e read-only:** primeiro **mapeia + recomenda + gap analysis**
  ("seus últimos 90 dias cobriram X dos domínios da AWS SAA; faltam estes; aqui o prep").
  Conteúdo/prática completos vêm depois. Reusa ledger+insights que já existem.
- **Dev manual é on-ramp inclusivo, não a manchete:** posicionar como *"funciona use você IA
  ou não"* — `north scan` deriva trilha de git+código sem exigir sessão de IA. Amplia TAM
  (≈15% dos devs não usam IA; privacidade e preço são os bloqueios #1 e #2). Atacar **depois**
  de o Solo provar tração.
- **Privacidade é table-stakes que destrava o enterprise, não o produto que se cobra.**
  Self-host/dado-é-seu remove risco e fecha deal regulado (modelo GitLab Duo Self-Hosted);
  **monetizar o valor de aprendizado/prova, não a privacidade em si.**

---

## 4. As 3 tensões centrais — resolvidas

**Tensão 1 — Dois compradores, um produto?**
→ **Resolvido:** dois SKUs sobre uma fundação. *Land* Eng (credibilidade do dado), *expand*
L&D (orçamento/prova). Aprendizado é a bandeira; observabilidade é a entrada. Não virar Jira.

**Tensão 2 — Aprendizado precisa de dado rico vs. "subir só metadado".**
→ **Resolvido:** o **learning-data é um stream de consentimento SEPARADO**, granular, **nunca
embutido** no metadado de progresso. Fase 1 sobe só metadado (máxima confiança). O sync de
aprendizado é um **gate próprio**, mais tarde, com seu próprio opt-in e seu próprio
`north sync status`. O dev escolhe (ex.: sobe conceitos/skills, **não** o código).

**Tensão 3 — "Prova de aprendizado" = vigilância?**
→ **Resolvido:** mesmo DNA — "seu dado é seu", transparência total do que sai, e enquadrar como
**crescimento, não monitoramento**. Tecnicamente, **Open Badges 3.0 / VC** (à prova de
adulteração) e **o dev controla o que é compartilhado** com o gestor. A prova é *do colaborador*,
portável, e ele a leva ao trocar de emprego.

---

## 5. Arquitetura (mantém a v1, com adendos)

Mantém a stack da v1 — **agente Python + `north sync`; API .NET 8 (ASP.NET Core); web Next.js;
OAuth2/OIDC (Entra ID + GitHub); PostgreSQL multi-tenant; Docker em cloud gerenciada.** O
dashboard local (HTML estático) continua para offline. Adendos da v2:

- **Serviço de credenciais** que emite **Open Badges 3.0 / W3C VC** (assinatura do issuer).
- **Modelo de skills** (taxonomia leve) que mapeia *conceitos do ledger/insights → skills →
  objetivos de certificação*. Começa enxuto e curado (não tentar cobrir tudo).
- **Dois canais de sync** separados por consentimento: `progress` (metadado) e `learning`
  (skills/conceitos/prova). Nunca acoplados.
- **`north scan`** (persona manual): comando read-only que deriva sinal de git+código sem IA,
  alimentando trilha/skills. Reusa o discovery existente.

---

## 6. Roadmap v2 (cada fase é um gate de aprendizado de mercado)

| Fase | Entrega | Objetivo de validação | vs. v1 |
|---|---|---|---|
| **0 — hoje** | CLI + dashboard local (v0.9.1) | feito | = |
| **1 — Sync + nuvem pessoal** | `north sync` opt-in (só **metadado**); web pessoal read-only | devs confiam em subir? veem valor no acesso web? | = v1 |
| **2 — Solo web + trilha** | kanban interativo, timeline, **trilha pessoal derivada do ledger/insights** (learning-data como opt-in próprio); **map+gap de cert** | vira hábito? o dev volta? a trilha tem valor percebido? | **trilha promovida ao centro** |
| **3 — Teams** | org, convites, RBAC, SSO, visão de time + **skills inventory derivado do trabalho real**; *land* via Eng | uma empresa paga por assento? o dado é crível p/ liderança? | **+ skills inventory** |
| **4 — Enterprise / aprendizado** | **prova auditável (Open Badges 3.0)**, acompanhamento L&D, **cert-prep com gap analysis**, self-host, features por empresa | contrato enterprise fecha? L&D compra a prova? | **nova ênfase L&D/prova** |
| **transversal** | **`north scan`** (dev manual, sem IA) | amplia TAM sem diluir foco — só após Solo provar tração | **persona nova** |

**Solo antes de Teams. Eng antes de L&D. Mapear/recomendar antes de produzir conteúdo de cert.**

---

## 7. Decisões em aberto (precisam do dono)

Herdadas da v1 e ainda válidas:
1. **Foco inicial:** Solo primeiro (recomendado) ✔ ou ir direto ao caso empresa?
2. **O que sobe na Fase 1:** confirmar **só metadado** (learning-data fica para a Fase 2, canal próprio).
3. **Open-core:** confirmar CLI local OSS/MIT e grátis para sempre.
4. **Stack:** .NET 8 + Next.js + Postgres — confirma?
5. **Posicionamento:** "privacidade por design" como bandeira (table-stakes) + **"aprendizado do
   trabalho real" como diferencial central** — fecha?
6. **Nome/edições:** north (OSS) · north Cloud · north Teams · north Enterprise — fecha?

Novas, trazidas pela v2:
7. **Comprador-âncora do Enterprise:** Eng-primeiro-L&D-depois (recomendado) ou apostar direto em L&D?
8. **Prova:** adotar **Open Badges 3.0 / W3C VC** como padrão de certificado — confirma?
9. **Cert-prep:** começar só **map+recomenda+gap** (read-only, barato) e adiar conteúdo — ok?
10. **Dev manual / `north scan`:** tratar como on-ramp transversal pós-Solo (recomendado) ou priorizar?

---

## 8. Pesquisa de mercado — fontes-chave (2026-06-09)

- **Skill via trabalho real é gap real:** Workera/Pluralsight inferem skill de **avaliações
  formais**, "não capturam skills demonstradas no trabalho real" — cloudassess.com (roundup de
  skills-intelligence); Pluralsight Skill IQ (help.pluralsight.com).
- **Observabilidade já deriva de git+PM:** Jellyfish (boardroom/allocation), LinearB (métricas +
  automação de PR), Swarmia (métricas dev-friendly), DX/getdx (surveys + AI measurement). GitHub
  Copilot metrics GA fev/2026 — mede *uso*, não *crescimento de skill*.
- **Aprender do próprio código/sessão:** ninguém produtiza; Sourcegraph Cody e CodeSee fazem
  *entendimento/onboarding*, não trilha de skill por dev.
- **L&D compra outcome, não catálogo:** Explorance, D2L — métrica que importa é skill aplicada no
  trabalho. Degreed agrega sinal verificado de skill (north pode ser *fonte*).
- **Prova:** Open Badges 3.0 (1EdTech, final jun/2024) sobre W3C Verifiable Credentials —
  assinado, verificável offline, portável.
- **Cert-prep:** AWS Skill Builder faz gap por *score de simulado*, não pelo seu código real —
  sem concorrente direto p/ "real-work → objetivos de cert" (confiança média).
- **Dev sem IA:** Stack Overflow 2025 — ~15% não adotaram IA, 52% não usam agentes; bloqueios #1
  privacidade, #2 preço.
- **Privacidade/self-host:** GitLab Duo Self-Hosted vende isolamento a setor regulado — destrava
  deal, não cobra prêmio isolado (table-stakes).

> **Não verificado / cuidado:** ausência de concorrente em cert-prep é *absence-of-evidence*
> (varrer startups + roadmaps AWS/Microsoft Learn antes de reivindicar "primeiro"); preço/tiers
> da DX são de terceiros; willingness-to-pay de L&D pela "prova do trabalho real" não tem
> benchmark; maturidade de adoção de OB 3.0 em sistemas de RH é incerta.

---

## 9. Próximo passo concreto (dogfooding)

Com a visão v2 fechada (após suas decisões na §7), escrever o **PRD da Fase 1**
(`/north-doc prd` — *north sync + nuvem pessoal read-only, só metadado*) + um **ADR da stack**,
usando as próprias ferramentas do north. Dogfooding: o north documenta o próprio futuro.
