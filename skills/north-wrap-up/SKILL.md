---
name: north-wrap-up
description: Ritual de fim de dia — regenera a Central de Produtividade e gera um RESUMO-DO-DIA central por projeto (espelhado em <projeto>/docs). Ative para "/north-wrap-up", "fim do dia", "encerrar o dia", "resumo do dia".
allowed-tools: Bash, Read, Edit
argument-hint: ""
---

# /north-wrap-up — Fim de dia (Central de Produtividade)

Ritual de encerramento, multi-projeto e 100% local. Regenera o painel e gera um
resumo datado por projeto, consolidando o que avançou no dia (commits, arquivos
não commitados, bloqueios, próximos passos).

**Passos obrigatórios (nessa ordem):**

0. **Atualize os refs git** (best-effort, para a checagem pré-push ser precisa):

   ```bash
   git fetch --all --quiet 2>/dev/null || true
   ```

1. Rode o launcher da central:

   ```bash
   # macOS / Linux
   python3 ~/.north/run.py wrap-up
   # Windows (PowerShell)
   python "$env:USERPROFILE\.north\run.py" wrap-up
   ```

   (Instalou via npm? `north wrap-up` funciona em qualquer SO.)

2. Mostre a saída do script (linha "FIM DO DIA —" + a lista de resumos gerados,
   um por projeto, em `~/.north/resumos/<projeto>/`).

3. Leia os resumos recém-gerados (caminhos impressos pelo script) e mostre o
   conteúdo formatado ao usuário, agrupado por projeto.

   **Foco real do dia:** o resumo distingue *"N commit(s) seu(s) hoje"* do total do
   time (repo compartilhado). Destaque o(s) projeto(s) onde **você** de fato trabalhou
   (commits seus / arquivos não commitados) — não trate como seu o que só teve avanço
   de outros devs. Se o dia teve um foco claro e ele não estava fixado, **ofereça**
   fixar (`north focus --only <id>`) para o próximo bom-dia já abrir nele.

4. Se algum resumo tiver linhas `[PREENCHER via /code-review]`, **ofereça**
   rodar a revisão do diff (não execute sem confirmação — apenas pergunte).

5. Se houver linhas `[PREENCHER]` que exigem decisão humana (ex.: próxima TASK
   quando não há planejadas), liste-as como itens que precisam do input do usuário.

6. **Versionamento antes de encerrar (boas práticas git):** se algum resumo trouxer
   "⚠ ANTES DE PUSHAR" (branch atrás do remoto/base) ou commits locais não pushados,
   oriente o fechamento seguro — **sem executar sozinho, apenas guiando**:
   - `git pull --rebase` (sincroniza sem merge-commit ruidoso) e resolver conflitos agora;
   - rodar os testes após o rebase;
   - revisar o diff (`/north-...`? não — `git diff`) antes do push;
   - então `git push`. Se a branch é de feature, lembre de abrir/atualizar o PR.
   Objetivo: terminar o dia com a branch sincronizada, sem conflito pendente.

**Não faça mais nada além disso.** Não invoque outras skills, não acione squads,
não rode testes você mesmo (além do fetch best-effort). Este é o ritual de encerramento.
