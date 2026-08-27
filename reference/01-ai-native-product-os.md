# AI-Native Product OS

## Purpose

The AI-Native Product OS is a reference architecture for structuring product knowledge so that product teams and AI agents can work from the same durable, version-controlled context.

The core idea is simple:

> Product knowledge should not live only in meetings, chat threads, individual memory, scattered documents, and disconnected tools. It should be organized so both humans and agents can reliably understand the product, find the right context, trace decisions to sources, and execute recurring workflows.

This project should demonstrate how a modern product organization can make its operating context machine-readable without turning the repository into a dumping ground.

The repository should position the author as someone who understands not only how to use AI agents, but how to redesign product-team information architecture around them.

---

## Why this project matters

AI agents become less useful when they operate in a poorly structured environment.

Common problems include:

- product knowledge scattered across dozens of tools
- duplicate or contradictory definitions
- old decisions remaining indistinguishable from current decisions
- agents loading too much context
- agents missing important context because there is no clear navigation model
- feature information fragmented across product, engineering, analytics, design, and customer research
- no clear provenance between raw evidence and derived conclusions
- recurring workflows described informally rather than made executable
- humans repeatedly re-explaining the same context to agents

The Product OS should address these problems through deliberate context architecture.

---

## Product positioning

### Short positioning statement

**A reference architecture for organizing product-team knowledge so humans and AI agents can navigate, reason, and execute effectively from shared context.**

### Target users

Primary:

- Product Directors and Heads of Product
- Product Managers
- Product Operations leaders
- Engineering Managers
- AI transformation leads
- teams adopting Claude Code, Codex, or other agentic development environments

Secondary:

- Design leaders
- Data and analytics teams
- Technical program managers
- startup founders building AI-native operating models

---

## Core principles

### 1. Context is an operating system, not a document archive

The repository should not attempt to store everything.

Its purpose is to store information that benefits from:

- version control
- structured navigation
- durable reuse
- explicit ownership
- traceability
- agent access

External systems should remain external when they are the better source of truth.

Examples:

- Figma stays in Figma
- Jira or Linear stays the delivery system of record
- warehouse data stays in the warehouse
- dashboards stay in analytics tools
- CRM data stays in the CRM

The Product OS stores:

- definitions
- references
- decisions
- structured summaries
- requirements
- architecture notes
- feature indexes
- workflows
- research conclusions
- links to authoritative external systems

---

### 2. Progressive disclosure

Agents should not load the entire repository.

The root context should contain only what is universally useful.

Each meaningful folder should contain local instructions describing:

- what is stored there
- how artifacts are named
- what is authoritative
- what related folders exist
- what an agent should load next depending on the task

This creates a navigable context tree.

Example:

```text
/
├── CLAUDE.md
├── product/
│   ├── CLAUDE.md
│   ├── strategy/
│   ├── discovery/
│   └── features/
├── engineering/
│   ├── CLAUDE.md
│   ├── architecture/
│   └── plans/
├── analytics/
│   ├── CLAUDE.md
│   ├── metrics/
│   └── experiments/
└── customers/
    ├── CLAUDE.md
    ├── interviews/
    └── summaries/
```

The agent should walk the tree rather than ingest everything at once.

---

### 3. Feature-centered reassembly

Functional folder structures are useful for ownership, but they fragment information.

A feature may involve:

- PRD
- engineering RFC
- implementation plan
- experiment design
- dashboard
- customer interviews
- Figma
- tickets
- launch plan
- incident history

The Product OS should provide a feature index that reassembles those artifacts.

Example:

```yaml
feature: ai-query-review
status: development

product:
  prd: product/features/ai-query-review-prd.md

engineering:
  rfc: engineering/features/ai-query-review-rfc.md
  plan: engineering/plans/ai-query-review.md

analytics:
  experiment: analytics/experiments/ai-query-review.md
  dashboard: https://...

design:
  figma: https://...

delivery:
  epic: https://...

research:
  interviews:
    - customers/interviews/2026-07-15-customer-a.md
    - customers/interviews/2026-07-21-customer-b.md
```

This file becomes a join table across the operating system.

---

### 4. Naming conventions are part of retrieval architecture

Files should be predictably named.

Examples:

```text
{feature}-prd.md
{feature}-rfc.md
{feature}-plan.md
{feature}-launch.md
{feature}-experiment.md

YYYY-MM-DD-{customer}-interview.md
YYYY-MM-DD-{topic}-decision.md
YYYY-MM-DD-{incident}-review.md
```

Predictable naming reduces search dependency.

Agents can infer likely paths.

---

### 5. Define shared vocabulary once

Terms should not be redefined in every document.

Create explicit reference files for:

- product terminology
- user segments
- business metrics
- customer categories
- lifecycle stages
- product statuses
- risk levels
- experiment states

Example:

```text
reference/
├── terminology.md
├── metrics.md
├── customer-segments.md
└── status-definitions.md
```

Downstream artifacts should reference these definitions.

---

### 6. Preserve provenance

Keep raw evidence close to derived conclusions.

Example:

```text
customers/
├── interviews/
│   ├── raw/
│   └── summaries/
```

The summary should link to the raw source.

This allows:

- human verification
- agent citation
- re-analysis
- correction when interpretation changes

A claim should ideally be traceable to evidence.

---

### 7. Durable context and transient context should be separated

Durable:

- strategy
- terminology
- approved decisions
- canonical metrics
- system architecture
- approved requirements

Transient:

- working hypotheses
- early drafts
- debugging notes
- temporary research
- unapproved alternatives
- meeting scratchpads

Do not mix them without clear labels.

---

## Recommended repository structure

```text
/
├── README.md
├── CLAUDE.md
├── feature-index.yaml
│
├── product/
│   ├── CLAUDE.md
│   ├── strategy/
│   ├── roadmaps/
│   ├── discovery/
│   ├── features/
│   └── launches/
│
├── engineering/
│   ├── CLAUDE.md
│   ├── architecture/
│   ├── rfcs/
│   ├── plans/
│   └── incidents/
│
├── design/
│   ├── CLAUDE.md
│   └── references/
│
├── analytics/
│   ├── CLAUDE.md
│   ├── metrics/
│   ├── experiments/
│   └── dashboards/
│
├── customers/
│   ├── CLAUDE.md
│   ├── interviews/
│   ├── summaries/
│   └── accounts/
│
├── operations/
│   ├── workflows/
│   ├── reviews/
│   └── templates/
│
├── reference/
│   ├── terminology.md
│   ├── metrics.md
│   ├── segments.md
│   └── status-definitions.md
│
└── .claude/
    ├── skills/
    ├── commands/
    └── agents/
```

---

## Executable workflows

The Product OS should demonstrate that process can be encoded as executable instructions.

Examples:

### Customer interview workflow

1. Collect transcript.
2. Normalize metadata.
3. Produce structured summary.
4. Extract pains, goals, objections, and evidence.
5. Link findings to existing product areas.
6. Flag genuinely new signals.
7. Update the relevant feature or problem index.
8. Preserve the source transcript.

### Bi-weekly product update

1. Gather delivery status.
2. Gather experiment results.
3. Gather customer insights.
4. Compare against OKRs.
5. Draft update.
6. Request PM review.
7. Publish approved version.
8. Archive prior cycle.

### New feature intake

1. Capture problem.
2. Identify supporting evidence.
3. Check for existing feature/problem entries.
4. Draft intent.
5. Resolve constraints.
6. Create PRD only after approval.

The repository should show both the human review points and automated stages.

---

## Agent behavior

Agents using the Product OS should follow explicit rules.

### Read behavior

- Start from root instructions.
- Load local folder instructions before reading many files.
- Prefer canonical references over duplicate definitions.
- Use feature indexes before repository-wide search.
- Cite source files when producing conclusions.
- Distinguish current decisions from archived material.

### Write behavior

- Never overwrite raw source evidence.
- Write new decisions into dated decision files.
- Update indexes when creating major artifacts.
- Maintain naming conventions.
- Mark draft vs approved state explicitly.
- Ask for approval before modifying canonical strategy or shared definitions.

---

## AI-specific design decisions

The repository should explain why it uses structured files instead of relying entirely on embeddings.

Possible rationale:

- predictable paths are cheaper than broad semantic search
- hierarchical instructions reduce unnecessary context
- canonical files improve determinism
- version control provides auditability
- structured indexes allow agents to reassemble fragmented artifacts
- retrieval can still be added selectively for large unstructured collections

The project should not claim that vector search is unnecessary in all cases.

Instead:

> Use explicit structure when the knowledge domain is stable and addressable. Use semantic retrieval where the source space is too large or unstructured for deterministic navigation.

---

## Evaluation ideas

This project should include a small benchmark showing whether the context architecture actually helps.

Example task set:

- find the current definition of a metric
- locate all artifacts related to one feature
- identify the approved product decision
- summarize customer evidence behind a roadmap item
- find the latest experiment result
- identify conflicting or outdated context
- generate a bi-weekly product update

Compare:

### Baseline

Agent receives repository with no routing structure.

### Product OS

Agent uses:

- root instructions
- local routing files
- feature index
- canonical definitions

Measure:

- task completion accuracy
- wrong-source rate
- context tokens consumed
- number of files opened
- time to answer
- citation accuracy

The point is not academic benchmarking.

The point is showing that product context architecture improves agent reliability.

---

## Demo

A strong demo should show one complete workflow.

Example:

**Question:**
"Why are we building AI Query Review, what evidence supports it, and what is currently blocking launch?"

The agent:

1. checks the feature index
2. loads PRD
3. loads decision record
4. checks interview summaries
5. checks engineering plan
6. checks experiment status
7. produces a cited answer

Then show the same question against an unstructured repository.

---

## What this project should signal

This project should make a hiring manager conclude:

- understands context engineering
- understands product operating models
- understands agent information needs
- thinks about organization design, not just prompts
- can connect AI-native workflows to real product leadership
- understands provenance, governance, and decision traceability
- can structure knowledge for both people and machines

---

## Suggested future extensions

- Codex-compatible instructions
- Claude Code skills
- automated broken-link checks
- canonical-document validation
- stale-context detection
- conflict detection across decisions
- automatic feature-index maintenance
- agent-generated decision summaries
- optional hybrid retrieval for large research collections
- example integrations with Linear, Jira, GitHub, Figma, or analytics tools
- role-specific onboarding agents

---

## Avoid

Do not turn this into:

- a generic PM template library
- hundreds of empty folders
- an overcomplicated taxonomy
- a Notion clone in Git
- a collection of prompts without architecture
- a repository that requires loading everything into context
- an artificial demo with no realistic product artifacts

The credibility comes from showing how the pieces work together as a system.
