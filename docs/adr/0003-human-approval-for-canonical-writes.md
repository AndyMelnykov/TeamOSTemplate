# Human approval required before agents write to canonical/shared context

Agents may freely read, search, draft, and execute safe read operations across the repo, and may write new dated artifacts (call summaries, decision files, drafts) without asking. But agents must ask for approval before modifying `reference/` (terminology, metrics, segments, statuses, decision types) or `product/strategy/`, because a silent edit there would invalidate every downstream document that assumes that definition hasn't moved.

## Considered Options

Let agents edit canonical files freely and rely on git history / PR review to catch problems. Rejected: canonical files are read by many agent sessions before any human necessarily reviews the diff — the blast radius of a wrong edit is the whole repo's shared vocabulary, not one document.

## Consequences

Every skill or command that might touch `reference/` or `strategy/` has to build in an explicit approval step rather than writing straight through, which is slower than a pure autonomous-write model but keeps the one thing every other document depends on from drifting unreviewed.
