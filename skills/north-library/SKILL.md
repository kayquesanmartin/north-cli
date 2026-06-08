---
name: north-library
description: north — Biblioteca de referências de engenharia (local). Consulta e ancora mentoria/insights/docs em princípios curados (Clean Code, SOLID, DDD, TDD, CQRS, segurança…) que VOCÊ trouxe para ~/.north/library. Ative para "/north-library", "consulta a biblioteca", "o que o north sabe sobre X", "referência sobre <tópico>", "popular a biblioteca", "north library add".
allowed-tools: Bash, Read
argument-hint: "[find <tópico> | add <pasta> | list]"
---

# /north-library — Biblioteca de referências do north

O north mantém uma **biblioteca local** de referências de engenharia em
`~/.north/library/` (material seu, fora do pacote distribuído). Use-a para **ancorar
o que você ensina/orienta/documenta** em princípios sólidos — e **cite a fonte**.

## Comandos
```bash
python3 ~/.north/run.py library list                 # o que existe
python3 ~/.north/run.py library find "<tópico>"      # acha as referências relevantes
python3 ~/.north/run.py library add "<pasta>"        # popular/atualizar a biblioteca
# Windows: python "%USERPROFILE%\.north\run.py" library ...
```
(Com o PATH habilitado: `north library find "tdd"`.)

## Como usar (consulta ancorada — faça SEMPRE que puder)
Antes de orientar, ensinar um conceito, gerar um doc ou revisar arquitetura:
1. Rode `library find "<tópico do momento>"` (ex.: `clean architecture`, `cqrs`,
   `tdd`, `api design`, `cybersecurity`).
2. **Leia** o(s) arquivo(s) retornado(s) (caminhos impressos) com o Read e use o
   conteúdo para embasar a resposta — princípios, trade-offs, do/don't.
3. **Cite a referência** ("segundo `05-clean-code-solid.md` da sua biblioteca…"), para
   o aprendizado ficar rastreável. Se for PDF (ponteiro), aponte o arquivo p/ leitura.
4. Se a biblioteca **não** tiver o tópico, diga e siga com doc oficial (context7/
   microsoft-docs) — e sugira `north library add` se o usuário tiver material.

## Integração com as outras trilhas
- `/north-insight`: ao ensinar um conceito, ancore na biblioteca quando houver entrada.
- `/north-learn`, `/north-review`, `/north-codebase`: puxe o princípio relevante daqui.
- `/north-doc` (futuro): SDD/ADR citam as referências da biblioteca.

## Popular / manter
`north library add "<pasta>"` ingere `.md/.txt/.rst` (e indexa PDFs como ponteiro),
preservando subpastas, e reconstrói o índice. Rode de novo quando adicionar material.
Read-only sobre os planos do usuário; a biblioteca vive só em `~/.north/library/`.

## Aprender da web / context7 e salvar (enriquecimento)
Durante o desenvolvimento, se você buscar uma referência **atual** (WebSearch/WebFetch
ou context7/microsoft-docs) que valha guardar — ex.: best-practice nova de um framework,
um padrão atualizado — **ofereça salvar na biblioteca** para consultas futuras:
1. Escreva um resumo **seu** (não cole texto de terceiros verbatim) num `.md` com a fonte
   citada (URL/título), em `~/.north/library/<tema>.md`.
2. Reindexe: `python3 ~/.north/run.py library reindex`.
Assim o north "aprende" referências ao longo do tempo. Salve só com o aval do usuário e
sempre com a fonte citada; mantenha curto e autoral (evita problema de copyright).
