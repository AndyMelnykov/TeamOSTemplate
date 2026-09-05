# OPP-EXTRACT-001: Users can't tell whether extracted data is trustworthy enough to publish

## Problem

Non-technical ops/legal users have no way to judge whether AI-extracted fields are accurate enough to route into a live workflow. They either over-trust the output — and ship errors downstream — or manually re-check everything, losing the time automation was supposed to save.

## Who experiences it

- Ops and legal admins running document workflows without an engineering background
- Teams moving from a manual pilot to production volume (see `INS-001`, `INS-004`)

## Evidence

- `INS-002` — trust/security is the top named concern for non-technical users evaluating extraction output
- `INS-003` — users ask whether extraction is "good enough", not how OCR works internally

## Why it matters

Low trust in extraction output blocks the exact production-readiness transition Pillar 1 (Extraction Quality) is supposed to enable — see [`product/CLAUDE.md`](../../CLAUDE.md)'s Five Core Pillars table, which already lists "extraction confidence scoring" as a P0 feature with no PRD behind it yet.

## Success signal

Users can look at any extracted field and get a plain-language confidence read ("high confidence" / "needs review" / "not ready to publish") with a concrete reason, without needing to understand OCR.

## Status

`validated`
