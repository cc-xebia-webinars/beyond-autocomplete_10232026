# Agentic Coding Checklist

Use this checklist when you hand a real engineering task to a coding agent such as GitHub Copilot's agent mode or Claude Code, and again when you set a repository up for a team that uses them. It follows the same order as the webinar: prepare the task, write the prompt, stay with the agent while it works, review what it produced, and make the setup shared. The demos in this repository show most of these checks in action.

## Before You Start a Task

- [ ] The task has a clear finish line that a test or a command can check, such as "these tests pass" or "this endpoint returns that response".
- [ ] The test suite passes before the agent starts, so a failure afterward means something.
- [ ] The tests cover the code the agent will change. If they don't, the first task is writing those tests.
- [ ] The task is small enough to review in one sitting. A large feature is split into slices that each leave the code working.
- [ ] You know which files and contracts are off limits, such as public APIs, database schemas, and other teams' code.

## Writing the Prompt

- [ ] The prompt says what you want and why, not only what to type.
- [ ] It names the code to reuse, so the agent doesn't write a second version of something that already exists.
- [ ] It lists the constraints: no new dependencies, no changes to existing tests, no edits outside the area of the task.
- [ ] It defines done as checks the agent can run itself, such as acceptance criteria, specific test cases, or a command that has to succeed.
- [ ] For a feature, the prompt is a short written spec the team can review, rather than a paragraph typed into a chat.
- [ ] For a bug, the prompt asks the agent to reproduce it with a failing test and explain the root cause before it fixes anything.
- [ ] For a refactor, the prompt says the behavior must stay exactly the same, and asks for a plan first.
- [ ] For tests of existing code, the prompt asks for expected values that come from running the code. For new behavior, they come from the spec. Neither comes from the agent's own arithmetic, which only makes the tests agree with its mistakes.

## While the Agent Works

- [ ] You read the plan before any code is written, and you push back on anything that breaks a constraint.
- [ ] Approvals stay on for commands, and you read each command before you allow it.
- [ ] You step in when the agent edits a test to make it pass, adds a dependency, touches files the task doesn't need, or repeats the same failing step.
- [ ] When you step in, you say what you want instead, rather than only stopping it.
- [ ] You restart from a checkpoint, or with a better prompt, when a run has gone the wrong way, instead of patching on top of it.

## Reviewing the Output

- [ ] You run the tests yourself, and every test that passed before still passes without having been changed.
- [ ] You read the new tests as carefully as the new code, because they're what the agent used to decide it was done.
- [ ] You read the whole diff, file by file, and check that nothing changed outside the task.
- [ ] A fix addresses the root cause, and you've checked the other places that use the faulty code.
- [ ] Edge cases specific to your domain are tested, such as time zones and daylight saving changes, rounding, empty inputs, or limits.
- [ ] A second reviewer looks at the change: a teammate, a second agent, or both. A second agent's findings are suggestions for you to judge, not a verdict.
- [ ] Agent-written changes go through the same pull request review and CI as any other change.

## Setting Up a Team Repository

- [ ] One command installs the project, one runs the tests, and one formats and lints, and they're written down where agents look.
- [ ] The tests are fast and reliable enough that an agent can run them after every change. A flaky test misleads an agent even more than it misleads a person.
- [ ] There's one shared instructions file, such as `AGENTS.md`, that's short, specific, reviewed like code, and kept up to date. Tool-specific files, such as `CLAUDE.md`, import it rather than copy it.
- [ ] The instructions cover what the code can't tell an agent: conventions, the files that are off limits, and rules such as "don't edit tests to make them pass".
- [ ] Lessons from agent sessions, such as a bug pattern or a convention someone got wrong, are added to the instructions file.
- [ ] Shared permission rules are checked in, so the safe commands run without prompts and risky ones, such as pushing, are denied.
- [ ] Rules that must always hold, such as formatting, are enforced by hooks or CI rather than requested in instructions.
- [ ] In a monorepo, each team's instructions apply only to its own part of the repository.
- [ ] The team has agreed which tasks agents are trusted with, who reviews their changes, and how agent work is labeled in pull requests.
