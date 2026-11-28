# Grader

[`grader`](https://github.com/source-academy/grader) runs a submission's test cases and reports a score for each. It is a component of the [backend](./backend), runs as an AWS Lambda function, and **knows no language**: the language is whatever evaluator the event names. Checked against the repository's README on 28 November 2026.

## What it does

1. It receives a JSON event from the backend. The event names the [Conductor](./conductor) evaluator that grades the question (`library.evaluator`, an id from the [language directory](./directories)), and carries the prepend, student and postpend programs and the test cases (a program, the expected answer and a score each).
2. For each test case it joins the prepend, student, postpend and test-case programs into one program and runs it in that evaluator, in a worker thread, under a Conductor host (`src/conductorGrader.ts`).
3. It returns a `Summary`: the total and maximum score and one result per test case: `pass`, `fail` (with the expected and the actual answer) or `error`. A test case's answer is compared with the last line the program prints.

## The evaluators are vendored

The grader keeps its own copy of the evaluators (`vendor/evaluators`, listed in `vendor/evaluators/manifest.json`), so that grading does not depend on the network. It refuses an event whose evaluator it does not have. To add or update one, `scripts/vendor-evaluator.sh` downloads it from the evaluator's GitHub Pages site (Source from js-slang, Python from py-slang, OCaml from ocaml-slang), and the manifest entry says how to load it. An evaluator that is updated and deployed for the browser is therefore **not** updated for grading until it is vendored again.

## Where to read more

The README (the full input and output formats, the manifest fields, timeouts).
