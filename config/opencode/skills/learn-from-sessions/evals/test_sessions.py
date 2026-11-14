#!/usr/bin/env python3
"""Test the sessions script against a store built for the test.

The real store is not a public interface, so the script is run against a
temporary database with the two tables it reads. Every assertion is about the
JSON contract `learn-from-sessions` and `scripts/hwt-wrapup` rely on.

Run it from anywhere:

    python3 config/opencode/skills/learn-from-sessions/evals/test_sessions.py
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "sessions"

SCHEMA = """
create table session_v2 (
  id text primary key,
  parent_id text,
  directory text not null,
  title text,
  time_created integer not null
);
create table session_message (
  session_id text not null,
  data text not null
);
"""


def make_store(root: Path) -> Path:
    """A store with a worktree session tree under `root`."""
    db = root / "opencode.db"
    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    work = root / "worktree"
    other = root / "elsewhere"
    rows = [
        ("ses_old", None, work, "first ask", 1000, ["a" * 10, "b" * 10]),
        ("ses_trigger", None, work, "trigger", 3000, ["c" * 5]),
        ("ses_child", "ses_trigger", work, "a subagent", 3100, ["d" * 7]),
        ("ses_grandchild", "ses_child", work, "a subagent's child", 3200, []),
        ("ses_nested", None, str(work / "nested"), "nested checkout", 2000, ["e"]),
        ("ses_elsewhere", None, other, "another repo", 4000, ["f" * 3]),
    ]
    for sid, parent, directory, title, created, messages in rows:
        con.execute(
            "insert into session_v2 (id, parent_id, directory, title, time_created)"
            " values (?, ?, ?, ?, ?)",
            (sid, parent, str(directory), title, created),
        )
        for data in messages:
            con.execute(
                "insert into session_message (session_id, data) values (?, ?)",
                (sid, data),
            )
    con.commit()
    con.close()
    return db


class SessionsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="sessions-test-"))
        self.work = self.root / "worktree"
        self.work.mkdir()
        self.db = make_store(self.root)
        self.env = dict(os.environ, OPENCODE_DB=str(self.db))

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=self.env,
            timeout=60,
        )

    def listing(self, *args: str) -> dict:
        proc = self.run_script("list", *args)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_list_reads_the_tree_with_counts_and_sizes(self) -> None:
        payload = self.listing("--directory", str(self.work))
        ids = [row["id"] for row in payload["sessions"]]
        self.assertEqual(
            ids, ["ses_old", "ses_nested", "ses_trigger", "ses_child", "ses_grandchild"]
        )
        by_id = {row["id"]: row for row in payload["sessions"]}
        self.assertEqual(by_id["ses_old"]["messages"], 2)
        self.assertEqual(by_id["ses_old"]["bytes"], 20)
        self.assertEqual(by_id["ses_child"]["parent_id"], "ses_trigger")
        self.assertFalse(payload["fallback"])
        self.assertNotIn("ses_elsewhere", ids)

    def test_exclude_tree_drops_the_trigger_and_its_children(self) -> None:
        payload = self.listing(
            "--directory", str(self.work), "--exclude-tree", "ses_trigger"
        )
        ids = [row["id"] for row in payload["sessions"]]
        self.assertEqual(ids, ["ses_old", "ses_nested"])

    def test_newest_is_the_newest_top_level_session(self) -> None:
        payload = self.listing("--directory", str(self.work))
        self.assertEqual(payload["newest"], "ses_trigger")

    def test_lookup_reports_where_a_session_lives(self) -> None:
        payload = self.listing("--directory", str(self.work), "--session", "ses_nested")
        self.assertEqual(
            payload["lookup"],
            {"id": "ses_nested", "directory": str(self.work / "nested")},
        )

    def test_lookup_of_an_unknown_session_is_null(self) -> None:
        payload = self.listing("--directory", str(self.work), "--session", "ses_nope")
        self.assertIsNone(payload["lookup"]["directory"])

    def test_an_unreadable_store_and_no_cli_exits_three(self) -> None:
        # A store with no tables cannot be read; hide the CLI so no fallback
        # can rescue it.
        broken = self.root / "broken.db"
        sqlite3.connect(broken).close()
        env = dict(self.env, OPENCODE_DB=str(broken), PATH="/nonexistent")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "list", "--directory", str(self.work)],
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 3)
        self.assertIn("sessions:", proc.stderr)

    def test_export_without_out_is_a_usage_error(self) -> None:
        proc = self.run_script("export", "ses_old")
        self.assertEqual(proc.returncode, 2)

    @unittest.skipUnless(shutil.which("opencode"), "opencode is not on PATH")
    def test_export_writes_the_file(self) -> None:
        listed = subprocess.run(
            ["opencode", "session", "list", "--format", "json", "-n", "1"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        try:
            session = json.loads(listed.stdout or "[]")[0]["id"]
        except (json.JSONDecodeError, IndexError, KeyError):
            self.skipTest("the real session store has no session to export")
        out = self.root / "transcripts" / f"{session}.json"
        proc = self.run_script("export", session, "--out", str(out))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(out.is_file())
        summary = json.loads(proc.stdout)
        self.assertEqual(summary["path"], str(out))
        self.assertEqual(summary["id"], session)
        self.assertGreater(summary["bytes"], 0)
        self.assertGreater(summary["messages"], 0)


if __name__ == "__main__":
    unittest.main()
