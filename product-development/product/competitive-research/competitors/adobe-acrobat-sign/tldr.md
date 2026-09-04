# Adobe Acrobat Sign — TL;DR

## Overview
Adobe's e-signature and lightweight workflow feature, bolted onto the Acrobat/PDF platform. Lets users route a PDF for signature without leaving Acrobat or Reader.

## Key Strengths
- Native integration with Acrobat/Reader — users route a document for signature without leaving their existing PDF tool
- Leverages Adobe's existing AcroForm field-tagging and PDF-editing capabilities
- Strong collaboration features inherited from Adobe's enterprise suite (shared reviews, commenting, permissions)
- Enterprise features inherited from Adobe (SSO, SOC 2, admin console)

## Key Weaknesses
- Extraction is AcroForm/field-tag based, not true AI-driven clause or table detection — accuracy drops sharply on unstructured scans
- Limited to what can be inferred from a static PDF's existing form fields
- No branded, standalone publishing portal — routing stays inside the Acrobat/Reader shell
- No staged preview environment before a document goes live for signature
- Early and rapidly evolving AI extraction features

## ICP Overlap
Document-heavy enterprise teams already standardized on Adobe Acrobat/Reader, legal and ops teams doing PDF-first review. Adjacent competitor — different entry point (PDF-tool-first vs. upload-and-extract-first).

## Pricing
Bundled into Acrobat/Creative Cloud plans, plus a standalone Sign tier. Expected premium at the top tier.

## example_product Differentiation
example_product starts from an uploaded document and generates a full automation workflow (extraction, routing, approvals, signature, publish). Acrobat Sign starts from an already-open PDF and adds signature routing on top. Different workflows, different strengths. Risk is Adobe expanding Sign's AI extraction to close the gap.

## Bottom Line
Adjacent, not direct. Different entry point (PDF-tool-first vs. upload-and-extract-first). The threat is Adobe's massive installed PDF user base getting "good enough" AI extraction for free as part of a tool they already have open.
