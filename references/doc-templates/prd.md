# PRD — <Nome da feature/produto>

> Product Requirements Document. Responde **POR QUE** e **PARA QUEM**, não como.
> Nasce de uma sabatina (`/north-grill`): as gray-areas já foram furadas antes de escrever.
> A IA rascunha a partir do contexto do projeto; o time/PO dirige. Requisitos com **ID
> rastreável** que descem até os critérios de aceite do SPEC e às tasks do Sprint.

> **Status:** Rascunho | Em revisão | Aprovado · **Complexidade:** Pequeno | Médio | Grande | Complexo
> *(a complexidade calibra o que vem depois — Médio+: SPEC; Grande+: SDD; sempre: Sprint)*

## 1. Problema
- Qual dor/oportunidade? Por que agora?
- Evidência (dados, feedback, ticket).

## 2. Usuários & personas
- Quem usa? Qual o cenário/jornada principal?

## 3. Objetivo & métricas de sucesso
- Resultado esperado (1 frase).
- Métricas mensuráveis (ex.: -30% no tempo de X; NPS; adoção). Sem métrica = sem como saber se deu certo.

## 4. Escopo
- **Inclui:** ...
- **Não inclui (out of scope):** ...

## 5. Requisitos (com ID rastreável)
> Cada requisito ganha um ID. O SPEC referencia o ID nos critérios de aceite (AC); o Sprint
> referencia o ID nas tasks. Assim dá pra rastrear requisito → contrato → teste → entrega.

**Funcionais** (priorize — MoSCoW: Must/Should/Could/Won't):

| ID | Requisito | Prioridade | Vira (SPEC/AC) |
|----|-----------|------------|----------------|
| RF-1 | O sistema deve ... | Must | AC-1, AC-2 |
| RF-2 | ... | Should | AC-3 |

**Não-funcionais** (performance, segurança, LGPD, disponibilidade, acessibilidade):

| ID | Requisito | Critério mensurável |
|----|-----------|---------------------|
| RNF-1 | Performance | ex.: p95 < 300ms |
| RNF-2 | LGPD | ex.: PII mascarada em log |

## 6. Decisões da sabatina (gray-areas resolvidas)
> Saída do `/north-grill`: cada ramo da árvore que foi furado. Evita re-discutir o resolvido.

| Decisão | Escolha | Por quê | Alternativa descartada |
|---------|---------|---------|------------------------|
| ... | ... | ... | ... |

## 7. Riscos & dependências
- Riscos (com mitigação) · dependências externas/times · suposições que, se falsas, derrubam o plano.

## 8. Marcos / faseamento
- MVP → incrementos. Critério de "pronto para lançar".

---
*Encadeia para:* SPEC (contrato + AC testáveis por RF) → (SDD se Grande+) → Sprint (tasks por RF).
*Referências consultadas (north library):* <citar — ex.: 10-requirements-process, 14-spec-driven-development>
