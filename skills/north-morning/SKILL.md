---
name: north-morning
description: Ritual de início de dia — regenera a Central de Produtividade (todos os projetos), mostra o FOCO DO DIA consolidado e abre o painel no navegador. Ative para "/north-morning", "bom dia", "começar o dia", "o que faço hoje".
allowed-tools: Bash
argument-hint: ""
---

# /north-morning — Início de dia (Central de Produtividade)

Ritual de início de dia, multi-projeto e 100% local. O motor varre todos os
projetos rastreados (qualquer `plan-build/` com `Progress*.md` + `Sprint*.md`),
consolida o progresso e mostra onde focar.

**Passos obrigatórios (nessa ordem):**

0. **Atualize os refs git** (best-effort, para o bloco VERSIONAMENTO ser preciso) —
   se houver repositório git no diretório atual / projetos:

   ```bash
   git fetch --all --quiet 2>/dev/null || true
   ```

   Ignore silenciosamente se estiver offline ou não for um repo.

1. Rode o launcher da central:

   ```bash
   # macOS / Linux
   python3 ~/.north/run.py morning
   # Windows (PowerShell)
   python "$env:USERPROFILE\.north\run.py" morning
   ```

   (Instalou via npm? `north morning` funciona em qualquer SO.)

2. Mostre a saída completa do script — ela já vem formatada: cabeçalho
   "BOM DIA", progresso global do portfólio, FOCO DE HOJE por projeto
   (sprint atual em aberto, próximas tasks desbloqueadas, bloqueios, débito de
   alta prioridade) e ferramentas/squads recomendados.

3. O script já regenera o `dashboard.html` e o abre no navegador (Windows/macOS/Linux).
   Apenas confirme ao usuário que o painel foi atualizado — não tente abrir
   manualmente.

4. Com base no FOCO DO DIA, sugira **qual squad** acionar primeiro hoje
   (Backend, Frontend, QA, Arquitetura, Security, DevOps…). Use as ferramentas
   já recomendadas pelo script como pista. Seja breve — uma linha por sugestão.

5. Se houver vários projetos e o usuário sinalizar que hoje só vai mexer em um,
   **ofereça fixar o foco do dia** (`north focus --only <id>`) — assim o `/north-morning`
   e o `/north-wrap-up` mostram só esse projeto. `north focus --all` volta ao portfólio.

6. **Se aparecer o bloco "⚠ VERSIONAMENTO"** (branch atrás do remoto/base),
   destaque-o e oriente o usuário a sincronizar **antes** de novos commits:
   `git pull --rebase` (ou rebase na base), resolver conflitos cedo. Isso evita
   conflitos grandes no fim do dia. **Não execute o pull sozinho — oriente.**

**Não faça mais nada além disso.** Não edite código, não rode testes, não
invoque outras skills (além do fetch best-effort). Este é só o ritual de bom dia.
