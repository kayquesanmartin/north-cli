---
name: north-dev
description: north — Codar com TDD-first. SEMPRE que for desenvolver uma task/feature, oferece o ciclo TDD e escreve os TESTES ANTES, a partir dos critérios de aceite reais do plano (red→green→refactor) — prende o código ao teste e ao contexto do projeto. Ative para "/north-dev", "vou codar isso", "implementar a task", "começar a desenvolver", "codar com TDD", "bora implementar S3B-2".
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, WebSearch, WebFetch
argument-hint: "[id da task ou descrição do que vai codar]"
---

# /north-dev — Desenvolvimento TDD-first

Quando o usuário vai **desenvolver**, o north **sempre oferece TDD** e, se aceito,
escreve os **testes primeiro** a partir dos **critérios de aceite reais** — assim o
código fica preso ao teste e ao contexto do projeto, não ao "achismo".

## 0. Pergunte ANTES de codar (regra de produto)
Ao iniciar qualquer implementação, **ofereça TDD** (default recomendado):

> "Vou implementar **<task/feature>**. Codamos com **TDD** (testes primeiro, a partir
> dos critérios de aceite)? **[S/n]**"

- **Default ON.** Só pule se o usuário recusar, ou se `north config set tdd_default off`
  estiver configurado (nesse caso, ofereça mais leve, sem insistir).
- Se o usuário recusar: siga normal, mas registre o risco ("sem teste primeiro, valido depois").

## 1. Puxe os critérios de aceite REAIS (não invente)
Se houver id de task, leia o contrato que o north já extrai do plano:

```bash
python3 ~/.north/run.py task <id>      # o que entregar + ✅ critérios de aceite
# Windows: python "%USERPROFILE%\.north\run.py" task <id>
```

Use o bloco **✅ critérios de aceite** (vindo do `Evaluator valida:` / DoD do `Sprint*.md`)
como a especificação dos testes. Sem id/contrato: leia o `Sprint*.md`/`spec`/`PRD` com Read,
ou alinhe os critérios com o usuário **antes** de escrever teste.

## 2. Ancore na biblioteca + doc oficial
Antes de escrever os testes, consulte os princípios de teste do projeto:

```bash
python3 ~/.north/run.py library find "tdd testing"
```

Leia `07-testing-tdd.md` (3 leis do TDD) e cite. Complemente com doc oficial do framework
de teste (microsoft-docs p/ xUnit/.NET; context7 p/ libs) — **detecte a stack do repo**
(xUnit/NUnit/pytest/Jest…) lendo os arquivos de projeto; não imponha framework.

## 3. O ciclo (red → green → refactor)
1. **RED — escreva os testes primeiro**, um por critério de aceite. Rode-os e **mostre
   que falham** (vermelho) — prova que testam algo real.
2. **GREEN — implemente o mínimo** para passar. Sem dourar a pílula (3ª lei do TDD).
   Rode os testes até **verde**.
3. **REFACTOR — limpe** com os testes te protegendo (nomes, duplicação, SOLID — cite a
   biblioteca). Rode os testes de novo.
4. Repita por critério até cobrir o aceite. **Não pule pro código de produção sem um
   teste falhando antes** (1ª lei do TDD).

## 4. Feche
- Resuma: critérios cobertos por teste, o que ficou verde, o que falta.
- Se o `/north-insight` estiver ligado, ensine o conceito mais difícil que você usou.
- Lembre o usuário de revisar o diff (`/north-review`) antes do PR.

## Regras de ouro
- **Teste antes do código.** É o ponto inteiro — não inverta "pra ir mais rápido".
- **Critérios reais do plano**, não inventados. Se não existem, defina com o usuário/PO primeiro.
- **Read-only sobre os planos:** você escreve testes/código no projeto (com consentimento),
  nunca edita os arquivos de plano (`plan-build/`, `spec`, `PRD`).
