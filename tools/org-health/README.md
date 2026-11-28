# Organisation health scan

A monthly, read-only scan of the `source-academy` organisation (documentation#66). It writes **one issue**,
"Organisation health", edited in place: a table of checks, the repositories that fail each, and what changed
since the last scan. Every month the issue is assigned to the duty holder and gets a short comment that @-mentions them (what is newly
failing, what is fixed, or "nothing changed"), so **an email arrives every month, quiet or not**.

## The checks

| check        | fails when                                                     |
| ------------ | -------------------------------------------------------------- |
| `licence`    | the repository has no licence                                  |
| `readme`     | no README                                                      |
| `protection` | the default branch has no branch protection and no ruleset     |
| `alerts`     | there are open high or critical Dependabot alerts              |
| `scanning`   | code scanning is not set up                                    |
| `stale-prs`  | open pull requests older than six months                       |
| `branches`   | more than 30 branches                                          |
| `inactive`   | no commit on the default branch for over a year                |
| `empty`      | the repository has no commits (nothing to check on a branch)   |
| `cache`      | the Actions cache is above 80% of its limit (10 GB by default) |
| `links`      | the README has a dead link (404, 410, or a host that is gone)  |

The `cache` check needs the App's **Actions: read** permission, which the App has (granted on 27 November 2026) and the token step of `.github/workflows/org-health.yml` requests. It compares the size of a repository's Actions cache with its limit: the configured limit where GitHub reports one (a paid plan can raise it), else the default of 10 GB. If the permission is ever removed, the scan skips this one check, says so in the report, keeps its **last known result** (so nothing reads as fixed), and carries on. When you grant a new permission to the App, grant it first and request it in the workflow second: the token action asks for exactly the permissions it lists, and GitHub refuses a token that asks for one the App lacks, which would fail the whole scan. Not checked yet: whether the default branch builds; it needs the same permission.

The `links` check reads each repository's README and asks for every absolute link in it (placeholders such as `localhost` and `example.com` are skipped). A link is **dead** only on a definite sign: the answer 404 or 410, or a host that does not exist, on two tries. A site that refuses automated clients (403, 429), a timeout, a TLS error or a server error is **not** reported: the network is noisy, and a link that is really gone is found by a later scan. (This differs on purpose from the calls to GitHub, whose failure stops the scan.) The report lists the dead links under "Dead links in READMEs"; the table and the baseline count only repositories. It checks the README only, not the other Markdown files of a repository, and not the links inside a repository's own files. The docs repository's own pages are checked on every pull request by `.github/workflows/links.yml`.

Only the checks and thresholds at the top of `scan.py` need changing to add or tune one. Keep the list short:
a report that has to be read has few checks.

## Run it

```sh
python3 tools/org-health/scan.py --dry-run   # prints the report; writes nothing
```

It uses your `gh` login, or `READ_TOKEN` if set. It takes a few minutes (about nine API calls per repository).
Pull requests run the unit tests only, **with no secret**: a pull request's own code must never run with the App's
token. To try a change against the real organisation, run `--dry-run` on your machine. Scheduled runs (the first of
each month) and manual runs on the default branch run the scan; a manual run with _dry_run_ ticked only prints the
report (to the job summary).

To test the parts that decide what counts as healthy: `python3 -m unittest discover tools/org-health`.

A failing API call is never counted as healthy: an expected absence (a feature that is off for a repository) is told
apart from a real failure, which is retried and then **stops the scan before it writes anything**. A failed run is the
alarm, through GitHub's own email about failed workflows.

Only **public, active** repositories are scanned and named: the report goes to a public repository (an issue and a
job summary), so a private or internal repository is never scanned. Archived repositories are left out too.

## Exceptions

A repository that fails a check on purpose goes in [`health-exceptions.toml`](health-exceptions.toml), with a reason
and an **expiry date**. The scan stops reporting it; when the date passes, the check applies again and the report
says so. An exception is a decision that is reviewed, not a way to hide a problem.

## Who looks at it

The duty holder reads the issue once a month (about ten minutes) and does nothing when it is quiet.
**Duty holder: @martin-henz** (since 27 November 2026). To hand over, change this line, the line in the
contributing guide, and the owner below.

## The GitHub App

The scan reads other repositories with a short-lived token from the GitHub App **source-academy-health**
(owned by the `source-academy` organisation; App ID 5949427). The App is **read-only** everywhere: administration
(to read branch protection), contents, issues, pull requests, code scanning alerts, Dependabot alerts and metadata
(and, once granted, Actions, for the cache check).
It never writes: the report issue is written with the workflow's own `GITHUB_TOKEN`.

- **Owner:** the organisation owners (currently @martin-henz).
- **Secrets:** `APP_PRIVATE_KEY` (secret) and the variables `APP_ID` and `APP_CLIENT_ID` of this repository.
- **Who can use the secret:** anyone with write access to this repository can use its Actions secrets, for example
  through a workflow on a branch of their own. The App is read-only and its token lives for an hour, but it reads every
  repository's security alerts. When the key is next rotated, store it as a secret of an _environment_ (say `org-health`)
  that only the default branch may use (environment settings, _Deployment branches_), and set `environment: org-health`
  on the `scan` job.
- **Rotate the key** (once a year, or when someone with access leaves): organisation settings, _Developer settings_,
  _GitHub Apps_, `source-academy-health`, _Credentials_, _Generate a private key_. Store it with
  `gh secret set APP_PRIVATE_KEY --repo source-academy/documentation < the-file.pem`, delete the file, then delete the
  old key on the same page. Never paste a key into an issue, a chat or a commit.
