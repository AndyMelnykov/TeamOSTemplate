# Step 1: Engineering Status

## Goal

Produce the "What the Team Is Building Now" section with OKR tables showing current workstream status.

---

## Automated Part

### 1. Pull completed tickets

Query the ticketing system for issues completed in the last 2 weeks.

**Filters:**
- Team: example_product
- State: completed
- Updated: last 2 weeks from today's date

### 2. Map issues to OKR workstreams

Categorize each completed issue into one of the three OKR objectives:

**Generation Quality (OKR 1):**
- Multi-Page App Generation
- Component Library Support
- State Management Patterns
- Design Token Integration
- Responsive Layout Engine

**Enterprise & Deployment (OKR 2):**
- SSO / SAML Integration
- Audit Logging
- Team Workspaces
- CI/CD Pipeline
- Environment Management

**Platform & Integrations (OKR 3):**
- Git Provider Integration (GitHub, GitLab)
- Database Connectors
- Auth Provider Support
- Plugin / Extension API
- Cloud Provider Export (AWS, GCP, Azure)

### 3. Generate draft status tables

For each workstream, draft a status update based on what was completed and what appears to be in progress. Use the OKR table format from the reference file.

---

## Interactive Part

### 4. Present ticket summary to PM

Show:
- List of completed issues grouped by workstream
- Any issues that don't map cleanly to existing workstreams
- Draft status tables

### 5. Ask for additional context

Prompt: **"Dump any additional context: decisions made, meeting notes, things not in tickets, status changes I should know about."**

The PM will provide a single context dump. This is the primary source for nuanced status updates that the ticketing system can't capture (e.g., "Design complete but eng hasn't started" or "Blocked on external dependency").

### 6. Synthesize and draft

Combine ticket data + PM's context into the full "What the Team Is Building Now" section:
- Opening paragraph describing quarterly objectives
- OKR 1 table (Generation Quality)
- OKR 2 table (Enterprise & Deployment)
- OKR 3 table (Platform & Integrations)
- "Designs Complete" list (if applicable)

### 7. Write to output file

Write the section to the dated output file. Present draft for review before moving to Step 2.

---

## Output Format

```markdown
# [Month] 2026: What the Team Is Building Now

[Opening paragraph: example_product has three objectives this quarter...]

## Generation Quality (OKR 1)

**Goal:** [Goal from OKRs]

[Context paragraph if needed]

| Workstream | Why It Matters | Status |
|---|---|---|
| **[Workstream]** | [Business impact] | [Current status] |

## Enterprise & Deployment (OKR 2)

**Goal:** [Goal from OKRs]

| Workstream | Why It Matters | Status |
|---|---|---|
| **[Workstream]** | [Business impact] | [Current status] |

## Platform & Integrations (OKR 3)

**Goal:** [Goal from OKRs]

| Workstream | Why It Matters | Status |
|---|---|---|
| **[Workstream]** | [Business impact] | [Current status] |

## Designs Complete (Ready for Engineering)

- [Item 1]
- [Item 2]
```

---

## Notes

- The OKR goals themselves don't change within a quarter. Only the workstream rows and status column change.
- If a new workstream appears (not in previous cycle), add it to the appropriate OKR table and flag it to the PM.
- If a workstream is complete and shipped, move it out of the table and note it in the opening paragraph or a "Shipped" section.
