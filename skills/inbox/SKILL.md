---
name: inbox
description: north — Triagem da inbox de capturas. Lista as ideias/notas/lembretes salvos com /btw e ajuda a decidir cada um (validar/fazer agora, ou descartar). Ative para "/inbox", "minhas ideias", "o que eu anotei", "revisar capturas", "triar a inbox", "aquelas ideias que salvei".
allowed-tools: Bash, Read
argument-hint: ""
---

# /inbox — Triagem de capturas (north)

Revisa o que foi capturado com `/btw` e ajuda a dar destino a cada item.

**Passos:**

1. Liste os itens abertos:

   ```bash
   # macOS / Linux (Windows: python "$env:USERPROFILE\.north\run.py" inbox)
   python3 ~/.north/run.py inbox
   ```

   (Instalou via npm? `north inbox` em qualquer SO.)

2. Mostre a lista (id, tipo, texto, projeto, idade) ao usuário de forma organizada
   por tipo (💡 ideia · 🗣️ reunião · ✅ todo · ❓ pergunta).

3. Para cada item (ou em lote), **pergunte o destino** — não decida sozinho:
   - **Validar/fazer agora** → ofereça acionar o `tech-lead` ou o squad adequado
     para transformar a ideia em tarefa; ao concluir, marque feito:
     ```bash
     python3 ~/.north/run.py inbox-done <id>     # ou: north inbox-done <id>
     ```
   - **Descartar** (não faz mais sentido):
     ```bash
     python3 ~/.north/run.py inbox-dismiss <id>  # ou: north inbox-dismiss <id>
     ```
   - **Manter** → não faça nada; segue na inbox e será relembrado no próximo bom-dia.

4. Resuma ao final o que foi validado, descartado e o que ficou pendente.

**Regra:** a inbox é do dev. Você organiza e sugere, mas a decisão de validar ou
descartar é sempre dele.
