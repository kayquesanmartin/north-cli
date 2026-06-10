# -*- coding: utf-8 -*-
"""Testes do motor de DIREÇÃO (painel/focus.py): scoring, pick, WIP, squad."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from painel import focus as F  # noqa: E402
from painel import parsers as P  # noqa: E402


def _task(tid, col, sprint="S1", blocked=False, deps="", desc="task"):
    return {"id": tid, "col": col, "sprint": sprint, "blocked": blocked,
            "deps": deps, "desc": desc, "status_raw": ""}


def _proj(pid, tasks, current_sprint="S1", mine=None):
    return {"id": pid, "name": pid, "color": "#000", "tasks": tasks,
            "sprints": [{"key": "S1"}], "current_sprint": current_sprint,
            "mine": mine or {}, "alerts": []}


class SuggestSquadTests(unittest.TestCase):
    def test_qa(self):
        self.assertEqual(F.suggest_squad("escrever testes xunit"), "squad-qa")

    def test_frontend(self):
        self.assertEqual(F.suggest_squad("criar a tela em react"), "squad-frontend")

    def test_security(self):
        self.assertEqual(F.suggest_squad("validar jwt e oauth"), "squad-security")

    def test_backend_is_default(self):
        self.assertEqual(F.suggest_squad("algo sem palavra-chave"), "squad-backend")


class ScoreTaskTests(unittest.TestCase):
    def test_done_is_none(self):
        self.assertIsNone(F.score_task(_task("T", P.COL_DONE), {"S1"}))

    def test_in_progress_base(self):
        score, _ = F.score_task(_task("T", P.COL_ANDAMENTO, sprint="S2"), set())
        self.assertEqual(score, 100)

    def test_current_sprint_bonus(self):
        score, reasons = F.score_task(_task("T", P.COL_ANDAMENTO), {"S1"})
        self.assertEqual(score, 150)
        self.assertIn("sprint atual", reasons)

    def test_blocked_penalty(self):
        score, reasons = F.score_task(_task("T", P.COL_ANDAMENTO, blocked=True), set())
        self.assertLess(score, 0)
        self.assertIn("BLOQUEADA", reasons)

    def test_planejado_unblocked_bonus(self):
        score, reasons = F.score_task(_task("T", P.COL_PLANEJADO, sprint="S2"), set())
        self.assertEqual(score, 55)            # 40 + 15
        self.assertIn("desbloqueada", reasons)

    def test_planejado_with_dep_penalty(self):
        score, _ = F.score_task(_task("T", P.COL_PLANEJADO, sprint="S2", deps="T1"), set())
        self.assertEqual(score, 15)            # 40 - 25


class ComputeFocusTests(unittest.TestCase):
    def test_picks_highest_actionable(self):
        p = _proj("proj", [_task("A", P.COL_PLANEJADO), _task("B", P.COL_ANDAMENTO)])
        self.assertEqual(F.compute_focus([p])["pick"]["task"]["id"], "B")

    def test_blocked_not_picked_when_actionable_exists(self):
        p = _proj("proj", [_task("A", P.COL_ANDAMENTO, blocked=True),
                           _task("B", P.COL_PLANEJADO)])
        self.assertEqual(F.compute_focus([p])["pick"]["task"]["id"], "B")

    def test_wip_alert_over_limit(self):
        tasks = [_task("T%d" % i, P.COL_ANDAMENTO) for i in range(F.WIP_LIMIT + 1)]
        res = F.compute_focus([_proj("proj", tasks)])
        self.assertTrue(res["wip_alerts"])
        self.assertEqual(res["wip_alerts"][0]["count"], F.WIP_LIMIT + 1)

    def test_no_wip_alert_at_limit(self):
        tasks = [_task("T%d" % i, P.COL_ANDAMENTO) for i in range(F.WIP_LIMIT)]
        self.assertFalse(F.compute_focus([_proj("proj", tasks)])["wip_alerts"])


if __name__ == "__main__":
    unittest.main()
