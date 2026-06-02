---
name: painel
description: Abre/regenera a Central de Produtividade — dashboard multi-projeto que consolida progresso, sprints, kanban, bloqueios e débito técnico de todos os projetos rastreados. Ative para "/painel", "abrir o painel", "dashboard", "status dos projetos", "como estão os projetos".
allowed-tools: Bash
argument-hint: "[build|open]"
---

# /painel — Central de Produtividade

Painel HTML profissional (CSS/JS puro, sem dependências) que consolida **todos
os projetos** rastreados em arquivos `plan-build/*.md`. Tem visão de portfólio
(donuts + KPIs por projeto), detalhe por projeto (sprints + kanban filtrável),
bloqueios, débito técnico e tema claro/escuro.

**Comportamento:**

1. Por padrão, **regenera e abre** o painel:

   ```bash
   python "%USERPROFILE%\.claude\painel\run.py" build
   python "%USERPROFILE%\.claude\painel\run.py" open
   ```

   (Ou, em um comando, `... run.py bom-dia` se o usuário também quiser o foco do dia.)

2. Se o usuário passar `open` como argumento e o painel já existir, apenas abra
   (sem regenerar):

   ```bash
   python "%USERPROFILE%\.claude\painel\run.py" open
   ```

3. Mostre a saída do script (caminho do `dashboard.html`, nº de projetos,
   tasks done, bloqueios). Confirme que abriu no navegador.

4. Se aparecerem novos projetos descobertos ("+ N novo(s) projeto(s)…"),
   comente brevemente e lembre que a config fica em
   `%USERPROFILE%\.claude\painel\config\projects.json` (apelidos, cores, ordem,
   ligar/desligar projetos).

**Não edite os arquivos de plano** — o motor só lê. Este comando é de leitura/visualização.
