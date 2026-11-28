# Contributing

How to contribute to Source Academy, in any of its repositories. This is the page that the organisation's default [`CONTRIBUTING.md`](https://github.com/source-academy/.github/blob/main/CONTRIBUTING.md) points to. A repository can have its own `CONTRIBUTING.md` with more detail (the frontend does, on its application structure and testing); that one comes first where the two differ.

## The short version

1. **Start from an issue.** Look in the issue tracker of the repository for something to work on, or open an issue to describe what you want to change. For anything larger than a small fix, wait for a reply before you start, so that the work does not collide with a plan that you cannot see.
2. **Fork the repository** and make a branch in your fork. Write access to the repositories is limited to the organisation's owners, so everybody else contributes from a fork. GitHub's [fork a repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo) page explains how.
3. **Make the change** and run the checks of the repository (format, lint, test, build: the scripts of `package.json`, or the commands in the README) before you push.
4. **Open a pull request** that says what changed and why, and which issue it closes. The repository's pull-request template (or the organisation's default) shows what to include.
5. **Answer the review.** An owner reviews the pull request. Change what the review asks for, or explain why not, and the pull request is merged when the checks pass and the review approves.

## What to expect from a pull request

- **A pull request is required** to change the default branch of a repository, and force pushes and deletion of the branch are blocked. The repositories that only hold built output (the deployment repositories, such as `docs.sourceacademy.org`) are written by workflows instead.
- **Most repositories require one approving review**, and some require passing checks (for example the tests, the linter or the build). The checks that a repository requires are listed in its branch protection or ruleset, and you see them at the bottom of the pull request.
- **Merged branches are deleted** automatically.
- **Dependencies** are updated by Dependabot pull requests. Reviewing one is a good first contribution: read what changed, and check that the checks pass.

## Conventions that apply everywhere

- **Node.js:** every repository that uses it uses one version, described on the [Node.js version](./node-version) page.
- **Comments:** the playbook is on the [Cleaning up comments](./comment-cleanup) page. A pull request that only changes comments follows it.
- **One change per pull request.** A small pull request is reviewed sooner than a large one, and is easier to take back.

## Reporting a security problem

Do not open a public issue. Use GitHub's private vulnerability reporting, as described in the [security policy](https://github.com/source-academy/.github/blob/main/SECURITY.md).

## Behaviour

Everyone who takes part in the project is expected to follow the [code of conduct](https://github.com/source-academy/.github/blob/main/CODE_OF_CONDUCT.md).

## For maintainers: a new repository

The organisation's security settings (Dependabot, CodeQL, secret scanning with push protection, private vulnerability reporting) apply to a new repository by themselves. The protection of its default branch does not, because the organisation is on a plan without organisation-wide rulesets. The checklist is in the [README of the `.github` repository](https://github.com/source-academy/.github#checklist-for-a-new-repository): in short, run `scripts/apply-baseline.sh --apply <repository>`.
