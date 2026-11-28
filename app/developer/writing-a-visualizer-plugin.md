# Writing a visualizer plugin

A visualizer shows what a program does in a side-content tab of the workspace: the Stepper shows substitution steps, the E-Stepper shows the program with its environment frames and heap, the Data Visualizer shows data structures, and the CSE machine shows the control, the stash and the environments.

Each of them is a **plugin**. The frontend knows no visualizer and no language: an evaluator asks the host to load a plugin by its id, the host finds the plugin in the **plugin directory**, loads it from the URL given there, and the plugin contributes its own tab. This guide describes the parts, in the order that a run uses them, and uses the E-Stepper as the model.

It is for someone who is making a visualizer for a language of their own. A visualizer does not have to look like the existing ones, and the parts below do not assume that it does.

## The parts

| Part                             | Where it lives                              | What it is                                                                                                                 |
| -------------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Protocol package `common-<tool>` | `plugins`, `src/common/<tool>`              | The channel's id, the id in the plugin directory, and the types of the messages. Used by both sides, so it has no UI code. |
| Runner plugin `runner-<tool>`    | `plugins`, `src/runner/<tool>`              | The evaluator's half: collects what the picture needs and sends it over the channel.                                       |
| Web plugin `web-<tool>`          | `plugins`, `src/web/<tool>`                 | The host's half: receives the messages and contributes the tab.                                                            |
| Plugin directory entry           | `plugin-directory`, `src/plugins/<tool>.ts` | The plugin's id and name, how its tab behaves, and the URL of the web bundle.                                              |
| The evaluator                    | the language's own repository               | Registers the runner plugin and asks the host to load the web plugin.                                                      |
| Language directory entry         | `language-directory`, `src/languages/...`   | Offers the visualizer for a language: an evaluator of its own that names the plugin.                                       |

The three packages need not live in the `plugins` repository: the plugin directory entry can point to a bundle anywhere. That repository has the build and the deployment ready, so the rest of this guide assumes it.

## 1. The protocol

A **channel** is a named line of messages between the runner and the host. Pick an id for the channel and one for the plugin directory, and write down the messages. The E-Stepper has `E_STEPPER_CHANNEL_ID` (`"__e_stepper"`), `E_STEPPER_DIRECTORY_ID` (`"e-stepper"`), and these messages:

| Message                                    | Direction     | Meaning                                                                                                                                                       |
| ------------------------------------------ | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `batch` `{ index, steps, profile?, end? }` | runner → host | Steps of the run that is going on. `index` is the number of steps before this batch; 0 starts a run and replaces what the host had. The last batch has `end`. |
| `steps` `{ steps, profile? }`              | runner → host | A runner that does not stream sends the whole trace at the end. The host takes it as complete.                                                                |
| `error` `{ error }`                        | runner → host | The visualization failed, for example because the program does not parse.                                                                                     |
| `request`                                  | host → runner | "Send again what you last computed", so that a tab that is opened after the run still shows it.                                                               |

How a run ends is a `TraceEnd`: `complete`, or `cut-off` with a reason (a step limit, a memory guard). A run that the user stops, or that never ends, keeps the batches that arrived, which is the point of sending them while the run goes on. A failure is the `error` message, not a kind of end.

Rules that make a protocol safe to change:

- Messages must be plain JSON that can be copied between a worker and the page.
- Make every change **additive** (a new optional field, a new message). The runner is loaded at run time from where the language's evaluator is deployed, and the web plugin from where the plugins are, so either side may be deployed first. A message on a channel that only one side has is held back and ignored, and nothing fails.
- Keep UI code out of this package: it is imported in the evaluator's worker.

A visualizer of another kind defines its own messages. The shape above, batches that carry an `index` and a final `end`, is worth keeping.

## 2. The runner plugin

The runner plugin is an `IPlugin` (from `@sourceacademy/conductor/conduit`) with `static channelAttach = [CHANNEL_ID]`. It receives the channel in its constructor, sends messages on it, and answers `request` by sending the last trace again.

A visualizer that is step-based can extend the existing base class instead: `BaseStepperRunnerPlugin<TAst>` (`runner-stepper`), which `BaseEStepperRunnerPlugin<TAst>` extends by changing only the channel, the plugin id and the step type. A subclass implements `getSteps(ast)`, or, better, `getStepBatches(ast)`, a generator that yields arrays of steps and returns the `TraceEnd`, so that steps are sent while the program runs. The base class does the batching and the replay; the evaluator calls `sendSteps(ast)`.

## 3. The evaluator

In the language's repository, an evaluator

1. registers the runner plugin: `conductor.registerPlugin(TheRunnerPlugin, ...)`;
2. asks the host for the web plugin by its directory id: `conductor.hostLoadPlugin(DIRECTORY_ID)`;
3. on a run, parses the program, reads the host's run configuration, and calls `sendSteps(ast)`; then it reports the result or the error and its status as every evaluator does.

py-slang's `PyEStepperEvaluator` does exactly this.

The **run configuration** is the lines that have breakpoints in the editor's gutter. Conductor has no message for it, so the host serves it as a virtual file, `/__run_config__`, which an evaluator fetches with `requestFile`; py-slang and js-slang each read it with a small helper, `fetchRunConfig`. The file used to be called `/__cse_config__`, after the first tool that used it; the helpers still fall back to that name when a host does not serve the new one (source-academy/frontend#4648).

A visualizer's evaluator is not for running a program in the editor. It is a bundle of its own, and its own entry in the language directory.

## 4. The web plugin

The web plugin's bundle default-exports the plugin class. The host constructs it with `(conduit, channels, tabService, hostServices?)`. In its constructor the E-Stepper's plugin

1. subscribes to the channel and keeps what arrives in a small store (a `batch` that does not continue the steps that came before it is dropped, not put in the wrong place);
2. sends `request`, so that the runner replays a trace that it already has;
3. registers a tab with `tabService.registerTab({ id, label, iconName, body, hidesRepl, resizable })`, whose `body` is a React component that reads the store with `useSyncExternalStore`;
4. calls `tabService.revealTab(id)`, which makes the tab appear without taking the user's focus away (`showTab` would focus it).

`hidesRepl` says that the host's REPL is of no use while the tab is shown (the tab shows the output itself), and `resizable: false` that the tab's layout depends on the space it was given.

A tab looks after itself: it handles its own keys on its root element, it shows the `error` message itself, and it does its own fullscreen. The host provides React, React DOM, Blueprint (`@blueprintjs/core` and `@blueprintjs/icons`), Konva and `react-konva`, `react-ace` and lodash to a plugin when it is loaded; list them as peer dependencies and do not bundle them. Anything else is built into the plugin.

## 5. What the host offers

Beyond the tab service, a host may pass the plugin a few optional services, as `hostServices` (the type is `IHostContract` in `common-tabs`, from version 0.2.0). A plugin must work without them.

- `editor.highlight(lines)` marks lines of the editor, as pairs `[first, last]`, 1-based and inclusive. Call it with no lines to clear. How a highlight looks is the host's to decide.

The contract grows only when a visualizer needs more, by adding an optional member.

## 6. The directory entries

The **plugin directory** entry says what the plugin is and where its bundle is. This is the E-Stepper's:

```ts
export const eStepperPlugin: IPluginDefinition = {
  id: "e-stepper",
  name: "E-Stepper",
  description: "...",
  tab: {
    id: "e-stepper",
    label: "E-Stepper",
    iconName: "flow-review",
    hidesRepl: true,
    resizable: false,
  },
  resolutions: {
    [PluginType.WEB]:
      "https://source-academy.github.io/plugins/web/e-stepper/index.mjs",
  },
};
```

The `tab` is there so that the host can show a placeholder for the tab, and know how it behaves, before the plugin has loaded. The id must be the one that the evaluator passes to `hostLoadPlugin`.

The **language directory** entry offers the visualizer for a language: an evaluator of its own, with `plugin` set to the plugin's id and `path` to its bundle. Such an evaluator is hidden from the evaluator dropdown. The host selects it when the user opens the plugin's tab, and deselects it when they leave. A language offers the tab if, and only if, one of its evaluators names the plugin.

## Building and releasing

In the `plugins` repository, each package has a `manifest.json`: `{"type": "installable"}` for the `common-` and `runner-` packages, which are published to npm, and `{"type": "external"}` for the web plugin, which is built into one `index.mjs`, wrapped so that the host can load it with its own `require`, and deployed to GitHub Pages at `https://source-academy.github.io/plugins/web/<tool>/index.mjs`.

- A change to a published package needs a changeset (`yarn changeset`). Merging a pull request with one opens a **Version Packages** pull request; merging that publishes the packages.
- The host does not install a web plugin from npm: the bundle is deployed from `main` on every merge. The existing ones are named in `ignore` in `.changeset/config.json`, so they need no changeset (a changeset for an ignored package is never consumed); add a new one there.
- An evaluator that uses a new version of the runner package bumps it and is deployed from its own repository.

## The E-Stepper as the model

| To read                            | In                                                                                                                                                                                            |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The channel, the ids, the messages | [`common-e-stepper`](https://github.com/source-academy/plugins/tree/main/src/common/e-stepper)                                                                                                |
| The runner's base class            | [`runner-e-stepper`](https://github.com/source-academy/plugins/tree/main/src/runner/e-stepper), on [`runner-stepper`](https://github.com/source-academy/plugins/tree/main/src/runner/stepper) |
| The host plugin and the view       | [`web-e-stepper`](https://github.com/source-academy/plugins/tree/main/src/web/e-stepper), `EStepperHostPlugin.tsx`                                                                            |
| The plugin directory entry         | [`plugin-directory`](https://github.com/source-academy/plugin-directory/tree/main/src/plugins), `eStepper.ts`                                                                                 |
| An evaluator that serves it        | [`py-slang`](https://github.com/source-academy/py-slang/tree/main/src/conductor), `PyEStepperEvaluator.ts` and `estepper/PyEStepperRunnerPlugin.ts`                                           |

The other shapes that exist:

- **The Stepper** is one plugin for several languages. The evaluator sends a `profile` with the rendering rules for its language, and the plugin draws with them.
- **The Data Visualizer** shows data structures, over a channel of its own.
- **The CSE machine** is a plugin, for languages that share the environment model: `web-cse-machine` in the plugins repository, with the directory id `cse-machine` (source-academy/plugins#223 and #226), and the frontend no longer has a built-in copy (source-academy/frontend#4646). Its evaluators extend `runner-cse-machine` and load it with `hostLoadPlugin`, like the Stepper. A language with another mental model does not use it, and brings a plugin of its own.

## Checklist

- [ ] A protocol package with a channel id, a directory id and the message types.
- [ ] A runner plugin that sends batches while the program runs, ends them with `complete` or `cut-off`, and answers `request`.
- [ ] A web plugin that registers a tab and reveals it, and works with no host services.
- [ ] An entry in the plugin directory, with the tab described.
- [ ] An evaluator that registers the runner plugin and calls `hostLoadPlugin` with the directory id.
- [ ] An entry in the language directory for that evaluator, with `plugin` set.
- [ ] A changeset for each published package.
