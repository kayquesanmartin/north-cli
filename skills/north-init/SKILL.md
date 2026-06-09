---
name: north-init
description: north — Pluga um projeto no north (enrollment opt-in). Em vez de auto-varrer pastas, o north passa a rastrear SÓ os projetos que você plugou — track direcionado, sem ruído no bom-dia/fim-do-dia. Read-only: registra o caminho em ~/.north, nada é escrito no projeto. Ative para "/north-init", "plugar o projeto no north", "rastrear este projeto", "north track", "começar a acompanhar este repo".
allowed-tools: Bash
argument-hint: "[caminho]   (vazio = projeto atual)"
---

# /north-init — Plugar um projeto no north (enrollment opt-in)

Faz o north rastrear **só** os projetos que você escolheu, em vez de auto-varrer
todas as pastas. Mata o ruído (bom-dia/fim-do-dia/painel passam a mostrar só o que
você plugou). **Motor read-only:** registra o caminho absoluto em `~/.north` —
**nada é escrito dentro do projeto**.

1. Na **raiz do projeto** que você quer acompanhar, rode:

   ```bash
   python3 ~/.north/run.py init
   # Windows: python "$env:USERPROFILE\.north\run.py" init
   # ou um caminho específico:  python3 ~/.north/run.py init "/caminho/do/projeto"
   ```

   (Instalou via npm? `north init` funciona em qualquer SO.)

2. O north pluga o projeto e **ativa o modo enrolled** (passa a rastrear só os
   plugados). Se não houver `plan-build/`/`.planning` ali, ele avisa — o projeto
   aparece no painel quando tiver um plano.

3. Confirme com `north status` (mostra o modo e os projetos plugados). Para
   des-plugar: `/north-forget <projeto>` (ou `north forget <projeto>`).

**Quem já usava o north** (com `scan_roots`) continua no modo `scan` legado até
rodar o `init` pela primeira vez — então migra para o enrolled, sem quebrar nada.
