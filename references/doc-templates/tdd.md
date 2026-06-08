# TDD — Plano de Testes — <Nome da feature>

> Test Design/Plan. Deriva dos **critérios de aceite do SPEC**. No fluxo TDD, estes
> testes são escritos **antes** do código (red→green→refactor — ver `/north-dev`).

## 1. Estratégia
- Pirâmide: o que cobrir em unit / integração / e2e (e por quê).
- Stack de teste do projeto (ex.: xUnit + Moq + FluentAssertions).

## 2. Casos de teste (do aceite)
> Um caso por critério de aceite do SPEC. Marque o nível.
| ID | Critério (SPEC) | Nível | Dado / Quando / Então | Status |
|---|---|---|---|---|
| T-1 | AC-1 | unit | ... | [ ] |
| T-2 | AC-2 | integração | ... | [ ] |

## 3. Casos de borda & negativos
- Entradas inválidas, limites, concorrência, falhas externas, idempotência.

## 4. Dados & ambiente de teste
- Fixtures, mocks/stubs (o que mockar e o que não), banco de teste, seeds.

## 5. Cobertura & gates
- Meta de cobertura, thresholds, baseline, o que **bloqueia** o merge.

## 6. Fora do escopo de teste
- O que não será testado automaticamente (e como será validado).

---
*Referências consultadas (north library):* <citar — ex.: 07-testing-tdd.md (3 leis do TDD)>
