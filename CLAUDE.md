# CLAUDE.md — north-cli

Guia operacional para qualquer agente (Claude Code/Codex/Gemini) que trabalhe neste repo.
É curto de propósito: cada linha é uma regra que vale a pena seguir. Leia antes de codar.

---

## 1. O que é o north (entenda o produto antes de mexer)

north é um **copiloto de produtividade multi-projeto** para CLIs de IA. Ele descobre seus
projetos, mostra foco do dia, sinais vitais e um painel — lendo seus planos
(plan-build / GSD `.planning/`) para te orientar.

Arquitetura: **engine Python** (`src/painel/`) instalado uma vez em `~/.north`, embrulhado
por um **launcher npm cross-platform** (`bin/north.js`) distribuído como `north-cli`.

### north é IA-first
Todo comando é uma **skill invocável dentro do runtime** (Claude Code/Codex/Gemini) —
essa é a superfície principal. O terminal (`north <cmd>`) é um caminho **equivalente e
secundário**: nenhum comando pode existir só no terminal. O `CMDSPEC` em `runtimes.py` é
a **fonte de verdade** dos comandos; toda capability nova vira skill nos 3 runtimes
(e ganha um `skills/<nome>/SKILL.md` próprio quando precisa de instruções ricas).

### Invariante sagrado — north é READ-ONLY sobre os planos do usuário
north **lê** os planos/projetos do usuário e **nunca os edita**. Nenhuma feature pode
escrever, mover ou deletar arquivos dentro dos projetos descobertos. O único lugar onde
o north escreve é a própria casa dele (`~/.north`, config, dashboard gerado) e a inbox.
Se uma ideia exige escrever no projeto do usuário, a ideia está errada — repense.

---

## 2. Como pensar antes de cada feature (estreite o pensamento aqui)

Toda feature começa pelo **usuário final e pelo fluxo**, não pela implementação.
Antes de escrever código, responda em voz alta:

1. **Qual o comando?** Como a pessoa dispara isso? (`north <quê>` / qual skill?)
2. **Qual o output?** O que ela vê? A mensagem é clara sem ler a doc?
3. **Qual o fluxo completo?** Primeiro uso, uso recorrente, e o caso de erro.
4. **Funciona nos 3 runtimes?** Claude Code, Codex e Gemini têm paridade?
5. **É cross-platform?** Roda igual em Windows, macOS e Linux?
6. **Respeita o read-only?** Não toca nos planos do usuário?
7. **Precisa de config?** Se sim, tem um default sensato pra funcionar sem configurar?

Se algum item não tem resposta boa, **não comece a codar** — alinhe primeiro.

### Princípios de UX (CLI é interface)
- **Defaults > configuração.** Funciona out-of-the-box; configurar é opcional.
- **Falha nunca é silenciosa.** Erro mostra causa e próximo passo, não stack trace cru.
- **Mensagens ao usuário final em pt-BR, claras e curtas.** Não deveria precisar do README.
- **Idempotência.** Rodar de novo não quebra nem duplica.

---

## 3. Restrições técnicas (são contrato, não preferência)

- **Engine stdlib-only.** Zero dependências externas em Python. Só `os`, `pathlib`,
  `json`, `re`, `subprocess`, `datetime`, `io`, `contextlib`, etc. Não adicione `pip install`.
- **Python 3.8+.** O CI testa 3.8 e 3.12. Nada de `match/case` (3.10+) nem sintaxe nova.
- **Launcher Node >= 14.** `bin/north.js` só detecta o Python e delega — sem lógica de negócio.
- **Cross-platform sempre.** Use `pathlib`/`os.path`, nunca paths com `/` ou `\` hardcoded,
  nunca assuma bash/PowerShell. Teste mentalmente nos 3 SOs.
- **Idioma — inglês no código, pt-BR no produto.** Branch, mensagens de commit, nomes de
  comandos/skills, identificadores, arquivos e comentários: **inglês**. O que é voltado ao
  usuário final (output do CLI, descrições de skill, READMEs já em EN): segue o idioma do produto.
- **Sem dados pessoais embutidos.** Nome do dono, caminhos locais, e-mails ficam em config,
  nunca no código do engine.

---

## 4. Git — como versionamos

### Branches (sempre)
Trabalho não-trivial **nunca** vai direto na `main`. Crie uma branch por unidade de trabalho,
nomeada pelo que resolve: `tipo/descricao-curta`.
- `feat/inbox-filters`, `fix/ci-bytecode-gate`, `docs/claude-md`, `refactor/discovery-adapters`, `chore/bump-actions`

### Commits
- **NUNCA adicione co-author.** Sem trailer `Co-Authored-By`. Sem "Generated with".
- **Conventional Commits, em inglês:** `type(scope): description in the imperative`.
  Tipos: `feat`, `fix`, `docs`, `refactor`, `chore`, `ci`, `test`, `release`, `perf`.
  Escopos comuns: `install`, `discovery`, `statusline`, `painel`, `inbox`, `gsd`, `config`.
- **Curto e direto: o assunto basta.** Uma linha no imperativo, ~50 (máx. 72) caracteres,
  o mínimo de informação sem perder o contexto do que foi feito. Sem ponto final.
- **Corpo é exceção, não regra.** Só quando o *porquê* não é óbvio e importa (1–2 linhas).
  Nunca narre o diff em bullets — o diff já mostra o quê.
- **Commits atômicos.** Uma mudança coerente por commit. Working tree limpo antes de trocar de contexto.

### SemVer honesto
- `patch` (0.0.x): fix, docs, infra/CI — nada novo pro usuário.
- `minor` (0.x.0): nova capability voltada ao usuário.
- `major` (x.0.0): breaking change (formato de config, comando removido, etc.).

---

## 5. Qualidade — gates inegociáveis

- **Valide local antes de pushar:** `python -m compileall -q install.py runtimes.py src`,
  `npm pack` (tarball limpo), e o smoke de install num HOME isolado.
- **Verifique o artefato, não o log que o produziu.** (Lição real: o gate de bytecode
  do CI grepava o stdout do `prepack` e false-falhava; o certo é inspecionar o `.tgz` com `tar tzf`.)
- **CI verde é gate de release.** Não corta versão com CI vermelho.
- **Tarball nunca leva bytecode.** `prepack` (`bin/clean-pycache.js`) limpa `__pycache__`/`.pyc`;
  o job `package` do CI confirma.

---

## 6. Release (fluxo)

1. Bump `version` em `package.json`.
2. Mova `[Unreleased]` → `[X.Y.Z] - AAAA-MM-DD` no `CHANGELOG.md` (Keep a Changelog) e ajuste os links.
3. Commit `release: X.Y.Z — ...`, tag `vX.Y.Z`, push da branch + tag.
4. Publish via **OIDC trusted publishing** (`release.yml`): **dry-run primeiro**, depois `dry_run=false`.
   Sem `NPM_TOKEN` — a confiança é o repo+workflow registrados no npmjs.com.
5. Confirme na fonte: `npm view north-cli version`.

---

## 7. Mapa do repo (orientação rápida)

| Caminho | O quê |
|---|---|
| `src/painel/cli.py`        | entrada do engine, roteamento de comandos |
| `src/painel/discovery.py`  | descoberta de projetos + source adapters |
| `src/painel/parsers.py`    | leitura de planos (plan-build) |
| `src/painel/gsd.py`        | adapter de projetos GSD (`.planning/`) |
| `src/painel/render.py`     | renderização do painel/dashboard |
| `src/painel/health.py`     | sinais vitais / alertas |
| `src/painel/focus.py`      | foco do dia |
| `src/painel/inbox.py`      | captura rápida (`/north-note`) + inbox |
| `src/painel/rituals.py`    | rituais (bom-dia / fim-do-dia) |
| `src/painel/config.py`     | config (`north config`/`status`) |
| `bin/north.js`             | launcher npm cross-platform |
| `install.py` / `runtimes.py` | instalador multi-runtime (Claude/Codex/Gemini) |
| `skills/`                  | comandos: focus, note, inbox, panel, morning, wrap-up, status, config, learn/review/test (mentor), uninstall |

---

## 8. Definition of Done

- [ ] Passa o checklist de fluxo (seção 2) — pensei como usuário final.
- [ ] Cross-platform e paridade multi-runtime onde aplicável.
- [ ] Não viola o read-only sobre planos do usuário.
- [ ] Stdlib-only, compatível com Python 3.8.
- [ ] `compileall` + `npm pack` limpos localmente.
- [ ] Branch própria, commits conventional, sem co-author.
- [ ] CHANGELOG atualizado se muda algo visível ao usuário.
