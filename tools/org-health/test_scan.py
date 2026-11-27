"""Tests of the parts of scan.py that decide what counts as healthy. Run: python3 -m unittest discover tools/org-health"""

import os
import subprocess
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scan  # noqa: E402


def fake_run(rc, err="", out="[]"):
    return lambda cmd, **kw: types.SimpleNamespace(returncode=rc, stdout=out, stderr=err)


@mock.patch("time.sleep", lambda s: None)
class ErrorsAreNotPasses(unittest.TestCase):
    def test_an_expected_absence_is_none(self):
        with mock.patch.object(subprocess, "run", fake_run(1, "gh: Not Found (HTTP 404)")):
            self.assertIsNone(scan.gh("repos/x/y", None, absent=(404,)))

    def test_an_unexpected_404_stops_the_scan(self):
        with mock.patch.object(subprocess, "run", fake_run(1, "gh: Not Found (HTTP 404)")):
            with self.assertRaises(scan.ScanError):
                scan.gh("repos/x/y", None)

    def test_a_refusal_is_not_retried(self):
        calls = []
        def run(cmd, **kw):
            calls.append(cmd)
            return types.SimpleNamespace(returncode=1, stdout="", stderr="gh: Forbidden (HTTP 403)")
        with mock.patch.object(subprocess, "run", run):
            with self.assertRaises(scan.ScanError):
                scan.gh("repos/x/y", None)
        self.assertEqual(len(calls), 1)

    def test_a_server_error_is_retried_then_stops(self):
        calls = []
        def run(cmd, **kw):
            calls.append(cmd)
            return types.SimpleNamespace(returncode=1, stdout="", stderr="gh: Server Error (HTTP 500)")
        with mock.patch.object(subprocess, "run", run):
            with self.assertRaises(scan.ScanError):
                scan.gh("repos/x/y", None)
        self.assertEqual(len(calls), 3)

    def test_a_failed_report_lookup_stops_instead_of_creating_a_duplicate(self):
        with mock.patch.object(subprocess, "run", fake_run(1, "gh: Bad credentials (HTTP 401)")):
            with self.assertRaises(scan.ScanError):
                scan.previous_state("token")


class MonthlyComment(unittest.TestCase):
    def setUp(self):
        self.state = {c: {} for c in scan.CHECKS}
        self.state["licence"] = {"a": "", "b": ""}
        self.changes = {c: {"new": [], "fixed": []} for c in scan.CHECKS}

    def test_a_quiet_month_still_mentions_the_duty_holder(self):
        text = scan.monthly_comment(self.state, self.changes, 46, True)
        self.assertTrue(text.startswith(f"@{scan.DUTY_HOLDER} "))
        self.assertIn("Nothing changed", text)

    def test_what_is_new_and_fixed_is_listed(self):
        self.changes["licence"] = {"new": ["b"], "fixed": ["c"]}
        text = scan.monthly_comment(self.state, self.changes, 46, True)
        self.assertIn("Newly failing", text)
        self.assertIn("`b`", text)
        self.assertIn("Fixed since the last scan: 1", text)

    def test_the_first_scan_says_so(self):
        self.assertIn("first scan", scan.monthly_comment(self.state, {}, 46, False))


if __name__ == "__main__":
    unittest.main()
