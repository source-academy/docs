#!/usr/bin/env python3
"""Monthly health scan of the source-academy organisation (documentation#66).

Read-only: it reads repositories with READ_TOKEN (the token of the source-academy-health GitHub App;
without it, the ambient `gh` login) and writes only one issue, "Organisation health", in this
repository with WRITE_TOKEN (the workflow's GITHUB_TOKEN). The issue is edited in place; a comment is
added only when something is newly failing, so a quiet month is silent.

    python3 tools/org-health/scan.py --dry-run     # print the report, write nothing
"""

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import tomllib
import urllib.parse

ORG = "source-academy"
DUTY_HOLDER = "martin-henz"  # assigned and mentioned every month; change on handover (see README)
REPORT_REPO = f"{ORG}/docs"
LABEL = "org-health"
TITLE = "Organisation health"
MARKER = "<!-- org-health-state:"
HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = dt.datetime.now(dt.timezone.utc)

# check id: what a failing repository looks like. Keep this list short: a report that is read has few
# checks, each with a threshold.
CHECKS = {
    "licence": "No licence",
    "readme": "No README",
    "protection": "Default branch not protected (no branch protection and no ruleset)",
    "alerts": "Open high or critical Dependabot alerts",
    "scanning": "Code scanning not set up",
    "stale-prs": "Open pull requests older than six months",
    "branches": "More than 30 branches",
    "inactive": "No push for over a year (archive, or say who maintains it)",
    "empty": "Empty repository, no commits (delete it, or push something)",
    "cache": "Actions cache above 80% of its limit (builds slow down when it is evicted; see the cleanup workflow)",
}
MAX_BRANCHES = 30
DEFAULT_CACHE_LIMIT_BYTES = 10 * 2**30  # the default size of a repository's Actions cache
CACHE_WARN = 0.8
# Checks that could not be made, for example because the GitHub App lacks a permission: the report says so,
# and the scan carries on (one missing permission must not stop the whole monthly scan).
NOT_CHECKED = set()
STALE_DAYS = 180
INACTIVE_DAYS = 365


class ScanError(Exception):
    """A call failed in a way that the scan must not read as 'healthy': the scan stops and writes nothing."""


# A 403 means three different things: a feature that is switched off for the repository (an expected absence),
# a rate limit (wait and ask again), or an App that lacks a permission (a failure of the scan). Only the first is
# an absence; telling them apart is by the message.
RATE_LIMITED = re.compile(r"rate limit|abuse detection|too many requests", re.I)
FEATURE_OFF = re.compile(r"disabled|not enabled|must be enabled|no analysis found|not found", re.I)


def run_gh(cmd, token, absent=()):
    """Runs `gh`, retrying transient failures (server errors, rate limits). Returns stdout, or None if the call
    failed with a status in `absent` and, for a 403, with a message that says the feature is off. Any other
    failure raises ScanError."""
    env = dict(os.environ, **({"GH_TOKEN": token} if token else {}))
    for attempt in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if r.returncode == 0:
            return r.stdout
        m = re.search(r"HTTP (\d{3})", r.stderr)
        status = int(m.group(1)) if m else None
        rate_limited = status in (403, 429) and bool(RATE_LIMITED.search(r.stderr))
        if status in absent and not rate_limited and (status != 403 or FEATURE_OFF.search(r.stderr)):
            return None
        if rate_limited:
            time.sleep(30 * (attempt + 1))  # a limit is lifted by waiting
            continue
        if status is not None and status < 500 and status != 429:
            break  # a refusal will not change by asking again
        time.sleep(2 + 3 * attempt)
    raise ScanError(f"{' '.join(cmd[:3])}: {r.stderr.strip()[:200]}")


def gh(path, token, paginate=False, absent=()):
    """The JSON of a GitHub API call; None only if it failed with a status in `absent`."""
    out_text = run_gh(["gh", "api", path] + (["--paginate"] if paginate else []), token, absent)
    if out_text is None:
        return None
    text = out_text.strip()
    if not paginate:
        return json.loads(text) if text else None
    out, dec, i = [], json.JSONDecoder(), 0
    while i < len(text):  # --paginate prints one JSON document per page
        value, i = dec.raw_decode(text, i)
        out.extend(value) if isinstance(value, list) else out.append(value)
        while i < len(text) and text[i].isspace():
            i += 1
    return out


def days(iso):
    return (TODAY - dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))).days


def cache_limit_bytes(r, token):
    """The size limit of a repository's Actions cache: the configured one where GitHub reports it (a paid plan can
    raise it), else the default of 10 GB. Only the expected answers mean "no configured limit": 402 (the endpoint
    is a paid feature) and 404. Any other failure stops the scan, as everywhere: a limit that could not be read
    must not turn into a guess that makes a healthy repository look full."""
    data = gh(f"{r}/actions/cache/storage-limit", token, absent=(402, 404))
    gb = data.get("max_cache_size_gb") if isinstance(data, dict) else None
    return int(gb * 2**30) if isinstance(gb, (int, float)) and gb > 0 else DEFAULT_CACHE_LIMIT_BYTES


def cache_usage(r, token):
    """(bytes used, limit in bytes) of a repository's Actions cache, or None if the App may not read it (it needs
    Actions: read): then the check is recorded as not made, and the scan carries on."""
    try:
        usage = gh(f"{r}/actions/cache/usage", token)
    except ScanError as e:
        if "Resource not accessible by integration" not in str(e):
            raise
        NOT_CHECKED.add("cache")
        return None
    if not usage:
        return None
    return usage["active_caches_size_in_bytes"], cache_limit_bytes(r, token)


def scan_repo(repo, token):
    """The failing checks of one repository, each with a short detail."""
    name, default = repo["name"], repo["default_branch"]
    ref = urllib.parse.quote(default or "", safe="")  # a branch name goes into a URL: # and % need encoding
    r = f"repos/{ORG}/{name}"
    failed = {}
    if not repo.get("license"):
        failed["licence"] = ""
    profile = gh(f"{r}/community/profile", token)
    if profile is not None and not (profile.get("files") or {}).get("readme"):
        failed["readme"] = ""
    # An empty repository has no branches and no default branch to look at: it is a finding of its own,
    # and the checks that need a branch are skipped for it.
    branches = gh(f"{r}/branches?per_page=100", token, paginate=True)
    empty = not branches or not default
    if empty:
        failed["empty"] = ""
    else:
        branch = gh(f"{r}/branches/{ref}", token)
        rules = gh(f"{r}/rules/branches/{ref}", token, absent=(404,))
        if not ((branch and branch.get("protected")) or rules):
            failed["protection"] = ""
    alerts = gh(f"{r}/dependabot/alerts?state=open&severity=critical,high&per_page=100", token, paginate=True, absent=(403, 404))
    if alerts is None:  # Dependabot alerts are switched off for this repository
        failed["alerts"] = "alerts are off"
    elif alerts:
        failed["alerts"] = str(len(alerts))
    setup = gh(f"{r}/code-scanning/default-setup", token, absent=(403, 404))
    analyses = gh(f"{r}/code-scanning/analyses?per_page=1", token, absent=(403, 404))
    if not ((setup and setup.get("state") == "configured") or analyses):
        failed["scanning"] = ""
    prs = gh(f"{r}/pulls?state=open&per_page=100", token, paginate=True)
    stale = [p for p in prs if days(p["created_at"]) > STALE_DAYS]
    if stale:
        failed["stale-prs"] = f"{len(stale)} of {len(prs)}"
    if len(branches) > MAX_BRANCHES:
        failed["branches"] = str(len(branches))
    if not empty:
        # The last commit on the default branch, not `pushed_at`: that moves when anyone pushes a branch.
        latest = gh(f"{r}/commits?sha={ref}&per_page=1", token, absent=(409,))  # 409: no commits
        if latest and days(latest[0]["commit"]["committer"]["date"]) > INACTIVE_DAYS:
            failed["inactive"] = f"{days(latest[0]['commit']['committer']['date']) // 30} months"
    cache = cache_usage(r, token)
    if cache is not None and cache[0] > CACHE_WARN * cache[1]:
        failed["cache"] = f"{cache[0] / 2**30:.1f} of {cache[1] // 2**30} GB"
    return failed


def load_exceptions():
    path = os.path.join(HERE, "health-exceptions.toml")
    with open(path, "rb") as f:
        items = tomllib.load(f).get("exception", [])
    active, expired = {}, []
    for e in items:
        if dt.date.fromisoformat(str(e["expires"])) >= TODAY.date():
            active[(e["repo"], e["check"])] = e["reason"]
        else:
            expired.append(e)
    return active, expired


def render(state, exceptions_used, expired, changes, repos_total):
    lines = [f"Scanned **{repos_total}** active repositories on {TODAY:%d %B %Y}. Read-only: "
             "[`tools/org-health`](https://github.com/source-academy/docs/tree/main/tools/org-health).", ""]
    lines += ["| check | failing | change |", "| --- | --- | --- |"]
    skipped = [CHECKS[c] for c in CHECKS if c in NOT_CHECKED]
    for c, title in CHECKS.items():
        n = len(state.get(c, {}))
        ch = changes.get(c, {"new": [], "fixed": []})
        delta = ", ".join(filter(None, [f"+{len(ch['new'])} new" if ch["new"] else "", f"-{len(ch['fixed'])} fixed" if ch["fixed"] else ""])) or "no change"
        if not changes:  # no earlier report to compare with: "no change" would say something that was not checked
            delta = "first scan"
        lines.append(f"| {title} | {n} | {delta} |")
    if skipped:
        lines += ["", "**Not checked** (the GitHub App lacks a permission, see the README of `tools/org-health`; the table shows the last known result): " + "; ".join(skipped)]
    for c, title in CHECKS.items():
        repos = state.get(c, {})
        if not repos:
            continue
        items = ", ".join(f"`{r}`" + (f" ({d})" if d else "") for r, d in sorted(repos.items()))
        lines += ["", f"<details><summary><b>{title}</b>: {len(repos)}</summary>", "", items, "", "</details>"]
    if exceptions_used:
        lines += ["", "<details><summary><b>Exceptions in force</b></summary>", ""]
        lines += [f"- `{r}` / {c}: {why}" for (r, c), why in sorted(exceptions_used.items())] + ["", "</details>"]
    if expired:
        lines += ["", "**Expired exceptions** (the check applies again): " + ", ".join(f"`{e['repo']}` / {e['check']} (expired {e['expires']})" for e in expired)]
    lines += ["", f"{MARKER} {json.dumps(state, sort_keys=True, separators=(',', ':'))} -->"]
    return "\n".join(lines)


def previous_state(write_token):
    out = run_gh(["gh", "issue", "list", "--repo", REPORT_REPO, "--label", LABEL, "--state", "open",
                  "--json", "number,body", "--limit", "1"], write_token)
    items = json.loads(out or "[]")
    if not items:
        return None, None
    body = items[0]["body"]
    if MARKER not in body:
        return items[0]["number"], {}
    raw = body.split(MARKER, 1)[1].split("-->", 1)[0].strip()
    return items[0]["number"], json.loads(raw)


def monthly_comment(state, changes, repos_total, had_before):
    """The comment that is posted every month, quiet or not: it carries the @-mention, which is what sends the email."""
    failing = sum(len(v) for v in state.values())
    lines = [f"@{DUTY_HOLDER} Monthly scan, {TODAY:%d %B %Y}: {repos_total} repositories, **{failing}** failing checks."]
    if not had_before:
        lines.append("This is the first scan with a report to compare against: everything counts as new. The table is in the issue above.")
        return "\n".join(lines)
    new = {c: v["new"] for c, v in changes.items() if v["new"]}
    fixed = sum(len(v["fixed"]) for v in changes.values())
    if not new and not fixed:
        lines.append("Nothing changed since the last scan.")
    if new:
        lines.append("")
        lines.append("**Newly failing:**")
        lines += [f"- {CHECKS[c]}: " + ", ".join(f"`{r}`" for r in repos_) for c, repos_ in new.items()]
    if fixed:
        lines.append("")
        lines.append(f"Fixed since the last scan: {fixed}.")
    return "\n".join(lines)


def select_repos(listing):
    """The repositories that are scanned and named in the report: active (not archived) and **public**. The report
    goes to a public repository (the issue, and the job summary of a public repository's workflow), so a private or
    internal repository must never be scanned: its name and its security alerts would be published."""
    return [r for r in listing
            if not r["archived"] and (r.get("visibility") or ("private" if r.get("private") else "public")) == "public"]


def scan(args):
    read_token, write_token = os.environ.get("READ_TOKEN"), os.environ.get("WRITE_TOKEN")
    repos = select_repos(gh(f"orgs/{ORG}/repos?type=sources&per_page=100", read_token, paginate=True))
    if not repos:
        raise ScanError("the organisation lists no repositories: check the token")
    active, expired = load_exceptions()
    state, used = {c: {} for c in CHECKS}, {}
    for repo in sorted(repos, key=lambda r: r["name"]):
        for check, detail in scan_repo(repo, read_token).items():
            if (repo["name"], check) in active:
                used[(repo["name"], check)] = active[(repo["name"], check)]
            else:
                state[check][repo["name"]] = detail
    number, before = previous_state(write_token)
    had_before = bool(before)
    before = before or {}
    for check in NOT_CHECKED:
        # A check that could not be made keeps its last known result: it must not read as "fixed", and the baseline
        # for the next scan must not lose it.
        state[check] = dict(before.get(check, {}))
    changes = {c: {"new": sorted(set(state[c]) - set(before.get(c, {}))), "fixed": sorted(set(before.get(c, {})) - set(state[c]))} for c in CHECKS}
    if not had_before:
        changes = {}
    body = render(state, used, expired, changes, len(repos))
    comment = monthly_comment(state, changes, len(repos), had_before)
    if args.summary_file:
        with open(args.summary_file, "a") as f:
            f.write(body + "\n\n---\n\nThe monthly comment would read:\n\n" + comment + "\n")
    if args.dry_run:
        print(body + "\n\n--- the monthly comment ---\n" + comment)
        return
    env = dict(os.environ, GH_TOKEN=write_token or os.environ.get("GH_TOKEN", ""))
    subprocess.run(["gh", "label", "create", LABEL, "--repo", REPORT_REPO, "--color", "0e8a16", "--description", "The monthly organisation scan"], capture_output=True, env=env)
    if number is None:
        # Created with the duty holder assigned: that sends the first email.
        subprocess.run(["gh", "issue", "create", "--repo", REPORT_REPO, "--title", TITLE, "--label", LABEL, "--assignee", DUTY_HOLDER, "--body", body], check=True, env=env)
        print("created the issue")
        return
    # The comment goes first. The baseline for the next scan is in the issue body, so it moves only after the
    # notification has been posted: if the comment fails, the next run still sees what is new.
    subprocess.run(["gh", "issue", "comment", str(number), "--repo", REPORT_REPO, "--body", comment], check=True, env=env)
    subprocess.run(["gh", "issue", "edit", str(number), "--repo", REPORT_REPO, "--body", body], check=True, env=env)
    assigned = subprocess.run(["gh", "issue", "edit", str(number), "--repo", REPORT_REPO, "--add-assignee", DUTY_HOLDER], capture_output=True, text=True, env=env)
    if assigned.returncode != 0:
        print(f"warning: could not assign {DUTY_HOLDER}: {assigned.stderr.strip()[:150]}", file=sys.stderr)
    print("edited the issue and posted the monthly comment")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print the report; write nothing")
    ap.add_argument("--summary-file", help="also append the report to this file (the job summary)")
    try:
        scan(ap.parse_args())
    except ScanError as e:
        # Nothing has been written: the existing report stays as it was, and the failed run is the alarm.
        sys.exit(f"scan failed, nothing written: {e}")


if __name__ == "__main__":
    main()
