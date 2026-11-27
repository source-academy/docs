# Organisation health scan

A monthly, read-only scan of the `source-academy` organisation (documentation#66). It writes **one issue**,
"Organisation health", edited in place: a table of checks, the repositories that fail each, and what changed
since the last scan. Every month the issue is assigned to the duty holder and gets a short comment that @-mentions them (what is newly
failing, what is fixed, or "nothing changed"), so **an email arrives every month, quiet or not**.

## The checks

| check        | fails when                                                 |
| ------------ | ---------------------------------------------------------- |
| `licence`    | the repository has no licence                              |
| `readme`     | no README                                                  |
| `protection` | the default branch has no branch protection and no ruleset |
| `alerts`     | there are open high or critical Dependabot alerts          |
| `scanning`   | code scanning is not set up                                |
| `stale-prs`  | open pull requests older than six months                   |
| `branches`   | more than 30 branches                                      |
| `inactive`   | no commit on the default branch for over a year            |

Not checked yet: whether the default branch builds. It needs the App's _Actions: read_ permission.

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
(to read branch protection), contents, issues, pull requests, code scanning alerts, Dependabot alerts and metadata.
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
