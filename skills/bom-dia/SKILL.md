---
name: bom-dia
description: Ritual de início de dia — regenera a Central de Produtividade (todos os projetos), mostra o FOCO DO DIA consolidado e abre o painel no navegador. Ative para "/bom-dia", "bom dia", "começar o dia", "o que faço hoje".
allowed-tools: Bash
argument-hint: ""
---

# /bom-dia — Início de dia (Central de Produtividade)

Ritual de início de dia, multi-projeto e 100% local. O motor varre todos os
projetos rastreados (qualquer `plan-build/` com `Progress*.md` + `Sprint*.md`),
consolida o progresso e mostra onde focar.

**Passos obrigatórios (nessa ordem):**

1. Rode o launcher da central:

   ```bash
   python "%USERPROFILE%\.claude\painel\run.py" bom-dia
   ```

   (Se `%USERPROFILE%` não expandir no seu shell, use o caminho absoluto
   `C:\Users\<seu-usuario>\.claude\painel\run.py`.)

2. Mostre a saída completa do script — ela já vem formatada: cabeçalho
   "BOM DIA", progresso global do portfólio, FOCO DE HOJE por projeto
   (sprint atual em aberto, próximas tasks desbloqueadas, bloqueios, débito de
   alta prioridade) e ferramentas/squads recomendados.

3. O script já regenera o `dashboard.html` e o abre no navegador (Windows).
   Apenas confirme ao usuário que o painel foi atualizado — não tente abrir
   manualmente.

4. Com base no FOCO DO DIA, sugira **qual squad** acionar primeiro hoje
   (Backend, Frontend, QA, Arquitetura, Security, DevOps…). Use as ferramentas
   já recomendadas pelo script como pista. Seja breve — uma linha por sugestão.

**Não faça mais nada além disso.** Não edite código, não rode testes, não
invoque outras skills. Este é só o ritual de bom dia.
