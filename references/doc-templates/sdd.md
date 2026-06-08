# SDD — <Nome da feature/módulo>

> Software Design Document: **COMO** será construído. Lê o PRD/SPEC antes.
> Ancore decisões em princípios (Clean Architecture, SOLID — north library).

## 1. Contexto & objetivo
- Resumo do que o SPEC pede e a restrição-chave de design.

## 2. Visão de arquitetura
- Diagrama (Mermaid) dos componentes e do fluxo principal.
- Camadas/limites (Domain/Application/Infrastructure) e regra de dependência.

```mermaid
flowchart LR
  A[Cliente] --> B[API/Controller]
  B --> C[Application/Use Case]
  C --> D[(Repositório)]
```

## 3. Decisões de design
- Padrões adotados e **por quê** (trade-offs). Linkar ADRs quando houver.

## 4. Modelo de dados
- Entidades, relacionamentos, migrações. Invariantes.

## 5. Contratos internos
- Interfaces/ports, eventos, integrações externas (timeouts, retries, idempotência).

## 6. Não-funcionais
- Performance, escalabilidade, observabilidade (logs/traces/métricas), segurança.

## 7. Alternativas consideradas
- O que foi descartado e por quê.

## 8. Riscos & plano de teste (resumo — detalhar no TDD)
- Pontos de risco do design e como serão validados.

---
*Referências consultadas (north library):* <citar>
