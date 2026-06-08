---
name: north-doc
description: north — Gera docs de SDLC (PRD, SPEC, SDD, TDD, ADR, SECURITY) ancorado no contexto real do projeto e na biblioteca de referências. A IA redige sob sua direção; o motor é read-only. Ative para "/north-doc", "gera o PRD", "escreve a spec", "cria um ADR", "documenta a arquitetura (SDD)", "plano de testes (TDD)", "modelo de ameaças".
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, WebSearch, WebFetch
argument-hint: "<tipo> [alvo]   ex.: spec checkout | adr \"escolha do banco\""
---

# /north-doc — Fábrica de documentos de SDLC

Ajuda a **criar e manter** os artefatos de engenharia (PRD · SPEC · SDD · TDD · ADR ·
SECURITY) com qualidade consistente. **A IA redige; você dirige.** O motor do north é
**read-only** — quem escreve o arquivo é você (a IA), com o consentimento do usuário.

## Tipos
`prd` (por quê/para quem) · `spec` (o quê — contrato) · `sdd` (como — design) ·
`tdd` (plano de testes) · `adr` (decisão) · `security` (ameaças/controles).

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
   - Default: ao lado dos planos — `plan-build/<TIPO>-<alvo>.md` (ou `docs/`). 
   - **Idempotente:** se já existe, **atualize** preservando o que é válido; não duplique.
   - Cross-link: SDD referencia PRD/SPEC; TDD referencia SPEC; mencione ADRs.

## Encadeamento natural
PRD → SPEC → (SDD + TDD) → código (`/north-dev`, TDD-first usa o SPEC/TDD) → SECURITY/ADR conforme decisões.

## Regras de ouro
- **Read-only sobre os planos do usuário** no nível do MOTOR; o arquivo novo é escrito por
  você (IA) **com confirmação** do usuário, no caminho que ele aprovar.
- **Ancore, não invente:** contexto real do projeto + biblioteca/doc oficial, com citação.
- Conciso e específico ao projeto — nada de doc genérico de template vazio.
