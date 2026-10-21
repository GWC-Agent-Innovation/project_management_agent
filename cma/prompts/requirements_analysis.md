# Requirements Analysis Methodology

Use this methodology whenever you analyze raw Slack requirements (chat text plus any extracted document/attachment text) into the `project_details.md` specification.

## Reading the source material

- Treat every message and attachment as a fragment of one shared context — cross-reference them rather than summarizing each in isolation.
- Distinguish firm requirements ("must", "will") from open questions, assumptions, and wishes ("maybe", "could we").
- Note anything that reads as a constraint (deadline, budget, compliance, existing system to integrate with) even if it's mentioned only once in passing.
- If two parts of the source material conflict, surface the conflict explicitly in the document rather than silently picking one.

## Document structure

1. **Project Title & Jira Key** — one clear H1-style title line, no filler ("Project for X" is worse than "X Inventory Tracker"), followed by the Jira project key determined in Step 1 of the workflow.
2. **Project Overview** — 3-6 sentences: what it is, who it's for, the problem it solves, the ultimate goal. This is the paragraph a stakeholder reads first.
3. **Core Requirements** — split into **Functional Requirements** and **Non-Functional Requirements**, each as a grouped bullet list (group by feature area / module, not chronologically as they were mentioned in chat). Include a short **Assumptions & Open Questions** subsection if anything in the source material was ambiguous.
4. **Technology Stack** — only state a technology if either (a) it was explicitly named in the source material, or (b) it's the obvious standard choice for the stated application type (e.g. a web app implies a frontend framework and a database). Never propose AI/ML, blockchain, or other specialized stacks unless the requirements actually call for them.
5. **Action Plan / Tasks** — a checklist (`- [ ]`) grouped by the actual pages/modules named in the requirements (e.g. if a Login Page, Dashboard, and Reports Page are mentioned, have a checklist group for each with concrete sub-tasks, not a generic "build backend" bullet).
6. **Immediate Next Steps** — 3-5 numbered items, the literal first things a team would do to start building the highest-priority module.

## Quality bar

- Be thorough — don't omit anything mentioned in the transcript, even minor details.
- Don't editorialize about the quality of the requirements; document what's there and flag gaps neutrally.
- Prefer concrete, testable requirement statements over vague ones ("supports up to 500 concurrent users" beats "should scale well").
