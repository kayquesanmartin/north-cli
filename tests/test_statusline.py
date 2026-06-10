# -*- coding: utf-8 -*-
"""Testes dos helpers da statusline (painel/cli.py).

Inclui regressao do bug real: _git_branch truncava branches com '/'
(feat/x -> x) por usar rsplit('/'). Stdlib unittest, sem deps externas.
"""
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from painel import cli  # noqa: E402

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def plain(s):
    return _ANSI.sub("", s)


class GitBranchTests(unittest.TestCase):
    def _repo(self, head_content):
        d = Path(tempfile.mkdtemp())
        git = d / ".git"
        git.mkdir()
        (git / "HEAD").write_text(head_content, encoding="utf-8")
        return d

    def test_simple_branch(self):
        d = self._repo("ref: refs/heads/main\n")
        self.assertEqual(cli._git_branch(str(d)), "main")

    def test_slashed_branch_name_preserved(self):
        # regressao: rsplit('/') truncava feat/x -> x
        d = self._repo("ref: refs/heads/feat/statusline-polish\n")
        self.assertEqual(cli._git_branch(str(d)), "feat/statusline-polish")

    def test_deep_slashed_branch(self):
        d = self._repo("ref: refs/heads/user/feature/sub\n")
        self.assertEqual(cli._git_branch(str(d)), "user/feature/sub")

    def test_detached_head_short_sha(self):
        d = self._repo("0123456789abcdef0123456789abcdef01234567\n")
        self.assertEqual(cli._git_branch(str(d)), "0123456")

    def test_walks_up_from_subdir(self):
        d = self._repo("ref: refs/heads/dev\n")
        sub = d / "src" / "deep"
        sub.mkdir(parents=True)
        self.assertEqual(cli._git_branch(str(sub)), "dev")

    def test_worktree_gitdir_file(self):
        d = Path(tempfile.mkdtemp())
        real = d / "realgit"
        real.mkdir()
        (real / "HEAD").write_text("ref: refs/heads/wt/branch\n", encoding="utf-8")
        wt = d / "wt"
        wt.mkdir()
        (wt / ".git").write_text("gitdir: {}\n".format(real), encoding="utf-8")
        self.assertEqual(cli._git_branch(str(wt)), "wt/branch")

    def test_not_a_repo(self):
        self.assertEqual(cli._git_branch(str(Path(tempfile.mkdtemp()))), "")

    def test_empty_cwd(self):
        self.assertEqual(cli._git_branch(""), "")


class WipStrTests(unittest.TestCase):
    STATE = {"wip": [{"project": "Acme", "count": 4, "limit": 3}]}

    def test_scoped_match(self):
        self.assertEqual(plain(cli._wip_str(self.STATE, "Acme")), "⚠WIP 4/3")

    def test_scoped_no_match(self):
        self.assertEqual(cli._wip_str(self.STATE, "Other"), "")

    def test_portfolio_count(self):
        self.assertEqual(plain(cli._wip_str(self.STATE, None)), "⚠WIP 1")

    def test_empty(self):
        self.assertEqual(cli._wip_str({"wip": []}, "Acme"), "")
        self.assertEqual(cli._wip_str({}, None), "")


class CtxMeterTests(unittest.TestCase):
    def test_none_is_empty(self):
        self.assertEqual(cli._ctx_meter(None, 1_000_000), "")

    def test_has_percent_and_bar(self):
        out = plain(cli._ctx_meter(80, 1_000_000))
        self.assertIn("%", out)


class StatuslineTextTests(unittest.TestCase):
    def _state(self):
        return {
            "wip": [], "focus": None,
            "projects": {"north": {
                "name": "north", "pct": 50, "alertsRisk": 0, "alertsWarn": 0,
                "next": {"id": "N1", "desc": "do it", "squad": "backend", "actionable": True}}},
            "totals": {"projects": 1, "alertsRisk": 0, "alertsWarn": 0},
        }

    def test_includes_model_and_next_action(self):
        hook = {"model": "Sonnet", "cwd": "/home/u/north", "remaining": None, "total": 1_000_000}
        line = plain(cli._statusline_text(self._state(), hook))
        self.assertIn("Sonnet", line)
        self.assertIn("N1", line)

    def test_stale_marker_present(self):
        hook = {"model": "", "cwd": "", "remaining": None, "total": 1_000_000}
        self.assertIn("⟳", plain(cli._statusline_text(self._state(), hook, stale=True)))

    def test_no_stale_marker_when_fresh(self):
        hook = {"model": "", "cwd": "", "remaining": None, "total": 1_000_000}
        self.assertNotIn("⟳", plain(cli._statusline_text(self._state(), hook, stale=False)))


if __name__ == "__main__":
    unittest.main()
