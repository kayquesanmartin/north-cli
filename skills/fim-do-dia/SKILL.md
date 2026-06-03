---
name: fim-do-dia
description: Ritual de fim de dia — regenera a Central de Produtividade e gera um RESUMO-DO-DIA central por projeto (espelhado em <projeto>/docs). Ative para "/fim-do-dia", "fim do dia", "encerrar o dia", "resumo do dia".
allowed-tools: Bash, Read, Edit
argument-hint: ""
---

# /fim-do-dia — Fim de dia (Central de Produtividade)

Ritual de encerramento, multi-projeto e 100% local. Regenera o painel e gera um
resumo datado por projeto, consolidando o que avançou no dia (commits, arquivos
não commitados, bloqueios, próximos passos).

**Passos obrigatórios (nessa ordem):**

1. Rode o launcher da central:

   ```bash
   # macOS / Linux
   python3 ~/.north/run.py fim-do-dia
   # Windows (PowerShell)
   python "$env:USERPROFILE\.north\run.py" fim-do-dia
   ```

   (Instalou via npm? `north fim-do-dia` funciona em qualquer SO.)

2. Mostre a saída do script (linha "FIM DO DIA —" + a lista de resumos gerados,
   um por projeto, em `~/.north/resumos/<projeto>/`).

3. Leia os resumos recém-gerados (caminhos impressos pelo script) e mostre o
   conteúdo formatado ao usuário, agrupado por projeto.

4. Se algum resumo tiver linhas `[PREENCHER via /code-review]`, **ofereça**
   rodar a revisão do diff (não execute sem confirmação — apenas pergunte).

5. Se houver linhas `[PREENCHER]` que exigem decisão humana (ex.: próxima TASK
   quando não há planejadas), liste-as como itens que precisam do input do usuário.

**Não faça mais nada além disso.** Não invoque outras skills, não acione squads,
não rode testes. Este é o ritual de encerramento — só consolidar o dia.
