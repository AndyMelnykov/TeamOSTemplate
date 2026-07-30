# Write example_product Product Vision & Competitive Strategy Document

## Context
Leadership needs a comprehensive product vision and competitive strategy document that articulates why example_product is differentiated in the AI prototyping space, maps the competitive landscape, and makes the case for why example_product is uniquely positioned to win. The document will be used for exec reviews, board prep, and strategic planning.

## Output
Single markdown file: `product-development/product/strategy/vision/example_product-competitive-strategy-2026.md`

## Temp folder
Agents write to `product-development/product/strategy/vision/.tmp/` during execution. Assembly pass merges into the final file and deletes the temp folder.

```
vision/.tmp/
├── agent1-vision-problem.md
├── agent2-competitors.md
├── agent3-features-pricing.md
└── agent4-customer-research.md
```

## Source files

### Writing guide
- `.claude-user/skills/writing-guide-strategy/SKILL.md` — voice, argument construction, evidence toolkit, formatting

### Competitive research
- `product-development/product/competitive-research/competitors/competitive-matrix.md` — feature comparison across all 6 competitors
- `product-development/product/competitive-research/competitors/lovable/tldr.md`
- `product-development/product/competitive-research/competitors/google-stitch/tldr.md`
- `product-development/product/competitive-research/competitors/v0/tldr.md`
- `product-development/product/competitive-research/competitors/replit/tldr.md`
- `product-development/product/competitive-research/competitors/figma-make/tldr.md`
- `product-development/product/competitive-research/competitors/bolt/tldr.md`
- `product-development/product/competitive-research/competitors/*/pricing.md` — pricing per competitor

### Product context
- `product-development/product/CLAUDE.md` — five core pillars, terminology, product overview
- `product-development/product/strategy/vision/example_product-platform-vision.md` — existing vision doc
- `product-development/product/strategy/business-context/example_product-business-info.md` — business context and metrics
- `product-development/product/strategy/business-context/example_product-jtbd-and-users.md` — jobs to be done and personas

### Customer evidence
- `product-development/product/customers/accounts/*/account-context.md` — per-customer context
- `product-development/product/customers/accounts/*/calls/summaries/*.md` — call summaries with verbatims

### Feature inventory

## Steps

### Step 1: Build shared context briefing
Read the following files and prepare a context block that will be passed to all 3 agents:
- `product-development/product/CLAUDE.md` (pillars, modules, terminology)
- `product-development/product/competitive-research/CLAUDE.md` (competitor list, positioning, key takeaways)
- `product-development/product/competitive-research/competitors/competitive-matrix.md` (feature comparison)
- `product-development/product/strategy/business-context/example_product-business-info.md` (business metrics)

Condense into a briefing covering:
- What example_product is and its 5 pillars
- The 6 competitors and their positioning (1-2 sentences each)
- example_product's current state per pillar
- Key business metrics

### Step 2: Launch agents

**Dependency:** Agent 1 reads Agent 4's output for customer verbatims. Launch Agents 2, 3, and 4 in parallel first. Launch Agent 1 after Agent 4 completes.

```
Step 2a: Agents 2, 3, 4 in parallel
Step 2b: Agent 1 (after Agent 4 completes)
Step 3:  Assembly (after all agents complete)
```

#### Agent 1: Vision & Market Problem (Sections 1-3) [model: opus]

Prompt:

```
You are writing sections of a product vision and competitive strategy document for example_product, an AI prototyping platform.

WRITING GUIDE: Read `.claude-user/skills/writing-guide-strategy/SKILL.md` before writing anything. Follow the voice principles, argument construction pattern, and evidence toolkit exactly.

SHARED CONTEXT:
[Insert shared context briefing from Step 1]

SOURCE FILES TO READ:
- `product-development/product/strategy/vision/example_product-platform-vision.md` — existing vision
- `product-development/product/strategy/business-context/example_product-jtbd-and-users.md` — user personas and JTBD
- `product-development/product/strategy/vision/.tmp/agent4-customer-research.md` — customer research synthesis (from Agent 4, read after it completes)

WRITE THE FOLLOWING SECTIONS:

## Section 1: What's Broken in the Market Today

Organize around two themes:

**What's broken (5 structural failures):**
1. The stack is fragmented by design — AI prototyping tools cover one slice (frontend, or backend, or deployment) but none cover the full stack. Customers assemble 3-5 tools.
2. Prototype-to-production gap kills projects — most AI-generated code never ships. It's a demo, not an app. The export-to-IDE gap is where projects die.
3. Enterprise is locked out — no AI prototyping tool has SSO, audit logs, or compliance. Enterprise teams can't adopt.
4. Collaboration is an afterthought — most tools are single-player. Teams can't work together on generated projects.
5. Design quality vs engineering depth is a false tradeoff — tools are either beautiful but shallow (Lovable) or deep but ugly (Replit). Nobody does both.

**How this impacts customers (with verbatims):**
- Pull 2-3 real customer quotes from the call summaries
- Reference specific competitor limitations by name

## Section 2: Mission, Vision, and Why example_product Can Do Better

Three parts:
1. Mission/Vision/North Star — draft crisp, bold statements specific to example_product
2. Why example_product can do better — structural advantages (full-stack generation, one-click deploy, enterprise features, template marketplace)
3. The Five Pillars — brief overview referencing the pillar definitions from product/CLAUDE.md

## Section 3: Executive Summary

Write LAST (after reading Sections 4-8 from the other agents' output). Standalone 1-pager with:
- 2-sentence product thesis
- Pillar grid with status
- Competitive moat summary
- Key metrics
- Strategic kicker

OUTPUT: Write to `product-development/product/strategy/vision/.tmp/agent1-vision-problem.md`
```

#### Agent 2: Competitor Deep Dives & Module Analysis (Sections 4-5) [model: opus]

Prompt:

```
You are writing sections of a product vision and competitive strategy document for example_product, an AI prototyping platform.

WRITING GUIDE: Read `.claude-user/skills/writing-guide-strategy/SKILL.md` before writing anything. Follow the voice principles, argument construction pattern, and evidence toolkit exactly.

SHARED CONTEXT:
[Insert shared context briefing from Step 1]

SOURCE FILES TO READ:
- `product-development/product/competitive-research/competitors/competitive-matrix.md` — full feature matrix
- `product-development/product/competitive-research/competitors/lovable/tldr.md`
- `product-development/product/competitive-research/competitors/lovable/pricing.md`
- `product-development/product/competitive-research/competitors/google-stitch/tldr.md`
- `product-development/product/competitive-research/competitors/google-stitch/pricing.md`
- `product-development/product/competitive-research/competitors/v0/tldr.md`
- `product-development/product/competitive-research/competitors/v0/pricing.md`
- `product-development/product/competitive-research/competitors/replit/tldr.md`
- `product-development/product/competitive-research/competitors/replit/pricing.md`
- `product-development/product/competitive-research/competitors/bolt/tldr.md`
- `product-development/product/competitive-research/competitors/bolt/pricing.md`
- `product-development/product/competitive-research/competitors/figma-make/tldr.md`
- `product-development/product/competitive-research/competitors/figma-make/pricing.md`

WRITE THE FOLLOWING SECTIONS:

## Section 4: Competitive Landscape Matrix

Build a matrix with:
- Rows: example_product + all 6 competitors
- Columns: the 5 pillars (Generation Quality, Developer Experience, Deployment, Collaboration, Enterprise) + a "Pillar Count" column
- Cells: Full / Partial / None (pulled from competitive-matrix.md)
- Key insight line: "No single competitor covers all 5 pillars."

## Section 5: Competitor Deep Dives

For each of the 6 competitors, use this exact structure:

### [Competitor Name]

**How they position themselves:** [From their tldr.md]

**Key strengths:**
- [From their tldr.md]

**Key weaknesses:**
- [From their tldr.md]

**Pricing:** [From their pricing.md]

**Why example_product wins against them:**
- [Structural advantages — not features we've shipped, but why we'll be better once built]

OUTPUT: Write to `product-development/product/strategy/vision/.tmp/agent2-competitors.md`
```

#### Agent 3: Feature Analysis & Pricing (Sections 6-8) [model: opus]

Prompt:

```
You are writing sections of a product vision and competitive strategy document for example_product, an AI prototyping platform.

WRITING GUIDE: Read `.claude-user/skills/writing-guide-strategy/SKILL.md` before writing anything. Follow the voice principles, argument construction pattern, and evidence toolkit exactly.

SHARED CONTEXT:
[Insert shared context briefing from Step 1]

SOURCE FILES TO READ:
- `product-development/product/competitive-research/competitors/competitive-matrix.md` — full feature matrix
- `product-development/product/competitive-research/competitors/*/pricing.md` — all competitor pricing

WRITE THE FOLLOWING SECTIONS:

## Section 6: example_product vs Competitors Per Pillar

One comparison table per pillar (5 tables). For each table:
- Rows: key features in that pillar
- Columns: example_product + 3-4 most relevant competitors for that pillar
- After each table, include:
  1. Summary: "example_product covers X of Y features. Key gaps: [specific gaps]."
  2. Honest assessment: 1-2 sentences
  3. "Why example_product wins" callout with structural advantages

## Section 7: Head-to-Head Investment Roadmap

For each major competitor (Lovable, Google Stitch, Replit, Bolt):

### Beating [Competitor]
**Their core strength:** [1 sentence]
**Where they sell:** [Segment + buyer persona]
**What we have today that they don't:** [Specific features]
**What we need to reach parity:** [Specific features from competitive matrix]
**What we need to win (beyond parity):** [Structural advantages]

## Section 8: Competitor Pricing Comparison

Table with columns: Competitor, Starting Price, Model (per-seat/usage/flat), Free Tier, Enterprise Pricing
- Note which prices are confirmed vs estimated
- Include a "customer savings" comparison: buying 3-4 separate tools vs example_product

OUTPUT: Write to `product-development/product/strategy/vision/.tmp/agent3-features-pricing.md`
```

#### Agent 4: Customer Research Synthesis (Section 9) [model: opus]

Prompt:

```
You are writing a customer research synthesis section for a product vision and competitive strategy document for example_product, an AI prototyping platform.

WRITING GUIDE: Read `.claude-user/skills/writing-guide-strategy/SKILL.md` before writing anything. Follow the voice principles, argument construction pattern, and evidence toolkit exactly.

SHARED CONTEXT:
[Insert shared context briefing from Step 1]

SOURCE FILES TO READ:
- `product-development/product/customers/CLAUDE.md` — customer segments and account routing
- `product-development/product/customers/accounts/acme-corp/account-context.md`
- `product-development/product/customers/accounts/meridian-health/account-context.md`
- `product-development/product/customers/accounts/crestview-financial/account-context.md`
- `product-development/product/customers/accounts/stackline/account-context.md`
- `product-development/product/customers/accounts/axiom-logistics/account-context.md`
- `product-development/product/customers/accounts/helix-robotics/account-context.md`
- `product-development/product/customers/accounts/volta-energy/account-context.md`
- `product-development/product/customers/accounts/novabridge/account-context.md`
- `product-development/product/customers/accounts/pinnacle-media/account-context.md`
- `product-development/product/customers/accounts/*/calls/summaries/*.md` — all call summaries

WRITE THE FOLLOWING SECTION:

## Section 9: What Customers and Research Are Telling Us

Synthesize across all customer accounts and call summaries to surface:

**Common themes:**
- What are customers consistently asking for? Group requests into themes (e.g. "enterprise security," "deployment flexibility," "design quality").
- What pain points come up repeatedly across different accounts?

**Segment patterns:**
- How do Enterprise customer needs differ from Growth customer needs?
- What's blocking expansion in each segment?

**Key verbatims:**
- Pull the strongest 4-6 direct quotes from call summaries that illustrate the themes above
- Attribute each with name, title, and company
- Use pull-quote table format for the most compelling ones

**Feature demand signals:**
- Which features from the competitive matrix are customers explicitly requesting?
- Map customer requests to specific competitors they're comparing us to (e.g. "Stackline wants API access — evaluating Replit as alternative")

**Risk signals:**
- Which accounts have churn risk and why?
- What competitive threats are customers mentioning?

This section should give leadership a clear picture of what the market is telling us, grounded in specific customer evidence rather than assumptions.

OUTPUT: Write to `product-development/product/strategy/vision/.tmp/agent4-customer-research.md`
```

### Step 3: Assembly

After all 4 agents complete, the orchestrating agent:
1. Reads all 4 files from `product-development/product/strategy/vision/.tmp/`
2. Merges into `product-development/product/strategy/vision/example_product-competitive-strategy-2026.md` with proper section numbering
3. Writes Section 3 (Executive Summary) — the orchestrator has the full document in context, so it can distill the 1-pager
4. Inserts exec summary at the top
5. Deletes `.tmp/` folder

### Step 4: Verification

- All 6 competitors appear in the landscape matrix
- Pricing data matches source files
- Customer quotes are attributed with name and company
- Exec summary stands alone without referencing other sections
- Voice matches the writing guide (no hedging, specific numbers, active voice)
- Read end-to-end for narrative flow
