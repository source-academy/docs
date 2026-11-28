# A run in the workspace, and a submission

Two paths cross most of the parts. Both were traced through the code on 28 November 2026.

## A run in the workspace

1. The learner picks a **language** (and, for some languages, an evaluator). The frontend offers the choices that the [language directory](./directories) lists.
2. On Run, the frontend creates a [Conductor](./conductor) host: it starts the evaluator's entry file, named in the directory, as a **Web Worker**, and registers a host plugin (`src/features/conductor`).
3. The frontend sends the program. The evaluator may ask the host for other files (`requestFile`); the frontend answers from the workspace's files, and serves the editor's per-run settings (the breakpoint lines) as a virtual file.
4. If the program imports a **module**, the module loader plugin finds it through the modules directory and loads the bundle.
5. The evaluator sends **output** on the `__stdio` channel, the **result** on `__result` and **errors** on `__error`; the REPL shows them. Status changes go on `__status`.
6. If the evaluator belongs to a **tool** (it names a plugin in the language directory), it asks the host to load the plugin (`hostLoadPlugin(id)`). The host looks the id up in the [plugin directory](./directories), imports the bundle from the URL given there, and the plugin registers its **tab**. The evaluator then streams its steps on the plugin's channel; the tab draws them, and can ask for a replay if it was opened late.

## A submission

1. A student works on an assessment in the **assessment workspace**. Answers are saved through the backend's API (`answer_controller`), and programs can be run as above.
2. On **submit**, the backend finalises the submission (`Cadet.Assessments.finalise_submission`): it sets the status, queues a notification for the staff member, and begins **autograding** (`GradingJob.force_grade_individual_submission`).
3. For each programming question with test cases, an **Oban job** is queued on the `autograder` queue. The `LambdaWorker` invokes the [grader](./grader) (an AWS Lambda function) with an event that names the evaluator, the programs and the test cases.
4. The grader runs each test case in the named evaluator, under a Conductor host, and returns a `Summary` of passes, failures and errors with scores.
5. A `ResultStoreWorker` on the `autograder_results` queue writes the result to the database.
6. **Staff** grade the rest in the frontend's grading screens (the backend marks an assessment as manually graded or not, in its configuration), and the student sees the result.

If the assessment's due date passes without a submission, a daily job (00:01) closes and grades the assessments that were due the day before.
