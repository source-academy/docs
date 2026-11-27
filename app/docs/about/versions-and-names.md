# Versions and names

## The versions

A version keeps its name until the next one is named. 2019 and 2021 had a leadership team but **no new version**: Cadet carried on through 2019, and Knight through 2021.

| Version              | Year            | Main points                                                                                                                                                                                                                                                                                                                                                                                              |
| -------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Spell**            | 2026            | The current version. Language implementations run as Conductor evaluators, including Python (py2js, a Python CSE machine) and OCaml. Local-file imports for Python, search in the Python SICP book (SICPy), and a new login through NUS Entra ID. The old CAS and SAML logins, Sourcecast and Sourcereel, and the translations (i18n) were removed. The most active year in the history of the frontend. |
| **Charm**            | 2025            | Frontend tooling moved to rsbuild and BlueprintJS v6. The old Concurrent and Interpreter paths were removed. A message channel to the VS Code extension. Structured logging in the backend.                                                                                                                                                                                                              |
| **Strange**          | 2024            | The frontend moved its state handling to Redux Toolkit, step by step (eight parts). SAML login in frontend and backend. A wrapper around the OpenAI API in the backend.                                                                                                                                                                                                                                  |
| **Merlin**           | 2023            | Release v1.5.0 (March 2023). Editing several files at once, Stories with search, search in SICP JS, and the environment visualizer extended with the agenda and the stash (the CSE machine). Typed variants of Source in the backend.                                                                                                                                                                    |
| **Rook**             | 2022            | A quiet year. The HTML chapter, the editor key-binding setting, and a long migration of the frontend to function components. Source versions in the backend.                                                                                                                                                                                                                                             |
| **Knight**           | 2020 (and 2021) | Re-grading of submissions, GroundControl, the frontend can be disabled during an exam, and jQuery was removed. In 2021: the v2 backend API, courses for several institutions (multi-tenant, August 2021), login through Auth0, and a mobile navigation bar.                                                                                                                                              |
| **Cadet**            | 2018 (and 2019) | The first version with this frontend and backend (the backend started in November 2017, the frontend in May 2018; release 1.0.0 in August 2018). Assessments, grading and XP, autograding on AWS Lambda, and Source §2. In 2019: notifications, Sourcecast and Sourcereel (recording and replaying a session), a maximum execution time, and the releases 1.4.0 and 1.4.1 (September 2019).              |
| **Source Academy 2** | 2017            | Before the repositories described here.                                                                                                                                                                                                                                                                                                                                                                  |
| **Source Academy**   | 2016            | The original.                                                                                                                                                                                                                                                                                                                                                                                            |

## What the words mean

| Word                      | Meaning                                                                                                                                                                 |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Source Academy**        | The whole system: what students and educators use, and everything behind it. This is the name to use in text.                                                           |
| **Spell**, **Charm**, …   | A version of the system, named by the team of that year. A version name is used only when a specific version is meant.                                                  |
| **Source**                | The original name of the JavaScript sublanguages taught in the SICP JS book (Source §1 to §4). They are now called JavaScript §1 to §4. Not the same as Source Academy. |
| **slang**                 | A language implementation for Source Academy, named after its language: `js-slang`, `py-slang`, `ocaml-slang`, …                                                        |
| **Conductor**             | The protocol and library through which the frontend (the host) runs a language implementation (an evaluator), which can live in a web worker or on a server.            |
| **Evaluator**             | A language implementation that speaks the Conductor protocol.                                                                                                           |
| **Frontend**, **backend** | The web application in the browser, and the server with the database, the courses and the assessments.                                                                  |
| **Grader**                | The service that runs submitted programs against the tests of an assessment.                                                                                            |
| **Module**, **plugin**    | A library of extra functions with optional user interface (the `modules` repository), and an extension of the frontend (the `plugins` repository).                      |

## Historical names in code

**Cadet** is also the name of the backend's code. These identifiers keep the name. Renaming them would break deployed configuration and releases and help nobody, so they are not renamed:

- the Elixir application `:cadet` and the `Cadet.*` modules, and the Mix tasks such as `mix cadet.token`;
- the backend configuration file `cadet.exs` (`/etc/cadet.exs` on a server);
- the frontend's old repository name `cadet-frontend`, which GitHub redirects, and the Sentry project of the same name;
- the `--cadet-color-*` CSS variables in the frontend;
- the title of the backend's API description.

If you read "cadet" in code or in an old document, it means the Source Academy backend (or the whole system, as it was in 2018).

## How a version gets its name

The name is chosen by Martin Henz. Recently the core team has made suggestions, and the best one, as judged by Martin Henz, has won a coffee.

When a name is chosen, add a row for it to the table above: this page is where the versions and their years are recorded. (The [contributors page](https://sourceacademy.org/contributors) of the frontend still lists them in its own text.)

<!-- cspell:ignore Henz sublanguages -->
