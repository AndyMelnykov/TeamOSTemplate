# Step 2: Customer Call Synthesis

## Goal

Produce the "Customer Calls" section with a customer overview table, thematic analysis ("What We're Hearing"), and key insights ("Highlights").

---

## Automated Part

### 1. Find recent call summaries

Scan `product/customers/calls/summaries/` for files modified in the last 2 weeks. Read each one.

### 2. Categorize customers

For each customer with a recent call, determine their category:
- **Paying customer** - signed and paying for example_product
- **Pilot** - active pilot, not yet paying
- **Pipeline** - in pipeline, being pitched
- **Free tier** - on free plan, potential upsell

Cross-reference `product/customers/example_product-customer-overview.md` if unsure about customer status.

### 3. Extract from each call

For each call summary, extract:
- **Date** of the call
- **One-line takeaway** (most important thing from the call)
- **Key quotes** (verbatim, with speaker attribution)
- **Product satisfaction signals** (positive or negative)
- **Product feedback / feature requests**
- **Workflow themes** (generation quality, deployment pain, collaboration needs, enterprise requirements)

### 4. Draft sections

Generate three sections:

**Customer Overview Table:**

| Customer | Date | Category | Takeaway |
|---|---|---|---|
| [Name] | MM/DD | [Category] | [One-line takeaway] |

**What We're Hearing:**
- Product satisfaction paragraph with supporting quotes
- Thematic analysis paragraph (identify patterns across customers)
  - Look for: workflow themes, buyer persona patterns, feature gap patterns

**Highlights:**
- Numbered list of 5-8 key insights
- Each insight: bold headline + one sentence of context
- Include customer name and specific evidence

---

## Interactive Part

### 5. Present customer overview table

Show the table and ask: **"Any calls missing? Any context to add?"**

The PM may flag calls that happened but weren't summarized, or provide additional context about a customer's status.

### 6. Present thematic analysis draft

Show "What We're Hearing" and "Highlights" for review. The PM will refine framing, correct any mischaracterizations, and add insights the data didn't surface.

### 7. Write to output file

Write the section to the dated output file immediately after approval. Don't wait for Steps 3-5.

---

## Output Format

```markdown
# Customer Calls: [Start Date] - [End Date]

| Customer | Date | Category | Takeaway |
|---|---|---|---|
| [Name] | MM/DD | [Category] | [One-line takeaway] |

## What We're Hearing

**[Theme 1 headline.]** [Supporting paragraph with quotes.]
- [Sub-theme]: [Detail with customer examples]
- [Sub-theme]: [Detail with customer examples]

**[Theme 2 headline.]** [Supporting paragraph.]
- [Sub-theme]: [Detail]

## Highlights

1. **[Bold headline.]** [One sentence with customer name and evidence.]
2. **[Bold headline.]** [One sentence.]
...
```

---

## Notes

- The customer table is ordered chronologically by call date (earliest first).
- "What We're Hearing" should identify patterns across customers, not just summarize each call individually.
- "Highlights" are the most important insights for leadership. They should be actionable or strategic, not just interesting facts.
- If fewer than 3 calls happened in the last 2 weeks, note this and ask the PM if they want to expand the date range.
