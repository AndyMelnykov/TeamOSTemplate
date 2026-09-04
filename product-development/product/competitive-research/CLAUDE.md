# Competitive Research

Competitive intelligence for example_product — tracking competitors, feature comparisons, and market positioning.

## Competitors

| Competitor | Website | Focus | Segment | Teardown |
|-----------|---------|-------|---------|----------|
| PandaDoc | pandadoc.com | Fast document/proposal builder, design-focused | SMB-Mid | [competitors/pandadoc/](competitors/pandadoc/CLAUDE.md) |
| Conga | conga.com | Enterprise document automation, deep Salesforce ecosystem lock-in | Mid-Enterprise | [competitors/conga/](competitors/conga/CLAUDE.md) |
| Dropbox Sign | sign.dropbox.com | Lightweight e-signature, narrow but fast | SMB-Mid | [competitors/dropbox-sign/](competitors/dropbox-sign/CLAUDE.md) |
| Ironclad | ironcladapp.com | Broad contract lifecycle management platform | SMB-Mid | [competitors/ironclad/](competitors/ironclad/CLAUDE.md) |
| Adobe Acrobat Sign | acrobat.adobe.com/sign | Signature/workflow bolted onto the Acrobat/PDF platform | Mid-Enterprise | [competitors/adobe-acrobat-sign/](competitors/adobe-acrobat-sign/CLAUDE.md) |
| DocuSign | docusign.com | Full-stack document workflow + signature, speed/brand-recognition-focused | SMB-Mid | [competitors/docusign/](competitors/docusign/CLAUDE.md) |

## Doc Index

| File | What's in it | When to read |
|------|-------------|--------------|
| `competitors/competitive-matrix.md` | Feature comparison matrix across all competitors | Quick feature lookup, roadmap prioritization |
| `competitors/{competitor}/tldr.md` | Per-competitor summary (strengths, weaknesses, differentiation) | Understanding a specific competitor |
| `competitors/{competitor}/pricing.md` | Pricing model, tiers, and comparison to example_product | Pricing analysis for a specific competitor |

## example_product Competitive Positioning

| Dimension | example_product Advantage |
|-----------|-----------------|
| **Extraction accuracy** | Only platform combining high-accuracy OCR/field extraction with a no-code workflow builder |
| **Full-stack** | Extraction + routing + approvals + e-signature + publishing in one flow |
| **Customization** | Deep control over extraction rules, routing logic, and branding |
| **Enterprise features** | SSO, audit logging, team workspaces, compliance controls |
| **Refinement speed** | Modify and republish a workflow without rebuilding it from scratch |

## Key Takeaways

1. **No single competitor covers the full stack well.** PandaDoc, Dropbox Sign, and DocuSign are signature/proposal-heavy; Ironclad is full-lifecycle but extraction-weak; Conga is ecosystem-locked; Adobe Acrobat Sign is PDF-tool-bound.
2. **Extraction accuracy is our moat.** Most competitors treat documents as static files to sign, not data to extract. example_product extracts structured data first.
3. **Enterprise is underserved.** Only Conga has enterprise credibility, but their product is Salesforce-locked. This is our biggest opportunity.
4. **Signature UX is table stakes.** DocuSign and PandaDoc set a high bar. We must match their signing experience while delivering superior extraction.

## When to Update

- After competitive deal wins/losses
- When competitors launch new features
- After sales calls where competitors are mentioned
- Quarterly review of pricing and positioning
- After each website audit (update `competitors/competitive-matrix.md`)
