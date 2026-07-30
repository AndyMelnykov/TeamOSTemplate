---
name: customer-call-summary
description: Customer Call Transcript Processing
---

# Customer Call Summary Style Guide

This skill defines how to summarize customer call transcripts for product management insights.

**For the expected level of detail, see the example:** [examples/acme-01-27-26.md](examples/acme-01-27-26.md)

## Summary Structure

Every customer call summary should include these sections in order:

### 1. Executive Summary

A detailed overview that orients the reader and captures the key takeaways. Structure:

**Quotes:** Always weave relevant verbatim quotes directly into the executive summary paragraphs. Quotes bring the exec summary to life - this is the most-read section. Use italicized quotes inline within paragraphs (e.g., *"We are digging it." - Derek*), not just in insight tables.

**Opening paragraph:** Status updates and any quick wins/progress since last meeting

**Second paragraph:** "This call focused on X areas: (1) [topic], and (2) [topic]." - orient the reader on what's covered

**Topic sections:** For each major topic discussed, add a bold header and detailed paragraph:
- `**[Topic Name]**` (e.g., "Templates for Batch Projects")
- Include specific context, decisions made, and any blockers

**How [Customer] is Using [Specific Feature/Workflow]:** Scope this heading to the specific features or workflows discussed on *this* call - not a comprehensive overview of all product usage. Example: "How Acme is Using Templates & Generation Deflection" not "How Acme is Using example_product Today." Only reflect what was discussed in the current meeting.

**Opportunity Areas:** Paragraph or numbered list describing opportunities identified. Tie back to their workflows.

**[Product Strategy/Hypothesis] Validation** (include when applicable): When a call provides evidence that validates or invalidates a product strategy or hypothesis, add a dedicated section with customer quotes as evidence. Example: "example_product's Upcoming Roadmap Validates User Expansion Strategy" with quotes showing customer enthusiasm and unprompted action (e.g., assigning internal owners before the feature ships). Also add a corresponding insight topic in the Insights/Learnings section with the detailed evidence and quotes.

**Key Product Gaps:** Bullet list of gaps with specific descriptions. Actively identify *implied* feature gaps - things the customer is working around, doing manually, or switching to another tool for. Don't just capture features they explicitly request; listen for pain points that imply a missing capability (e.g., "Derek manually exports generated code and re-imports it into their CI pipeline" implies example_product needs direct CI/CD integration).
```markdown
**Key Product Gaps**
- **[Gap 1]:** [Specific description with context]
- **[Gap 2]:** [Specific description with context]
```

### 2. Insights / Learnings

Organize insights by topic. Each topic section includes:

**Topic heading (H3):** Group related insights together
```markdown
### [Topic Name]
```

**Summary:** 1-2 sentence summary of what we learned in this topic area

**Table format:** Use tables with detailed descriptions and quotes on separate lines:
```markdown
| Insight | Details |
|---------|---------|
| **[Insight headline]** | [Detailed description with specific examples from the call]<br><br>*"[Verbatim quote]" - [Speaker]* |
```

**Level of detail:** Include enough context that someone who wasn't on the call understands:
- The "why" behind the insight, not just the "what"
- Specific examples mentioned (e.g., "Acme batch project compliance")
- Multiple quotes if they add different perspectives

### 3. Feature Requests

Organize feature requests by area. Each area section includes:

**Area heading (H3):** Group related features together
```markdown
### [Area Name] (e.g., "Data Export & Sharing", "Filtering & Search")
```

**Summary:** Description of this feature area and the underlying need

**Blockers (if applicable):**
```markdown
**Blocker:** [Description of what's blocking progress and any dependencies]
```

**Table format:**
```markdown
| Feature | Details |
|---------|---------|
| **[Feature name]** | [Detailed description]<br><br>*"[Verbatim quote]" - [Speaker]* |
```

### 4. Next Steps

Organize action items by category:
```markdown
## Next Steps

### [Category] (e.g., "Onboarding", "Template Configuration")
- [Action item] - [Owner]
- [Action item] - [Owner]

### [Next Category]
- [Action item] - [Owner]
```

### 5. Follow-up Email

Draft a follow-up email to send to the customer contact:
```markdown
## Follow-up Email

**To:** [Customer contact]
**Subject:** [Meeting Topic] Recap + Action Items

Hi [Name],

Thanks for the great discussion today! Here's a quick recap:

**What we covered:**
- [Key topic 1]
- [Key topic 2]
- [Key topic 3]

**Action items for you:**
- [ ] [Item 1]
- [ ] [Item 2]

**From our side:**
- [Item 1]
- [Item 2]

Let me know if I missed anything!

Best,
Hannah
```

### 6. Slack Summary

Draft a ready-to-post Slack message summarizing the call for internal stakeholders.

**Format:**
- Opening line: "Great [frequency] sync with [Customer] today! Full recap here: [link]"
- Bold topic headers for each major area discussed
- Detailed paragraphs covering each major topic with inline customer quotes
- Numbered lists for specific fixes or action items
- End with "Linear issues to come for all items raised above." when applicable

**Content guidelines:**
- Hit ALL key takeaways - be specific (e.g., list all 5 fixes, not "a couple of fixes")
- Include customer quotes that capture enthusiasm, frustration, or key feedback
- Include metrics or data points discussed
- Note when the customer is already taking action (e.g., assigning internal owners)

**Example:**

```
Great bi-weekly sync with Acme today! Full recap here.

Project Templates
Shared templates are off to a strong start - 91 projects created from templates
since launch. Derek gave a shoutout to the team: "We are digging it. It's off
to a great start and it's something that we've been looking forward to having
for so long." Acme flagged several issues, and we broke them down in sprint
planning into five template fast follows assigned to Sam and Jordan this week:

1. Fix template versioning when a template is updated after projects were
   already created from it (currently orphans the old projects)
2. Update template metadata display - currently shows "generated by example_product"
   which is misleading for hand-customized templates
3. Add a "failed generations" tab so teams can see which template configs
   are producing low-quality output and why
4. Add project detail link-outs and environment indicators (dev/staging/prod,
   example_product Teams vs. example_product Pro) to generated project cards
5. Add a "view deployment" button on generated projects so Acme can check
   deploy status without leaving example_product

Derek also noted they're already seeing early positive signals even before
the CI/CD integration is deployed: "There's been a noticeable decrease in the
time from idea to working prototype. And a slight increase in the number of
projects that actually make it to production. So I think example_product is sort of
working. It's just not producing the volume that we need."

Based on our initial data, we're seeing a healthy 40% template-to-deploy
conversion rate, which we think is the floor. Biggest bottleneck to delivering
greater value is template coverage across their tech stack, which reinforces
the React/Vue/Svelte template library and CI/CD integration as P0.

CI/CD integration is still WIP with Acme's setup - once deployed, we expect
a material increase in production deploys since a significant portion of their
projects require automated testing before launch. We also discussed adding
templates for all tiers (including example_product Teams) as an additional lever, which
has been successful with other customers. Derek wants to discuss this further
next meeting in coordination with their internal tooling standardization efforts.

Access Controls, Team Workspaces, and Usage Analytics
Access Controls, Team Workspaces, and Usage Analytics will be a major value unlock for Acme.
Derek's reaction to the access permissions preview was immediate and
enthusiastic - he didn't just want manager access, he wants a structured weekly
review process built around example_product. He's already assigned Priya and Tom
to develop an internal rollout plan before the feature even ships. This validates
our hypothesis that Access Controls and Team Workspaces will expand example_product's user base within
accounts and shift it from an individual prototyping tool to a team-wide dev platform.

"You had me at hello, Hannah. You had me at hello. So, yes, we definitely want
to look at this so that managers we can think about. Not just access, Hannah. What
would really be helpful would be like if you guys created some sort of process
where our engineering leads had to sign in once a week and review their team's
projects and click complete and then Priya gets a notification that they
completed their review." - Derek

Deployment Visibility Within example_product
Priya also flagged the need to surface deployment status within example_product so they
don't have to go to the AWS console to check if a project is already live before
spinning up a new environment - "There is a high chance that if it's a project
deployed through example_product Teams, it's already running on our infrastructure. So we're
not spinning up duplicate instances." We'll solve this by bringing the Deployment
Dashboard into example_product (long-standing ask across multiple example_product customers).

Linear issues to come for all items raised above.
```

## Action Item Management

Action items are tracked at the file level (top of the summary file), not per-meeting.

### File-Level Action Item Tables

At the top of each customer's summary file, maintain these tables:

```markdown
## Open Action Items

### example_product Labs
| Action Item | Owner | From Meeting |
|-------------|-------|--------------|

### [CustomerName]
| Action Item | Owner | From Meeting |
|-------------|-------|--------------|

## Completed Action Items

### example_product Labs
| Action Item | Owner | From Meeting | Completed |
|-------------|-------|--------------|-----------|

### [CustomerName]
| Action Item | Owner | From Meeting | Completed |
|-------------|-------|--------------|-----------|
```

### Each Meeting: Update the Tables

1. **Review existing Open Action Items** against what was discussed in the meeting
2. **Ask user about unclear status** - if an item's status wasn't mentioned, ask: "Was [action item] completed?"
3. **Move completed items** to the Completed table with completion date
4. **Add new action items** from this meeting to the Open tables

## Verbatim Guidelines

1. **Always italicize** with speaker attribution: *"Quote text" - Speaker*
2. **Put quotes on separate lines** using `<br><br>` before the quote in table cells
3. **Choose quotes that are:**
   - Specific and actionable
   - Particularly revealing of customer needs
   - Supporting evidence for key insights
4. **Keep quotes concise** - trim to the essential part if needed
5. **Preserve exact wording** - don't paraphrase within quotes
6. **Include multiple quotes** when they add different perspectives

## Level of Detail

The summary should be detailed enough that someone who wasn't on the call understands the full picture:

- **Include specific examples** from the call (e.g., "Acme's internal tooling migration", "Beta Corp's client prototype workflow")
- **Capture the "why"** behind insights, not just the "what"
- **Use real examples** mentioned by the customer
- **Provide context** for feature requests (what problem they solve, who needs them)
- **Note blockers and dependencies** that affect next steps

**See the example for the expected level of detail:** [examples/acme-01-27-26.md](examples/acme-01-27-26.md)

## Quality Checklist

Before finalizing the summary, verify:

- [ ] Executive Summary has opening status paragraph + topic focus paragraph
- [ ] Executive Summary includes bold topic headers with detailed paragraphs
- [ ] Executive Summary includes relevant verbatim quotes woven into paragraphs
- [ ] Feature/workflow headings are scoped to this call (not "How [Customer] is Using [Product] Today")
- [ ] "Opportunity Areas" ties opportunities back to their current workflows
- [ ] "Key Product Gaps" has specific descriptions with context
- [ ] Implicit feature gaps identified (not just explicit requests)
- [ ] Hypothesis/strategy validation section included where call provides evidence
- [ ] Insights are organized by topic with Summary paragraphs
- [ ] Insights use table format with quotes on separate lines (`<br><br>`)
- [ ] Feature Requests are organized by area with Summary paragraphs
- [ ] Blockers are noted where applicable
- [ ] Next Steps are organized by category
- [ ] Follow-up Email is drafted with recap and checkbox action items
- [ ] Slack summary drafted
- [ ] Action item tables at file top are updated (completed moved, new added)
- [ ] Feature requests cross-referenced with `feature-requests/feature-requests.md`
- [ ] New requests added to tracker with GitHub links and context
- [ ] Level of detail matches the Acme example
