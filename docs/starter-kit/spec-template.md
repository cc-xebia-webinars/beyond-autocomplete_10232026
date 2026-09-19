# Spec: <Feature Name>

## Goal

<Who needs this and why, in two or three sentences. The why helps the agent make the small decisions the spec doesn't cover.>

## Context

- <The files, functions, or patterns to reuse, so the agent doesn't write a second version of something that already exists.>
- <Anything about the domain that's easy to get wrong, such as time zones, currencies, or permissions.>

## What to Build

- <The behavior, endpoint by endpoint or screen by screen. Include the error cases and what each one returns.>

## Constraints

- Don't change <the existing rules, checks, or tests that must stay as they are>.
- Don't add a dependency.
- <Where the new code should live.>

## Acceptance Criteria

1. <A specific, checkable example with real values, such as "a weekly booking at 10:00 stays at 10:00 after the clocks change".>
2. <One criterion for each error case.>
3. Every existing test still passes, unchanged, and each criterion above has a test.

## Out of Scope

- <What not to build, so the agent doesn't build it.>
