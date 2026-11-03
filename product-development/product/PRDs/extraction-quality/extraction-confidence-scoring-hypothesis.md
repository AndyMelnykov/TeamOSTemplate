# HYP-EXTRACT-001: Users can't tell whether extracted data is trustworthy enough to publish

If extracted fields show a plain-language confidence label (high confidence / needs review / not ready to publish) with a one-line reason, then non-technical users will correctly identify which fields need manual review before publishing, because they're currently guessing rather than being told.

## Problem

Non-technical ops/legal users have no way to judge whether AI-extracted fields are accurate enough to route into a live workflow. They either over-trust the output -- and ship errors downstream -- or manually re-check everything, losing the time automation was supposed to save.

Experienced by ops and legal admins running document workflows without an engineering background, and by teams moving from a manual pilot to production volume (see `INS-001`, `INS-004`).

## Signals

- `INS-002` -- trust/security is the top named concern for non-technical users evaluating extraction output
- `INS-003` -- users ask whether extraction is "good enough", not how OCR works internally

## Why it matters

Low trust in extraction output blocks the exact production-readiness transition Pillar 1 (Extraction Quality) is supposed to enable -- see [`product/CLAUDE.md`](../../CLAUDE.md)'s Five Core Pillars table, which already lists "extraction confidence scoring" as a P0 feature with no PRD behind it yet.

## Test

Prototype + usability study: show test users a workflow with mixed-confidence extracted fields and ask them to identify which fields they'd manually check before publishing.

## Success criteria

- 70%+ of test users correctly flag the deliberately-low-confidence fields
- 0 high-confidence fields flagged as needing review (false positives undermine trust in the label itself)

## Status

`proposed`

## Result

`pending`
