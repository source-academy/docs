# Node.js version

Every Source Academy repository that uses Node.js uses **Node 24**, and says so in the same way. This page is the one place to refer to. When the version changes, change it here first.

_Decided on 27 November 2026._

## Why one version

Node matters to us for building, testing and continuous integration: the frontend runs in browsers, and the evaluators run in workers or on AWS Lambda. Mixing versions costs contributors time: the tools that we use have a minimum version (the spell checker of this repository needs Node 22.18 or later, for one), so a contributor who moves from one repository to another meets failures that have nothing to do with their change.

A version is also supported only for so long. At the time of the decision:

| Node | State                   | End of life |
| ---- | ----------------------- | ----------- |
| 20   | ended                   | 30 Apr 2026 |
| 22   | maintenance             | 30 Apr 2027 |
| 24   | maintenance (LTS)       | 30 Apr 2028 |
| 26   | active LTS since 28 Oct | 30 Apr 2029 |

24 is the version that most of our repositories could move to with the least risk, and that the repositories with the most to lose (the grader, the modules) already use. The next move, to 26, is made the same way as this one.

## How a repository says it

A repository that uses Node has all of these, and nothing else that states a Node version:

1. **`.node-version`** with the line `24`. It is the single source in the repository. The major version only: a patch version in it is something to keep up to date in every repository for no gain.
2. **Continuous integration** takes it from there: `actions/setup-node` with `node-version-file: .node-version`, not a number of its own.
3. **`package.json`** has `"engines": { "node": ">=24" }`.
4. **`@types/node`** is at `^24`, the version that the code runs on.
5. **The README** says in its build instructions that the repository needs Node 24, with a link to this page.
6. **Renovate** (or Dependabot) does not raise Node or `@types/node` past 24 on its own. The next version is a decision, made here, and then made in every repository.

**Code that runs in a host's own Node** is the one exception, and it is to point 4 only. A VS Code extension, or a language server that it starts, runs in the Node that VS Code brings, not in ours. Its `@types/node` follows the oldest VS Code that its `engines.vscode` allows, so that the types describe the runtime that the code really has; the build and CI still use Node 24. The README says which version the types follow.

Any other repository with a real need for another version says why, in its README and in an issue; there is none now.

## Using it on your machine

A version manager that reads `.node-version`, such as fnm or mise, selects the version when you enter the repository (check its setting for version files of other tools). With nvm, run `nvm use $(cat .node-version)`.

## Changing the version

1. Update this page: the version, the table and the date.
2. Check what depends on it that is not in a repository's files: the AWS Lambda runtime of the grader has to be one that AWS offers, and the runtime in the backend's Terraform (`deployment/terraform/lambda.tf`) has to say the same as the grader's build.
3. Open one pull request per repository that changes the five things above, and run its tests on the new version. Track them in one issue.
