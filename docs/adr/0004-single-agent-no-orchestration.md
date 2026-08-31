# One agent per session, not a multi-agent pipeline

Recurring processes (customer-call summarization, bi-weekly updates, onboarding, PRD drafting) run as skills/commands executed by a single coding-agent session, not as a pipeline of specialized agents. The tasks in this repo are read-heavy and sequential (gather → draft → human review) rather than independently parallelizable, so a second agent would add coordination and failure-handling cost without a measurable quality or speed gain over one agent following an ordered skill.

## Consequences

If a future workflow genuinely needs to fan out independent, parallel subtasks — e.g. running the `evaluation/task-set.md` tasks across many sessions at once — that's the concrete trigger for reconsidering this decision, not "it would look more sophisticated."
