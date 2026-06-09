# DECISIONS — por que este projeto é como é

> Log **vivo** de decisões — o *porquê*, não o *quê* (o "quê" o git já conta).
> Mais leve que um ADR: uma linha por decisão, em ordem cronológica inversa (a mais
> recente no topo). Serve de **contexto inicial** para uma sessão de IA e para você
> mesmo retomando o projeto. Mais pesado/estrutural? Promova a um `ADR`.

## Decisões

### AAAA-MM-DD — <decisão em uma linha>
- **Escolhi/optei por:** <o que foi decidido> (afirmativo e direto).
- **Porque:** <a razão real — restrição, trade-off, contexto do negócio>.
- **Em vez de:** <alternativas descartadas e por quê>.
- **Status:** vigente | revisada em AAAA-MM-DD | substituída por <link/ADR>.

### AAAA-MM-DD — <exemplo> Banco: SQL Server, não Postgres
- **Escolhi/optei por:** SQL Server 2022.
- **Porque:** stack do time já domina; licença já paga; integra com o resto do parque.
- **Em vez de:** Postgres (ótimo, mas adicionaria curva + ops sem ganho aqui).
- **Status:** vigente.

---
*Como manter:* registre a decisão **quando ela acontece** (antes de esquecer o porquê).
*Referências consultadas (north library):* <citar quando aplicável>
