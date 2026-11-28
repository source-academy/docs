# Directories

Three static JSON files tell the frontend what exists: the **language directory**, the **plugin directory** and the **modules directory**. All three are published on GitHub Pages and read by the browser at run time, so that adding a language, a tool or a module does not mean changing the frontend. Checked against the repositories and the published files on 28 November 2026.

## Language directory

[`language-directory`](https://github.com/source-academy/language-directory); published at <https://source-academy.github.io/language-directory/directory.json>.

- A **language definition** (`ILanguageDefinition`) has an id, a name, the evaluators that can run it, and optional settings: an editor configuration, a `textbook` (its label, route, base URL, cover image, and the `chapters` of the book that are written in this language, so that a snippet in a chapter runs in the right language), and `documentation` (the language's own documentation URL and its modules documentation URL, which make the frontend show a Documentation tab).
- An **evaluator definition** (`IEvaluatorDefinition`) has an id, a name, the URL of the evaluator's entry file, its capabilities, and optionally a `plugin`: an id in the plugin directory whose tab presents what the evaluator computes. The host hides such an evaluator from the evaluator dropdown and selects it when the user opens that plugin's tab. This is how the Stepper, the E-Stepper and the CSE machine are offered: as evaluators of the same language that name a plugin.
- Today it has 13 languages: Python §1, §2, §3, §4, §4 Typed and full Python; Source §1 to §4; Scheme; Java; OCaml. Python has several evaluators per language (compiled to JavaScript, a virtual machine, WebAssembly, CPython through Pyodide, and one for each tool). The evaluator URLs point to the GitHub Pages sites of the evaluator repositories (see [Evaluators](./evaluators)).
- To add a language, add its definition to `src/languages.ts`.

## Plugin directory

[`plugin-directory`](https://github.com/source-academy/plugin-directory).

- A **plugin definition** (`IPluginDefinition`) has an id, a name, an optional description, an optional `tab`, and `resolutions`. The `tab` gives the tab's id, label and icon, and whether the tab hides the host's REPL (`hidesRepl`) or keeps the side content from being resized (`resizable`), so that the host can show a placeholder and know how the tab behaves before the plugin loads. `resolutions` maps the kind of environment (web, runner, module) to the URL of the plugin's entry file; a plugin meant for the frontend's API has a web resolution, and one meant for Conductor's module API a module resolution.
- Today it has four plugins: `stepper`, `e-stepper`, `data-visualizer` and `cse-machine`. To add one, add its definition to `src/plugins.ts`.
- **Two copies are published.** The repository's own Pages site serves `https://source-academy.github.io/plugin-directory/directory.json`, and the `plugins` repository's Pages site serves `https://source-academy.github.io/plugins/directory.json`; the frontend's default for `directory.plugin.url` is the second. Both list the same four ids today. Which of the two is the source of truth is not written down; until it is, a change to a plugin entry has to reach the one the frontend reads.

## Modules directory

[`modules`](https://github.com/source-academy/modules) publishes `https://source-academy.github.io/modules/modules.json`, the list of the default modules (`rune`, `plotly`, `curve`, `midi`, `repl`, `robot_simulation`, ...). A program's `import` is resolved against it; see [Plugins and modules](./plugins-and-modules).

## Using a directory

The frontend bundles a copy of the language and plugin directories at a pinned tag (`@sourceacademy/language-directory` and `@sourceacademy/plugin-directory` in its `package.json`) and reads the published files at run time. Each directory can be imported as a package (bundled at build time, with the caution to pin a commit or tag), fetched as JSON at run time, or imported from its `index.js` as an external dependency. The repositories' READMEs describe the three ways and how to test a change locally (`yarn start`, then set the feature flag to the local URL).
