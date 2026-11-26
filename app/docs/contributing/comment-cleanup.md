# Cleaning up comments

This guide is for one job: going through existing code and removing comment clutter, in a pull request that changes comments and nothing else.

It applies to every Source Academy repository. Each repository's `AGENTS.md` has the short rules for writing new comments, and the facts that differ from repository to repository: which files are generated, and which commands to run. This guide says how to judge the comments that are already there.

## What a cleanup pull request is

- **Comment-only.** No code changes, no renames, no reformatting.
- **One file, or one folder, per pull request.** Aim for at most about 150 comment lines changed, so that a person can read all of it.
- **Not in generated files.** The repository's `AGENTS.md` lists them.

## For each comment

Read the code first, then ask in this order. Stop at the first question that decides it.

1. **Is it true?** If it contradicts the code, fix it or delete it. A wrong comment is worse than none.
2. **Does it say why?** A reason, a constraint, an invariant, a workaround, a trap, the format of some data. If it only says what the next lines do, or tells the history ("previously", "used to", "fixed per review"), delete it.
3. **Is it as short as it can be?** Shorten it to the reason. Drop issue and pull request numbers and the names of reviewers or review tools. Keep one `see #123` only if the issue holds context that the comment cannot carry.
4. **Is it in the right place?** An explanation of a whole module's model belongs at the top of that module. Anything else longer than about ten lines belongs in a document, with a one-line pointer.
5. **Does it document an exported function?** Keep it: documentation generators and editors show these to users. Fix the wording only.

When unsure, keep the comment and say so in the pull request.

### Examples

These are from `py-slang`.

| Comment                                                                                                              | Decision                                        | Why                                                    |
| -------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------ |
| the 52-line header of `src/engines/py2js/runtime.ts` (`int -> bigint`, `float -> number`, `None -> null`, and so on) | keep                                            | it states an invariant that the whole file relies on   |
| "... `enclosingPreludeFunction` (py-slang#397). Unset for both native/bridged ..."                                   | keep the sentence, drop `(py-slang#397)`        | the explanation is the value; the number is history    |
| "... forever (issue #341). Populating the memo before descending means a ..."                                        | keep the sentence, drop `(issue #341)`          | it explains a trap (infinite recursion on cyclic data) |
| `// String concatenation: str + str only.` above `if (typeof l === "string" \|\| ...`                                | check that it is true, then keep, fix or delete | question 1 comes first                                 |

## Directives are code

Some comments are instructions to a tool, not text for people. Leave them exactly as they are: `eslint-disable...`, `@ts-expect-error`, `@ts-ignore`, `istanbul ignore ...`, `prettier-ignore`, `@jest-environment ...`, `#!` lines, license headers, `/// <reference ...>`, and the equivalents in other languages (for example Credo's `# credo:disable-for-next-line`).

## Never

- Change code, rename anything, or reformat.
- Delete a `TODO` that is still true. Open the issue and write `TODO(#123): ...`, or leave it as it is.
- Delete the only record of why a workaround or a test exists. Shorten it instead.

## Before you open the pull request

1. The repository's format, lint and test commands pass (see its `AGENTS.md`).
2. The code is unchanged. For TypeScript, compile the base commit and your branch with comments removed, and compare the output:

   ```bash
   yarn tsc -p tsconfig.json --removeComments --outDir /tmp/before   # on the base commit
   yarn tsc -p tsconfig.json --removeComments --outDir /tmp/after    # on your branch
   diff -r /tmp/before /tmp/after
   ```

   No difference means that no code changed. This check does not cover directives, so leave those alone. A script that does the check for every language is planned.

## The pull request

- **Title:** `Comments: <path>`.
- **Body:** the number of comment lines before and after; the long comments you kept, one line each on why; the comments you rewrote (before and after); the judgement calls a person should check; and "No code changed", with the output of the check.

## Afterwards

If the same clutter comes back, make the rules in the repository's `AGENTS.md` sharper. Do not add to this guide.
