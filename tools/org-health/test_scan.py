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

    def test_a_403_that_says_the_feature_is_off_is_an_absence(self):
        err = "gh: Dependabot alerts are disabled for this repository. (HTTP 403)"
        with mock.patch.object(subprocess, "run", fake_run(1, err)):
            self.assertIsNone(scan.gh("repos/x/y/dependabot/alerts", None, absent=(403, 404)))

    def test_a_rate_limit_403_is_retried_then_stops_not_an_absence(self):
        calls = []

        def run(cmd, **kw):
            calls.append(cmd)
            return types.SimpleNamespace(returncode=1, stdout="", stderr="gh: API rate limit exceeded for installation ID 1. (HTTP 403)")

        with mock.patch.object(subprocess, "run", run):
            with self.assertRaises(scan.ScanError):
                scan.gh("repos/x/y/dependabot/alerts", None, absent=(403, 404))
        self.assertEqual(len(calls), 3)

    def test_a_secondary_rate_limit_is_not_an_absence_either(self):
        err = "gh: You have exceeded a secondary rate limit. Please wait a few minutes before you try again. (HTTP 403)"
        with mock.patch.object(subprocess, "run", fake_run(1, err)):
            with self.assertRaises(scan.ScanError):
                scan.gh("repos/x/y/code-scanning/analyses", None, absent=(403, 404))

    def test_a_403_for_a_missing_app_permission_stops_the_scan(self):
        err = "gh: Resource not accessible by integration (HTTP 403)"
        with mock.patch.object(subprocess, "run", fake_run(1, err)):
            with self.assertRaises(scan.ScanError):
                scan.gh("repos/x/y/dependabot/alerts", None, absent=(403, 404))

    def test_a_failed_report_lookup_stops_instead_of_creating_a_duplicate(self):
        with mock.patch.object(subprocess, "run", fake_run(1, "gh: Bad credentials (HTTP 401)")):
            with self.assertRaises(scan.ScanError):
                scan.previous_state("token")


class CacheCheck(unittest.TestCase):
    GB = 2**30

    def setUp(self):
        scan.NOT_CHECKED.clear()

    def gh_returning(self, usage_gb, limit_response):
        def gh(path, token, paginate=False, absent=()):
            if "/actions/cache/usage" in path:
                return {"active_caches_size_in_bytes": int(usage_gb * self.GB)}
            if "/actions/cache/storage-limit" in path:
                if isinstance(limit_response, Exception):
                    raise limit_response
                return limit_response
            if "/branches?" in path:
                return [{"name": "main"}]
            if "/community/profile" in path:
                return {"files": {"readme": {}}}
            if "/pulls?" in path or "/dependabot/alerts" in path:
                return []
            return None
        return gh

    def scan_repo_with(self, usage_gb, limit_response=None):
        repo = {"name": "r", "default_branch": "main", "license": {"spdx_id": "MIT"}}
        with mock.patch.object(scan, "gh", self.gh_returning(usage_gb, limit_response)):
            return scan.scan_repo(repo, None)

    def test_above_80_percent_of_the_default_limit_is_reported_with_its_size(self):
        self.assertEqual(self.scan_repo_with(9.9)["cache"], "9.9 of 10 GB")

    def test_below_80_percent_is_not_reported(self):
        self.assertNotIn("cache", self.scan_repo_with(7.9))

    def test_a_configured_larger_limit_is_used(self):
        self.assertNotIn("cache", self.scan_repo_with(9.9, {"max_cache_size_gb": 150}))
        self.assertEqual(self.scan_repo_with(130, {"max_cache_size_gb": 150})["cache"], "130.0 of 150 GB")

    def test_where_no_limit_is_configured_the_default_is_used(self):
        # gh() returns None for the expected answers (402: a paid feature; 404), and a response without the field is
        # the same as no configured limit
        self.assertEqual(self.scan_repo_with(9.9, None)["cache"], "9.9 of 10 GB")
        self.assertEqual(self.scan_repo_with(9.9, {"unexpected": "shape"})["cache"], "9.9 of 10 GB")

    def test_an_unexpected_failure_to_read_the_limit_stops_the_scan_not_a_guess(self):
        with self.assertRaises(scan.ScanError):
            self.scan_repo_with(9.9, scan.ScanError("gh api: Server Error (HTTP 500)"))

    def test_the_402_of_a_free_plan_is_asked_for_as_an_expected_absence(self):
        seen = {}

        def gh(path, token, paginate=False, absent=()):
            if "/storage-limit" in path:
                seen["absent"] = absent
            return None

        with mock.patch.object(scan, "gh", gh):
            scan.cache_limit_bytes("repos/o/r", None)
        self.assertIn(402, seen["absent"])
        self.assertIn(404, seen["absent"])
        self.assertNotIn(403, seen["absent"])

    def test_a_missing_app_permission_skips_this_check_and_says_so(self):
        with mock.patch.object(scan, "gh", side_effect=scan.ScanError("gh api: Resource not accessible by integration (HTTP 403)")):
            self.assertIsNone(scan.cache_usage("repos/o/r", None))
        self.assertIn("cache", scan.NOT_CHECKED)

    def test_any_other_failure_still_stops_the_scan(self):
        with mock.patch.object(scan, "gh", side_effect=scan.ScanError("gh api: Server Error (HTTP 500)")):
            with self.assertRaises(scan.ScanError):
                scan.cache_usage("repos/o/r", None)

    def test_the_report_names_a_check_that_could_not_be_made(self):
        scan.NOT_CHECKED.add("cache")
        text = scan.render({c: {} for c in scan.CHECKS}, {}, [], {}, 3)
        self.assertIn("Not checked", text)
        self.assertIn("last known result", text)

    def test_a_skipped_check_keeps_its_last_known_result_and_is_not_reported_as_fixed(self):
        import contextlib
        import io

        def scan_repo(repo, token):
            scan.NOT_CHECKED.add("cache")  # this month the App cannot read the cache
            return {}

        repos = [{"name": "r", "default_branch": "main", "archived": False, "visibility": "public"}]
        before = {"cache": {"r": "9.9 of 10 GB"}}
        out = io.StringIO()
        with mock.patch.object(scan, "gh", return_value=repos), \
             mock.patch.object(scan, "scan_repo", scan_repo), \
             mock.patch.object(scan, "load_exceptions", return_value=({}, [])), \
             mock.patch.object(scan, "previous_state", return_value=(5, before)), \
             contextlib.redirect_stdout(out):
            scan.scan(types.SimpleNamespace(dry_run=True, summary_file=None))
        text = out.getvalue()
        self.assertNotIn("Fixed since", text)
        self.assertIn("`r` (9.9 of 10 GB)", text)  # still listed as it was last month
        self.assertIn("Nothing changed", text)


class OnlyPublicActiveRepositories(unittest.TestCase):
    """The report is public, so a non-public repository must never be scanned or named."""

    def test_private_internal_and_archived_repositories_are_left_out(self):
        listing = [
            {"name": "open", "archived": False, "visibility": "public", "private": False},
            {"name": "secret", "archived": False, "visibility": "private", "private": True},
            {"name": "staff", "archived": False, "visibility": "internal", "private": False},
            {"name": "old", "archived": True, "visibility": "public", "private": False},
            {"name": "no-visibility-field-private", "archived": False, "private": True},
            {"name": "no-visibility-field-public", "archived": False, "private": False},
        ]
        names = [r["name"] for r in scan.select_repos(listing)]
        self.assertEqual(names, ["open", "no-visibility-field-public"])


class EmptyRepository(unittest.TestCase):
    """An empty repository has no default branch; it must be reported, not abort the whole scan."""

    def scan_with(self, branches, default):
        asked = []

        def gh(path, token, paginate=False, absent=()):
            asked.append(path)
            if "/branches?" in path:
                return branches
            if "/community/profile" in path:
                return {"files": {"readme": {}}}
            if "/pulls?" in path or "/dependabot/alerts" in path:
                return []
            return None

        repo = {"name": "r", "default_branch": default, "license": {"spdx_id": "MIT"}}
        with mock.patch.object(scan, "gh", gh):
            return scan.scan_repo(repo, None), asked

    def test_an_empty_repository_is_reported_and_does_not_stop_the_scan(self):
        failed, asked = self.scan_with([], None)
        self.assertIn("empty", failed)
        self.assertNotIn("protection", failed)
        self.assertFalse([p for p in asked if "/branches/" in p or "/commits" in p])

    def test_a_branch_name_is_encoded_in_the_urls(self):
        _, asked = self.scan_with([{"name": "release#1/x"}], "release#1/x")
        branch_calls = [p for p in asked if "/branches/" in p or "/commits?" in p]
        self.assertTrue(branch_calls)
        for p in branch_calls:
            self.assertIn("release%231%2Fx", p)
            self.assertNotIn("release#1", p)

    def test_a_repository_with_a_branch_is_not_empty(self):
        failed, _ = self.scan_with([{"name": "main"}], "main")
        self.assertNotIn("empty", failed)


class NotificationBeforeBaseline(unittest.TestCase):
    """The baseline for the next scan is in the issue body: it must move only after the comment has been posted."""

    def run_scan(self, fail_on=None):
        calls = []

        def run(cmd, **kw):
            calls.append(cmd)
            if fail_on and fail_on in cmd and kw.get("check"):
                raise subprocess.CalledProcessError(1, cmd)
            return types.SimpleNamespace(returncode=0, stdout="", stderr="")

        repo = [{"name": "a", "default_branch": "main", "archived": False}]
        with mock.patch.object(scan, "gh", return_value=repo), \
             mock.patch.object(scan, "scan_repo", return_value={}), \
             mock.patch.object(scan, "load_exceptions", return_value=({}, [])), \
             mock.patch.object(scan, "previous_state", return_value=(5, {"licence": {"x": ""}})), \
             mock.patch.object(subprocess, "run", run):
            try:
                scan.scan(types.SimpleNamespace(dry_run=False, summary_file=None))
                error = None
            except subprocess.CalledProcessError as e:
                error = e
        return [c[2] for c in calls if c[:2] == ["gh", "issue"]], error

    def test_the_comment_comes_before_the_edit(self):
        verbs, error = self.run_scan()
        self.assertIsNone(error)
        self.assertLess(verbs.index("comment"), verbs.index("edit"))

    def test_a_failed_comment_leaves_the_baseline_alone(self):
        verbs, error = self.run_scan(fail_on="comment")
        self.assertIsNotNone(error)
        self.assertNotIn("edit", verbs)


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
