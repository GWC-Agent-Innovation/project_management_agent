# Backlog Planning Methodology

Use this methodology to turn a requirements analysis into an Agile backlog.

## Proportional Backlog Sizing Standard (STRICT SIZING RULES)

You MUST scale the backlog complexity strictly to the input requirements' actual size:

- **Small / Simple Scope (1-3 Features)**:
  * **Epics**: 1 to 2 Epics max.
  * **User Stories**: 2 to 4 Stories TOTAL for the whole project (1-2 per Epic).
  * **Sub-tasks**: 1 to 2 essential sub-tasks per story (MAX 4-6 sub-tasks total across project).
  * **Sprints**: 1 Sprint.
  * **STRICT**: DO NOT create 10+ stories or 30+ sub-tasks for a small request!

- **Medium Scope (4-8 Features)**:
  * **Epics**: 2 to 3 Epics.
  * **User Stories**: 5 to 8 Stories total.
  * **Sub-tasks**: 2 sub-tasks per story.
  * **Sprints**: 2 Sprints.

- **Large Enterprise Scope (9+ Complex Modules)**:
  * **Epics**: 3 to 5 Epics max.
  * **User Stories**: 10 to 15 Stories total.
  * **Sub-tasks**: 2 to 3 sub-tasks per story.
  * **Sprints**: 3 to 4 Sprints.

## Per-story fields

For every story, produce:

- **Story Points** — Fibonacci scale (1, 2, 3, 5, 8, 13). Base the estimate on scope and technical complexity implied by the requirements, not on arbitrary defaults.
- **Acceptance Criteria** — 2-3 criteria, preferably Gherkin-style (`Given/When/Then`) or clear checkable sentences.
- **Technical Sub-tasks** — a checklist of the concrete developer tasks needed to implement the story (e.g. "Build the login form component", "Add POST /auth/login endpoint", "Write integration test for failed login").
- **Sprint** — assign to Sprint 1, Sprint 2, ... Sprint N dynamically based on functional dependencies and team workload (do not exceed 10 story points per person in a single sprint). Justify borderline calls with a one-line reason.
- **Assignee** — pick exactly one person from the team roster provided in the session kickoff message, matched by role/skill (frontend work to a Frontend Developer, backend to a Backend Developer, schema/queries to the Database Engineer, test plans to a QA Tester, visual/UX work to the UI/UX Designer, CI/CD or infra to the DevOps Engineer). Spread the workload evenly across the team — do not give any single person more than 10 story points within one sprint.

## Sprint plan summary

Before the per-story breakdown, give a short summary: Sprint 1 goal (MVP focus), Sprint 2 goal (enhancement/integration focus), and the total estimated story points across the whole backlog.

## Quality bar

- Every story must have all five fields above — no placeholders, no "TBD".
- Don't invent stories for requirements that don't exist; don't drop requirements that do.
- If the requirements are too thin to support a full backlog, produce a smaller, honestly-scoped one rather than padding it.
