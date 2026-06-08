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

4. **CONFIRME o foco real (não crave pela leitura).** O script detecta pelo git o
   que VOCÊ está tocando e imprime, quando há sinal, um bloco
   **"🎯 SEU FOCO PROVÁVEL (detectado pelo git)"** com os sinais (working tree sujo,
   commits seus hoje, sua branch). A regra:
   - **Se houver bloco 🎯:** pergunte de forma curta se é nele mesmo que ele vai
     trabalhar hoje (ex.: *"Detectei que você está em `backoffice-backend` (3 arquivos
     sujos, branch feat/x). É o foco de hoje?"*). **Se SIM**, fixe: `north focus --only <id>`.
     **Se NÃO**, pergunte qual projeto e fixe o escolhido (ou `north focus --all`).
   - **Se NÃO houver bloco 🎯** (nenhum sinal seu — início do dia, pós-clone):
     **pergunte** em qual projeto ele vai focar antes de sugerir, em vez de cravar
     pelo que foi lido. Aí fixe com `north focus --only <id>`.
   Nunca assuma silenciosamente um projeto que o git não aponta como seu.

5. Com base no foco confirmado, sugira **qual squad** acionar primeiro hoje
   (Backend, Frontend, QA, Arquitetura, Security, DevOps…). Use as ferramentas
   já recomendadas pelo script como pista. Seja breve — uma linha por sugestão.

6. **Se aparecer o bloco "⚠ VERSIONAMENTO"** (branch atrás do remoto/base),
   destaque-o e oriente o usuário a sincronizar **antes** de novos commits:
   `git pull --rebase` (ou rebase na base), resolver conflitos cedo. Isso evita
   conflitos grandes no fim do dia. **Não execute o pull sozinho — oriente.**

**Não faça mais nada além disso.** Não edite código, não rode testes, não
invoque outras skills (além do fetch best-effort). Este é só o ritual de bom dia.
