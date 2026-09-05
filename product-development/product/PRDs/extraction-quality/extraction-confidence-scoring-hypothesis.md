# HYP-EXTRACT-001

If extracted fields show a plain-language confidence label (high confidence / needs review / not ready to publish) with a one-line reason, then non-technical users will correctly identify which fields need manual review before publishing, because they're currently guessing rather than being told.

## Opportunity

OPP-EXTRACT-001

## Supporting evidence

- `INS-002`
- `INS-003`

## Test

Prototype + usability study: show test users a workflow with mixed-confidence extracted fields and ask them to identify which fields they'd manually check before publishing.

## Success criteria

- 70%+ of test users correctly flag the deliberately-low-confidence fields
- 0 high-confidence fields flagged as needing review (false positives undermine trust in the label itself)

## Result

`pending`
