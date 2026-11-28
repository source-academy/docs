# Backend

[`backend`](https://github.com/source-academy/backend) (the application is called **Cadet**) is the server of Source Academy @ NUS and of any deployment that has accounts, courses and assessments. Elixir, Phoenix and PostgreSQL; Ecto for the database and Oban for background jobs. Checked against the repository on 28 November 2026.

## What it does

- **Accounts and authentication**: the frontend sends the OAuth2 authorisation code to the backend, and an identity **provider** exchanges it for a token and a user id (`lib/cadet/auth/provider.ex`). The providers are ADFS, GitHub and OpenID Connect, the last with claim extractors for Auth0, Cognito, Google, MIT, MIT CSAIL and NUS Entra ID (`lib/cadet/auth/providers`). Sessions use Guardian tokens.
- **Courses and assessments**: courses, assessment configurations, assessments, questions, answers and submissions (`lib/cadet/courses`, `lib/cadet/assessments`). An assessment is created in the admin interface or **uploaded as an XML file** (`Cadet.Updater.XMLParser`, called from the admin assessments controller); the XML format is the one used by the CS1101S assessment repository.
- **Grading**: when a submission is made, the backend queues autograding jobs; see [Grader](./grader) and [A run and a submission](./run-and-submission). Staff then grade manually in the frontend's grading screens.
- **Other features**: notifications, the leaderboard and incentives (achievements), stories, teams, the AI chat assistants and generated comments (`lib/cadet/chatbot`, `lib/cadet/ai_comments`), and registration of remote-execution devices (`lib/cadet/devices`, with MQTT for EV3 robots).
- **The API**: Phoenix controllers under `lib/cadet_web`, with a Swagger description served at `/swagger` in development.

## Background jobs

Oban runs the jobs, in queues with these limits: `default` 10, `notifications` 1, `autograder` 20 and `autograder_results` 5 (`config/config.exs`). Autograding uses two workers: `Cadet.Autograder.LambdaWorker` invokes the grader and `Cadet.Autograder.ResultStoreWorker` writes the results to the database (it has a queue of its own, with lower concurrency, because grading takes much longer than the database write). A Quantum cron job (`config/config.exs`, daily at 00:01) closes and grades the assessments that were due the day before.

## Where to read more

The README (setup with PostgreSQL, secrets, MQTT for remote execution), `deployment/` for how it is run (see [Deployment](./deployment)), and the database schema picture `schema.png` at the root of the repository.
