# Architecture of Source Academy

How the parts of Source Academy fit together, and which repository holds each. This page is the overview; the pages for the components are listed at the end.

Written on 28 November 2026 from the code and the READMEs of the repositories. Each page names the files it was checked against, so that a maintainer can tell what to update when the code changes.

## The picture

A learner's browser runs the **frontend**. The frontend knows no language and no tool: it reads three **directories** (static JSON files on GitHub Pages) to find out which languages, evaluators, plugins and modules exist, and loads what it needs when a program runs. A language **evaluator** runs in a Web Worker and talks to the frontend through the **Conductor** protocol. Tools that show a program's execution, such as the Stepper, are **plugins** that the evaluator asks the frontend to load. The **backend** keeps the accounts, courses, assessments and submissions, and sends submissions to the **grader**, which runs the same evaluators on the server.

<svg viewBox="0 0 760 440" role="img" aria-labelledby="arch-title arch-desc" style="width:100%;height:auto;font-family:var(--vp-font-family-base);font-size:13px">
<title id="arch-title">The parts of Source Academy and how they connect</title>
<desc id="arch-desc">The frontend in the browser loads evaluators and plugins named by three directories, runs an evaluator in a Web Worker over Conductor, and talks to the backend, which sends submissions to the grader.</desc>
<defs><marker id="arch-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="var(--vp-c-text-3)"/></marker></defs>
<rect x="10" y="10" width="470" height="305" rx="10" fill="none" stroke="var(--vp-c-divider)" stroke-dasharray="5 4"/>
<text x="24" y="304" fill="var(--vp-c-text-2)">The learner's browser</text>
<rect x="30" y="60" width="200" height="90" rx="8" fill="var(--vp-c-bg-soft)" stroke="var(--vp-c-brand-1)" stroke-width="2"/>
<text x="130.0" y="90" text-anchor="middle" fill="var(--vp-c-text-1)" font-weight="600">Frontend</text>
<text x="130.0" y="112" text-anchor="middle" fill="var(--vp-c-text-2)">workspaces, editor, tabs</text>
<rect x="270" y="60" width="190" height="90" rx="8" fill="var(--vp-c-bg-soft)" stroke="var(--vp-c-divider)" stroke-width="2"/>
<text x="365.0" y="90" text-anchor="middle" fill="var(--vp-c-text-1)" font-weight="600">Evaluator</text>
<text x="365.0" y="112" text-anchor="middle" fill="var(--vp-c-text-2)">in a Web Worker</text>
<text x="365.0" y="130" text-anchor="middle" fill="var(--vp-c-text-2)">js-slang, py-slang, ...</text>
<rect x="30" y="195" width="200" height="80" rx="8" fill="var(--vp-c-bg-soft)" stroke="var(--vp-c-divider)" stroke-width="2"/>
<text x="130.0" y="225" text-anchor="middle" fill="var(--vp-c-text-1)" font-weight="600">Plugins</text>
<text x="130.0" y="247" text-anchor="middle" fill="var(--vp-c-text-2)">Stepper, E-Stepper,</text>
<text x="130.0" y="265" text-anchor="middle" fill="var(--vp-c-text-2)">Data Visualizer, CSE machine</text>
<rect x="270" y="195" width="190" height="80" rx="8" fill="var(--vp-c-bg-soft)" stroke="var(--vp-c-divider)" stroke-width="2"/>
<text x="365.0" y="225" text-anchor="middle" fill="var(--vp-c-text-1)" font-weight="600">Modules</text>
<text x="365.0" y="247" text-anchor="middle" fill="var(--vp-c-text-2)">bundles and tabs</text>
<text x="365.0" y="265" text-anchor="middle" fill="var(--vp-c-text-2)">that programs import</text>
<line x1="232" y1="105" x2="268" y2="105" stroke="var(--vp-c-text-3)" stroke-width="1.5" marker-start="url(#arch-arrow)" marker-end="url(#arch-arrow)"/>
<text x="250" y="56" text-anchor="middle" fill="var(--vp-c-text-2)" font-size="11">Conductor</text>
<line x1="130" y1="152" x2="130" y2="193" stroke="var(--vp-c-text-3)" stroke-width="1.5" marker-end="url(#arch-arrow)"/>
<text x="138" y="176" text-anchor="start" fill="var(--vp-c-text-2)" font-size="11">loads plugins, shows tabs</text>
<line x1="365" y1="152" x2="365" y2="193" stroke="var(--vp-c-text-3)" stroke-width="1.5" marker-end="url(#arch-arrow)"/>
<text x="373" y="176" text-anchor="start" fill="var(--vp-c-text-2)" font-size="11">import</text>
<rect x="500" y="60" width="250" height="215" rx="10" fill="none" stroke="var(--vp-c-divider)" stroke-dasharray="5 4"/>
<text x="514" y="82" fill="var(--vp-c-text-2)">Static JSON on GitHub Pages</text>
<rect x="520" y="96" width="210" height="46" rx="8" fill="var(--vp-c-bg-soft)" stroke="var(--vp-c-divider)" stroke-width="2"/>
<text x="625" y="124" text-anchor="middle" fill="var(--vp-c-text-1)">Language directory</text>
<rect x="520" y="152" width="210" height="46" rx="8" fill="var(--vp-c-bg-soft)" stroke="var(--vp-c-divider)" stroke-width="2"/>
<text x="625" y="180" text-anchor="middle" fill="var(--vp-c-text-1)">Plugin directory</text>
<rect x="520" y="208" width="210" height="46" rx="8" fill="var(--vp-c-bg-soft)" stroke="var(--vp-c-divider)" stroke-width="2"/>
<text x="625" y="236" text-anchor="middle" fill="var(--vp-c-text-1)">Modules directory</text>
<path d="M 500 70 L 490 70 L 490 34 L 130 34 L 130 58" fill="none" stroke="var(--vp-c-text-3)" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#arch-arrow)"/>
<text x="310" y="28" text-anchor="middle" fill="var(--vp-c-text-2)" font-size="11">the frontend reads the directories at run time</text>
<rect x="30" y="350" width="170" height="80" rx="8" fill="var(--vp-c-bg-soft)" stroke="var(--vp-c-brand-1)" stroke-width="2"/>
<text x="115.0" y="380" text-anchor="middle" fill="var(--vp-c-text-1)" font-weight="600">Backend</text>
<text x="115.0" y="402" text-anchor="middle" fill="var(--vp-c-text-2)">Phoenix, PostgreSQL</text>
<rect x="290" y="350" width="170" height="80" rx="8" fill="var(--vp-c-bg-soft)" stroke="var(--vp-c-brand-1)" stroke-width="2"/>
<text x="375.0" y="380" text-anchor="middle" fill="var(--vp-c-text-1)" font-weight="600">Grader</text>
<text x="375.0" y="402" text-anchor="middle" fill="var(--vp-c-text-2)">AWS Lambda,</text>
<text x="375.0" y="420" text-anchor="middle" fill="var(--vp-c-text-2)">vendored evaluators</text>
<path d="M 30 105 L 20 105 L 20 390 L 28 390" fill="none" stroke="var(--vp-c-text-3)" stroke-width="1.5" marker-end="url(#arch-arrow)"/>
<text x="36" y="338" text-anchor="start" fill="var(--vp-c-text-2)" font-size="11">HTTPS API</text>
<line x1="202" y1="390" x2="288" y2="390" stroke="var(--vp-c-text-3)" stroke-width="1.5" marker-end="url(#arch-arrow)"/>
<text x="245" y="382" text-anchor="middle" fill="var(--vp-c-text-2)" font-size="11">submission</text>
</svg>

## The parts, and where they live

| Part                                         | What it is                                                                                       | Repository                                                                                                                                                                                                                                                                                                   |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [Frontend](./frontend)                       | The web application: workspaces, the editor, the side-content tabs, assessments, grading screens | [`frontend`](https://github.com/source-academy/frontend)                                                                                                                                                                                                                                                     |
| [Backend](./backend)                         | Accounts, courses, assessments, submissions, the API; Elixir, Phoenix, PostgreSQL                | [`backend`](https://github.com/source-academy/backend)                                                                                                                                                                                                                                                       |
| [Grader](./grader)                           | Runs a submission's test cases in an evaluator, on AWS Lambda                                    | [`grader`](https://github.com/source-academy/grader)                                                                                                                                                                                                                                                         |
| [Directories](./directories)                 | JSON lists of the languages and evaluators, of the plugins, and of the modules                   | [`language-directory`](https://github.com/source-academy/language-directory), [`plugin-directory`](https://github.com/source-academy/plugin-directory), [`modules`](https://github.com/source-academy/modules)                                                                                               |
| [Conductor](./conductor)                     | The protocol between a host and a runner, and the code that implements it                        | [`conductor`](https://github.com/source-academy/conductor)                                                                                                                                                                                                                                                   |
| [Evaluators](./evaluators)                   | One implementation per language                                                                  | [`js-slang`](https://github.com/source-academy/js-slang), [`py-slang`](https://github.com/source-academy/py-slang), [`scm-slang`](https://github.com/source-academy/scm-slang), [`java-slang`](https://github.com/source-academy/java-slang), [`ocaml-slang`](https://github.com/source-academy/ocaml-slang) |
| [Plugins and modules](./plugins-and-modules) | Tools that show a run, and libraries that a program imports                                      | [`plugins`](https://github.com/source-academy/plugins), [`modules`](https://github.com/source-academy/modules)                                                                                                                                                                                               |
| [Deployment](./deployment)                   | Where the parts run                                                                              | [`backend`](https://github.com/source-academy/backend) (`deployment/`), GitHub Pages                                                                                                                                                                                                                         |

Two paths cross all of these: [a run in the workspace, and a submission](./run-and-submission).

## Three ideas that explain most of the design

- **The frontend knows no language and no tool.** Which languages exist, which evaluator runs each, which tab shows what an evaluator computes: all of it is in the directories, and the frontend reads them at run time. A new language or tool is added to a directory, not to the frontend. (This is the direction the code is moving in; the frontend still contains a few special cases, tracked in [frontend#4587](https://github.com/source-academy/frontend/issues/4587).)
- **An evaluator is a program that speaks Conductor.** It runs in a Web Worker in the browser and in a worker thread in the grader, with the same code in both.
- **A tool is a plugin.** The evaluator asks the host to load a plugin by its id in the plugin directory, and the plugin contributes a tab. [Writing a visualizer plugin](../writing-a-visualizer-plugin) describes how.

## The four pieces that make the frontend language- and tool-agnostic

### Conductor

[`conductor`](https://github.com/source-academy/conductor) is the standard interface between a **host** (an environment from which runners are created: the browser frontend, a command line, the grader) and a **runner** (the environment where user code runs, with an **evaluator** in it). Host and runner exchange messages over named, bidirectional **channels**; the standard ones carry results (`__result`), errors (`__error`), standard output (`__stdio`) and status (`__status`). A **plugin** is a program loaded on demand that can listen on and send over channels. An evaluator implements `IEvaluator` (the base class `BasicEvaluator` needs only `evaluateChunk`), and an entry point creates a `Conduit` and registers the runner plugin. Conductor also defines the **module interface**: the data types and the functions with which a module (a library such as `rune` or `plotly`) reads and builds values of an evaluator without knowing its memory model. More in [Conductor](./conductor).

### Plugins

A **plugin** is how a tool joins a run. The Stepper, the E-Stepper, the Data Visualizer and the CSE machine are plugins: each has a package that the evaluator uses (`common-*` for the protocol, `runner-*` for the evaluator's side) and a package that the browser loads (`web-*`, which contributes a side-content tab). They live in [`plugins`](https://github.com/source-academy/plugins), are built into bundles on GitHub Pages, and are found through the plugin directory. An evaluator asks the host to load one with `hostLoadPlugin(id)`. More in [Plugins and modules](./plugins-and-modules), and [Writing a visualizer plugin](../writing-a-visualizer-plugin).

### Language directory

[`language-directory`](https://github.com/source-academy/language-directory) lists the languages that Source Academy supports. A **language definition** has an id, a name, the **evaluators** that can run it, and optional settings: an editor configuration, a textbook (with the chapters written in this language), and links to documentation. An **evaluator definition** has an id, a name, the URL of the evaluator's entry file, its capabilities, and optionally the id of a **plugin** whose tab presents what the evaluator computes (an evaluator with that field is hidden from the evaluator dropdown, and chosen when the user opens the plugin's tab). The directory is published as JSON at `https://source-academy.github.io/language-directory/directory.json`; on 28 November 2026 it lists 13 languages (Python §1 to §4, Python §4 Typed, full Python, Source §1 to §4, Scheme, Java, OCaml). A new language is added to `src/languages.ts`. More in [Directories](./directories).

### Plugin directory

[`plugin-directory`](https://github.com/source-academy/plugin-directory) lists the plugins. A **plugin definition** has an id, a name, an optional description, an optional `tab` (its id, label, icon, and whether it hides the host's REPL or keeps the side content from being resized, so that the host can show a placeholder before the plugin loads), and **resolutions**: for each kind of environment (web, runner, module) the URL of the plugin's entry file. On 28 November 2026 it lists four plugins: `stepper`, `e-stepper`, `data-visualizer` and `cse-machine`. A new plugin is added to `src/plugins.ts`. More in [Directories](./directories).

## Pages

- [Frontend](./frontend)
- [Backend](./backend)
- [Grader](./grader)
- [Directories](./directories)
- [Conductor](./conductor)
- [Evaluators](./evaluators)
- [Plugins and modules](./plugins-and-modules)
- [Deployment](./deployment)
- [A run in the workspace, and a submission](./run-and-submission)
