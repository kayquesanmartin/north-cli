# Central de Produtividade — motor + instalador

Ferramenta local (sem nuvem) que **descobre automaticamente** todos os seus
projetos com tracking em `plan-build/*.md`, consolida o progresso e gera um
**dashboard.html profissional** (CSS/JS puro, sem Tailwind) + os rituais
`/bom-dia` e `/fim-do-dia`.

## Instalar (uma vez)

```bash
python install.py
```

O instalador:
1. Copia o motor para `~/.claude/painel/` (tool home).
2. Instala as skills globais `/bom-dia`, `/fim-do-dia`, `/painel` em `~/.claude/skills/`.
3. **Lista os projetos achados sob a raiz e abre um menu** para você escolher
   quais acompanhar (templates são detectados e ignorados).
4. Gera o primeiro painel.

Flags: `--all` (sem menu), `--scan-root "<caminho>"` (raiz extra), `--no-build`.

## Usar

No Claude Code (de qualquer projeto): `/bom-dia` · `/fim-do-dia` · `/painel`

No terminal:
```bash
python "~/.claude/painel/run.py" bom-dia      # foco do dia + abre painel
python "~/.claude/painel/run.py" fim-do-dia   # resumos do dia por projeto
python "~/.claude/painel/run.py" build        # só regenera o painel
```

## Estrutura

```
dashboard/
  install.py            # O INSTALÁVEL — rode este
  src/
    run.py              # launcher (vai para a tool home)
    painel/
      config.py         # projects.json: scan_roots, toggles, apelidos, cores, ordem
      discovery.py      # auto-descoberta + montagem do modelo + git
      parsers.py        # normaliza formatos heterogêneos (tabelas/code-blocks/barras/emojis)
      render.py         # dashboard.html (CSS/JS puro, multi-projeto, tema claro/escuro)
      rituals.py        # bom-dia / fim-do-dia (multi-projeto)
      cli.py            # build | bom-dia | fim-do-dia | open
  skills/               # SKILL.md de painel, bom-dia, fim-do-dia (instalados)
  templates/            # template do RESUMO-DO-DIA

  # legado (single-projeto, superseado pelo motor acima):
  bom-dia.py · fim-do-dia.py · generate-dashboard.py · dashboard.html
```

## Configuração

`~/.claude/painel/config/projects.json` — por projeto: `enabled`, `alias`,
`color`, `order`. Ligue/desligue projetos, dê apelidos e cores. Projetos novos
aparecem automaticamente (habilitados) na próxima execução.

> O motor **só lê** os `.md` — nunca edita seus planos. Fonte única de verdade.
