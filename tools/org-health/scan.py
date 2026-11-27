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
import subprocess
import sys
import tomllib

ORG = "source-academy"
REPORT_REPO = f"{ORG}/documentation"
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
}
MAX_BRANCHES = 30
STALE_DAYS = 180
INACTIVE_DAYS = 365


def gh(path, token, paginate=False):
    """The JSON of a GitHub API call, or None if it fails (not found, disabled, no access)."""
    cmd = ["gh", "api", path] + (["--paginate"] if paginate else [])
    env = dict(os.environ, **({"GH_TOKEN": token} if token else {}))
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        return None
    text = r.stdout.strip()
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


def scan_repo(repo, token):
    """The failing checks of one repository, each with a short detail."""
    name, default = repo["name"], repo["default_branch"]
    r = f"repos/{ORG}/{name}"
    failed = {}
    if not repo.get("license"):
        failed["licence"] = ""
    profile = gh(f"{r}/community/profile", token)
    if profile is not None and not (profile.get("files") or {}).get("readme"):
        failed["readme"] = ""
    branch = gh(f"{r}/branches/{default}", token)
    rules = gh(f"{r}/rules/branches/{default}", token)
    if not ((branch and branch.get("protected")) or rules):
        failed["protection"] = ""
    alerts = gh(f"{r}/dependabot/alerts?state=open&severity=critical,high&per_page=100", token, paginate=True)
    if alerts:
        failed["alerts"] = str(len(alerts))
    setup = gh(f"{r}/code-scanning/default-setup", token)
    analyses = gh(f"{r}/code-scanning/analyses?per_page=1", token, paginate=False)
    if not ((setup and setup.get("state") == "configured") or analyses):
        failed["scanning"] = ""
    prs = gh(f"{r}/pulls?state=open&per_page=100", token, paginate=True) or []
    stale = [p for p in prs if days(p["created_at"]) > STALE_DAYS]
    if stale:
        failed["stale-prs"] = f"{len(stale)} of {len(prs)}"
    branches = gh(f"{r}/branches?per_page=100", token, paginate=True) or []
    if len(branches) > MAX_BRANCHES:
        failed["branches"] = str(len(branches))
    # The last commit on the default branch, not `pushed_at`: that moves when anyone pushes a branch.
    latest = gh(f"{r}/commits?sha={default}&per_page=1", token)
    if latest and days(latest[0]["commit"]["committer"]["date"]) > INACTIVE_DAYS:
        failed["inactive"] = f"{days(latest[0]['commit']['committer']['date']) // 30} months"
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
             "[`tools/org-health`](https://github.com/source-academy/documentation/tree/main/tools/org-health).", ""]
    lines += ["| check | failing | change |", "| --- | --- | --- |"]
    for c, title in CHECKS.items():
        n = len(state.get(c, {}))
        ch = changes.get(c, {"new": [], "fixed": []})
        delta = ", ".join(filter(None, [f"+{len(ch['new'])} new" if ch["new"] else "", f"-{len(ch['fixed'])} fixed" if ch["fixed"] else ""])) or "no change"
        lines.append(f"| {title} | {n} | {delta} |")
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
    out = subprocess.run(["gh", "issue", "list", "--repo", REPORT_REPO, "--label", LABEL, "--state", "open",
                          "--json", "number,body", "--limit", "1"], capture_output=True, text=True,
                         env=dict(os.environ, **({"GH_TOKEN": write_token} if write_token else {})))
    items = json.loads(out.stdout or "[]")
    if not items:
        return None, None
    body = items[0]["body"]
    if MARKER not in body:
        return items[0]["number"], {}
    raw = body.split(MARKER, 1)[1].split("-->", 1)[0].strip()
    return items[0]["number"], json.loads(raw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print the report; write nothing")
    ap.add_argument("--summary-file", help="also append the report to this file (the job summary)")
    args = ap.parse_args()
    read_token, write_token = os.environ.get("READ_TOKEN"), os.environ.get("WRITE_TOKEN")
    repos = [r for r in (gh(f"orgs/{ORG}/repos?type=sources&per_page=100", read_token, paginate=True) or []) if not r["archived"]]
    if not repos:
        sys.exit("could not list the repositories: check the token")
    active, expired = load_exceptions()
    state, used = {c: {} for c in CHECKS}, {}
    for repo in sorted(repos, key=lambda r: r["name"]):
        for check, detail in scan_repo(repo, read_token).items():
            if (repo["name"], check) in active:
                used[(repo["name"], check)] = active[(repo["name"], check)]
            else:
                state[check][repo["name"]] = detail
    number, before = previous_state(write_token)
    before = before or {}
    changes = {c: {"new": sorted(set(state[c]) - set(before.get(c, {}))), "fixed": sorted(set(before.get(c, {})) - set(state[c]))} for c in CHECKS}
    if not before:
        changes = {}
    body = render(state, used, expired, changes, len(repos))
    if args.summary_file:
        with open(args.summary_file, "a") as f:
            f.write(body + "\n")
    if args.dry_run:
        print(body)
        return
    env = dict(os.environ, GH_TOKEN=write_token or os.environ.get("GH_TOKEN", ""))
    subprocess.run(["gh", "label", "create", LABEL, "--repo", REPORT_REPO, "--color", "0e8a16", "--description", "The monthly organisation scan"], capture_output=True, env=env)
    if number is None:
        subprocess.run(["gh", "issue", "create", "--repo", REPORT_REPO, "--title", TITLE, "--label", LABEL, "--body", body], check=True, env=env)
        print("created the issue")
        return
    subprocess.run(["gh", "issue", "edit", str(number), "--repo", REPORT_REPO, "--body", body], check=True, env=env)
    newly = {c: v["new"] for c, v in changes.items() if v["new"]}
    if newly:
        text = "Newly failing since the last scan:\n" + "\n".join(f"- {CHECKS[c]}: " + ", ".join(f"`{r}`" for r in repos_) for c, repos_ in newly.items())
        subprocess.run(["gh", "issue", "comment", str(number), "--repo", REPORT_REPO, "--body", text], check=True, env=env)
        print("edited the issue and commented on what is new")
    else:
        print("edited the issue; nothing new, so no comment")


if __name__ == "__main__":
    main()
