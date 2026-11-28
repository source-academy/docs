# Conductor

[`conductor`](https://github.com/source-academy/conductor) is the standard communication interface for languages: the one way in which a host and an evaluator talk, whatever the language. Checked against the repository's README on 28 November 2026.

## Terms

- **Host**: an environment from which runners are created, such as the browser frontend, a command line, or the [grader](./grader).
- **Runner**: an environment where user code runs.
- **Evaluator**: a program that processes user code and produces the results.
- **Channel**: a named, bidirectional data stream between a host and a runner.
- **Chunk**: a piece of user code that belongs to no file (for example a line typed in the REPL).
- **Plugin**: a program loaded on demand that can receive messages and send on declared channels.

## How the parts fit

The host creates a `Conduit` for a Web Worker (or a worker thread) and registers a host plugin; the runner's entry file creates its own `Conduit` and registers the runner plugin with the evaluator (`initialise(MyEvaluator)`). The standard channels carry results (`__result`), errors (`__error`), standard output (`__stdio`) and status (`__status`). An evaluator implements `IEvaluator`; the abstract class `BasicEvaluator` needs only `evaluateChunk`, and `evaluateFile` can be overridden. The runner asks its host for files (`requestFile`) and for plugins to be loaded (`hostLoadPlugin`); the frontend answers in `src/features/conductor`.

## The module interface

Modules make no assumption about an evaluator's memory model. The evaluator provides functions with which a module reads, builds and calls values: the standard data types (void, boolean, number, integer, string, empty list, pair, array, closure, opaque, list), some passed as JavaScript values and some as identifiers, and a standard library. Errors thrown by modules and evaluators use the classes in `conductor/common` (such as `EvaluatorRuntimeError` and `EvaluatorSyntaxError`), so that hosts can recognise and show them.

## Using it

The frontend depends on Conductor as the npm package `@sourceacademy/conductor` (version `^0.8.3` on 28 November 2026; the repository's README still says to load it from GitHub, which is out of date). To run an evaluator in the frontend, deploy it so that it appears in the [language directory](./directories), or use the `conductor.evaluator.url` feature flag for one under development. The repository has a template, `conductor-runner-example`, for a new evaluator.
