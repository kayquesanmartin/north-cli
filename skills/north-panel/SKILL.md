---
name: north-panel
description: Abre/regenera a Central de Produtividade — dashboard multi-projeto que consolida progresso, sprints, kanban, bloqueios e débito técnico de todos os projetos rastreados. Ative para "/north-panel", "abrir o painel", "dashboard", "status dos projetos", "como estão os projetos".
allowed-tools: Bash
argument-hint: "[build|open]"
---

# /north-panel — Central de Produtividade

Painel HTML profissional (CSS/JS puro, sem dependências) que consolida **todos
os projetos** rastreados em arquivos `plan-build/*.md`. Tem visão de portfólio
(donuts + KPIs por projeto), detalhe por projeto (sprints + kanban filtrável),
bloqueios, débito técnico e tema claro/escuro.

**Comportamento:**

1. Por padrão, **regenera e abre** o painel:

   ```bash
   # macOS / Linux (no Windows/PowerShell: python "$env:USERPROFILE\.north\run.py" ...)
   python3 ~/.north/run.py build
   python3 ~/.north/run.py open
   ```

   (Instalou via npm? `north build` / `north open`. Ou `north morning` se também
   quiser o foco do dia.)

2. Se o usuário passar `open` como argumento e o painel já existir, apenas abra
   (sem regenerar):

   ```bash
   python3 ~/.north/run.py open   # Windows: python "$env:USERPROFILE\.north\run.py" open
   ```

3. Mostre a saída do script (caminho do `dashboard.html`, nº de projetos,
   tasks done, bloqueios). Confirme que abriu no navegador.

4. Se aparecerem novos projetos descobertos ("+ N novo(s) projeto(s)…"),
   comente brevemente e lembre que a config fica em
   `~/.north/config/projects.json` (apelidos, cores, ordem,
   ligar/desligar projetos, fonte primária).

**Não edite os arquivos de plano** — o motor só lê. Este comando é de leitura/visualização.
