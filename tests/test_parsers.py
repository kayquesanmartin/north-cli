# -*- coding: utf-8 -*-
"""Testes dos parsers de markdown (painel/parsers.py): limpeza de descrição,
extração de tabela e chave de sprint."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from painel import parsers as P  # noqa: E402


class CleanDescTests(unittest.TestCase):
    def test_strips_markdown_link(self):
        self.assertEqual(P.clean_desc("[texto](http://x)"), "texto")

    def test_strips_emphasis_and_code(self):
        self.assertEqual(P.clean_desc("**bold** `code`"), "bold code")

    def test_collapses_whitespace(self):
        self.assertEqual(P.clean_desc("a    b\n c"), "a b c")

    def test_none_is_safe(self):
        self.assertEqual(P.clean_desc(None), "")


class ExtractTableTests(unittest.TestCase):
    TABLE = "\n".join([
        "preâmbulo",
        "| Conceito | Dificuldade |",
        "|---|---|",
        "| LINQ | pl |",
        "| async | sr |",
        "",
        "depois",
    ])

    def test_finds_rows_keyed_by_lower_header(self):
        header, rows = P.extract_table(self.TABLE, ["conceito", "dificuldade"])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["conceito"], "LINQ")
        self.assertEqual(rows[1]["dificuldade"], "sr")

    def test_no_match_returns_empty(self):
        header, rows = P.extract_table(self.TABLE, ["coluna-inexistente"])
        self.assertEqual(rows, [])


class SprintKeyTests(unittest.TestCase):
    # sprint_key normaliza com prefixo "S": "Sprint-CC1" -> "SCC1".
    def test_extracts_compound_key(self):
        self.assertEqual(P.sprint_key("Sprint-CC1 — Cálculo"), "SCC1")

    def test_extracts_numeric_key(self):
        self.assertEqual(P.sprint_key("Sprint 8"), "S8")

    def test_no_match_returns_none(self):
        self.assertIsNone(P.sprint_key("sem sprint aqui"))


if __name__ == "__main__":
    unittest.main()
