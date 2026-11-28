# Evaluators

An **evaluator** runs programs of one language, as a [Conductor](./conductor) runner: in a Web Worker in the browser, and in a worker thread in the [grader](./grader). The [language directory](./directories) names each evaluator and gives the URL of its entry file. Checked against the language directory and the repositories on 28 November 2026.

| Language                                     | Repository                                                     | Notes                                                                                                                                                                                                                                              |
| -------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Source §1 to §4 (sublanguages of JavaScript) | [`js-slang`](https://github.com/source-academy/js-slang)       | A default evaluator per chapter, plus evaluators that offer a tool: the Stepper (§1, §2) and the CSE machine (§3, §4). The language documentation is published at <https://docs.sourceacademy.org/javascript>                                      |
| Python §1 to §4, §4 Typed, full Python       | [`py-slang`](https://github.com/source-academy/py-slang)       | Several evaluators per chapter: Python compiled to JavaScript, a virtual machine (PVML), WebAssembly, CPython through Pyodide, and ones for the Stepper, the E-Stepper and the CSE machine. Documentation: <https://docs.sourceacademy.org/python> |
| Scheme                                       | [`scm-slang`](https://github.com/source-academy/scm-slang)     | One evaluator                                                                                                                                                                                                                                      |
| Java                                         | [`java-slang`](https://github.com/source-academy/java-slang)   | One evaluator; a Java parser and runtime in TypeScript                                                                                                                                                                                             |
| OCaml                                        | [`ocaml-slang`](https://github.com/source-academy/ocaml-slang) | The real OCaml toplevel, Menhir and ocamllex, compiled to JavaScript and run in a worker                                                                                                                                                           |

Other repositories contain language implementations that are not in the language directory today (for example `pie-slang` for Pie, `c-slang` for C, and `sinter` and `pynter` for microcontrollers).

## What an evaluator provides

- An entry file that creates a `Conduit` and registers the runner plugin with the evaluator (see [Conductor](./conductor)), published on GitHub Pages.
- The implementation of `IEvaluator`: evaluating chunks and files, sending results, errors and output.
- For a tool, the evaluator's side of the plugin: the `runner-*` package, whose base class turns the evaluator's steps into messages on the plugin's channel. See [Writing a visualizer plugin](../writing-a-visualizer-plugin).
- Support for modules, through the Conductor module interface.

## Two copies of an evaluator

The browser loads an evaluator from its GitHub Pages site. The grader keeps a vendored copy (see [Grader](./grader)). A fix to an evaluator reaches grading only when the copy is updated.
