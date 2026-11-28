# Plugins and modules

Two ways to extend what a program can do or show: **plugins** show a run, and **modules** give a program libraries to import. Checked against the repositories on 28 November 2026.

## Plugins

[`plugins`](https://github.com/source-academy/plugins) is a monorepo of the packages that tools are made of, in three groups under `src`: `common` (the protocol: types and the id in the plugin directory), `runner` (what an evaluator uses: a base class and the streaming of steps) and `web` (what the browser loads: a host plugin and the view, which contributes a side-content tab). Packages are released with Changesets, and the web bundles are built and deployed to GitHub Pages; the entries in the [plugin directory](./directories) point to them.

The plugins today:

| Plugin          | What it shows                                                                                 |
| --------------- | --------------------------------------------------------------------------------------------- |
| Stepper         | Substitution steps; one plugin for several languages, with a rules profile from the evaluator |
| E-Stepper       | The program with its environment frames and heap, step by step                                |
| Data Visualizer | Data structures, over a channel of its own                                                    |
| CSE machine     | The control, the stash and the environments, for languages that share the environment model   |

A plugin is loaded when an evaluator calls `hostLoadPlugin(id)`; the host fetches the bundle from the plugin directory's URL, and the plugin registers its tab with the tab service. What the host offers a plugin beyond the tab service (editor highlighting, today) is the host contract in `common-tabs`. The guide [Writing a visualizer plugin](../writing-a-visualizer-plugin) covers all of this.

## Modules

[`modules`](https://github.com/source-academy/modules) holds the default **bundles** (libraries a program imports, such as `rune`, `curve`, `plotly`, `midi` and `repl`) and their **tabs** (the side-content tab that a bundle can contribute, for example to draw a rune), with the documentation for them and the tooling to build them. Its layout is `src/bundles`, `src/tabs`, a `devserver`, a documentation server (`docs`, published at <https://source-academy.github.io/modules/documentation>) and a developer documentation site (<https://source-academy.github.io/modules/devdocs>).

The frontend finds the modules through the modules directory (`modules.json`) and loads them with the module loader plugin; a module talks to the evaluator through the [Conductor](./conductor) module interface.

## The difference

A plugin is chosen by the evaluator and shows the run; a module is imported by the program and is part of what the program does. Both are fetched at run time from GitHub Pages.
