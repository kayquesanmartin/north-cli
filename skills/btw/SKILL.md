---
name: btw
description: north — Captura rápida ("by the way"). Salva uma ideia/nota/lembrete/insight de reunião na inbox SEM quebrar o que está sendo feito, para revisar depois. O north relembra no fim do dia e no bom-dia seguinte. Ative para "/btw", "/capturar", "/ideia", "anota aí", "salva essa ideia", "não quero esquecer", "lembra disso", "ó, ideia:".
allowed-tools: Bash
argument-hint: "<sua ideia em uma frase>"
---

# /btw — Captura rápida (north)

Captura um pensamento no meio do fluxo e **volta imediatamente** ao que estava
sendo feito. Nada de derailing: é só registrar para não perder.

**Comportamento (rápido e leve):**

1. Pegue o texto que o usuário passou como argumento e capture:

   ```bash
   # macOS / Linux
   python3 ~/.claude/painel/run.py btw "<texto da ideia>"
   # Windows (PowerShell)
   python "$env:USERPROFILE\.claude\painel\run.py" btw "<texto da ideia>"
   ```

   (Instalou via npm? `north btw "<texto>"`. O projeto é inferido automaticamente
   do diretório atual; o tipo — ideia/reunião/todo/pergunta — é detectado do texto.)

2. Confirme em **UMA linha** (o id capturado + lembrete de que será relembrado no
   fim do dia). **Não** abra o painel, **não** acione squads, **não** comece a
   trabalhar na ideia.

3. **Se havia uma tarefa em andamento antes do `/btw`, retome-a** exatamente de onde
   parou. A captura é uma interrupção mínima, não uma troca de contexto.

**Regra de ouro:** capturar ≠ executar. A ideia fica guardada para decisão posterior
(no `/fim-do-dia` ou `/inbox`). Só comece a trabalhar nela se o usuário pedir
explicitamente.
