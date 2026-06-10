# -*- coding: utf-8 -*-
"""Testes do motor de insights (painel/insights.py): catálogo, devido,
cooldown, ranking e isolamento por namespace (libs vs linguagem)."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from painel import insights as I  # noqa: E402


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())   # ledger isolado; catálogo vem do repo

    def test_csharp_catalog_loads(self):
        cat = I.load_catalog(self.home, "csharp")
        self.assertIn("linq", cat)
        self.assertEqual(cat["linq"]["difficulty"], "pl")

    def test_unknown_lang_is_empty(self):
        self.assertEqual(I.load_catalog(self.home, "klingon-xyz"), {})


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())

    def test_new_concept_is_due(self):
        res = I.check(self.home, "csharp", ["LINQ"])
        self.assertEqual([d["concept"] for d in res["due"]], ["LINQ"])
        self.assertEqual(res["due"][0]["reason"], "novo")

    def test_recorded_concept_not_due_within_cooldown(self):
        I.check(self.home, "csharp", ["LINQ"])
        I.record(self.home, "csharp", "LINQ")
        res = I.check(self.home, "csharp", ["LINQ"])
        self.assertEqual(res["due"], [])

    def test_ranked_by_difficulty(self):
        # async/await = sr deve vir antes de if/else = jr
        res = I.check(self.home, "csharp", ["if/else", "async/await"])
        self.assertEqual(res["due"][0]["concept"], "async/await")

    def test_min_level_filters_below(self):
        res = I.check(self.home, "csharp", ["if/else"], min_level="sr")
        self.assertEqual(res["due"], [])      # if/else é jr, abaixo de sr

    def test_unknown_concept_defaults_pl_geral(self):
        res = I.check(self.home, "csharp", ["FooBarLib123"])
        self.assertEqual(res["due"][0]["difficulty"], "pl")
        self.assertEqual(res["due"][0]["category"], "geral")


class NamespaceIsolationTests(unittest.TestCase):
    def test_record_in_one_ns_does_not_affect_another(self):
        home = Path(tempfile.mkdtemp())
        # "MediatR" ensinado no namespace de libs
        I.check(home, "dotnet-libs", ["MediatR"])
        I.record(home, "dotnet-libs", "MediatR")
        # no namespace de linguagem, "MediatR" continua novo (ledger separado)
        res = I.check(home, "csharp", ["MediatR"])
        self.assertEqual([d["concept"] for d in res["due"]], ["MediatR"])


if __name__ == "__main__":
    unittest.main()
