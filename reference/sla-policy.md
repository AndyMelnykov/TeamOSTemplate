# SLA Policy

Canonical response-time policy for inbound feature requests filed via `/feature-request-intake`. Every request is assigned exactly one `Impact` level, which determines how quickly it must get a substantive response (triage, not resolution).

| Impact | Definition | Respond by |
|--------|------------|------------|
| High | Blocking a paying account from renewing or expanding, or reported independently by more than one Enterprise account (see `segments.md` for the Enterprise definition) | 3 business days |
| Medium | Reported by multiple accounts of any segment, or by a single Enterprise account, without blocking renewal/expansion | 10 business days |
| Low | Reported by a single non-Enterprise account, or a workaround already exists | Next planning cycle |

"Respond by" means triage happens by that date (the request moves out of `needs-triage` — see `.claude/skills/triage/SKILL.md`), not that the request ships by then. Impact is stated explicitly by whoever files the request (see `.claude/skills/feature-request-intake/SKILL.md`) — it is never inferred automatically from evidence search results.
