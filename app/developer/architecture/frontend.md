# Frontend

[`frontend`](https://github.com/source-academy/frontend) is the web application that learners and staff use: React, Redux with sagas, and Blueprint for the interface. Checked against the repository's README and source layout on 28 November 2026.

## What it contains

- **Workspaces**: the Playground (write and run programs), the assessment workspaces (missions, quests and contests), and the grading and editing workspaces for staff. The source is under `src/commons` (parts shared by the workspaces: editor, REPL, side content, control bar) and `src/features` (one folder per feature: `playground`, `assessments`, `grading`, `adminPanel`, `game`, `leaderboard`, `ragChat`, `github`, `persistence`, `remoteExecution`, ...).
- **Side-content tabs**: the panels next to the editor (the stepper, visualizers, the documentation tab, and so on). Tools that show a run are plugins that contribute a tab; see [Plugins and modules](./plugins-and-modules).
- **Language selection**: the choice of a language and of an evaluator for it comes from the [language directory](./directories). The code is in `src/features/directory`.
- **Running a program**: `src/features/conductor` creates a [Conductor](./conductor) host: it starts the evaluator in a Web Worker (`createConductor.ts`, `BrowserHostPlugin.ts`), answers its requests for files and for plugins to load, and loads modules.
- **Two builds**: the full build, with the Academy features (login, assessments), and a playground-only build, which is the one deployed to GitHub Pages (see [Deployment](./deployment)).

## Settings that point to the other parts

The directories that the frontend reads are feature flags (Settings, then Feature Flags): `directory.language.url`, `directory.plugin.url` and `directory.modules.url`. A deployment can pin them with the `REACT_APP_*_DIRECTORY_URL` variables in `.env`, so that they are the same for every user. The backend's address is also configuration, not code.

## What it is meant not to know

The frontend is being arranged so that it knows no tool and no language (see [frontend#4587](https://github.com/source-academy/frontend/issues/4587)): the built-in CSE machine is already removed (it is a plugin), and the per-run settings are served under a neutral name. Where the code still names a language or a tool, that is a leftover.

## Where to read more

The repository's README (setup, environment variables, the Knip dead-code check) and its [wiki](https://github.com/source-academy/frontend/wiki).
