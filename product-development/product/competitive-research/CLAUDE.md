# Competitive Research

Competitive intelligence for example_product — tracking competitors, feature comparisons, and market positioning.

## Competitors

| Competitor | Website | Focus | Segment | Teardown |
|-----------|---------|-------|---------|----------|
| Lovable | lovable.dev | Full-stack AI app builder, design-focused | SMB-Mid | [competitors/lovable/](competitors/lovable/CLAUDE.md) |
| Google Stitch | stitch.withgoogle.com | AI prototyping, Google Cloud ecosystem | Mid-Enterprise | [competitors/google-stitch/](competitors/google-stitch/CLAUDE.md) |
| v0 | v0.dev | AI UI generation, Vercel/React ecosystem | SMB-Mid | [competitors/v0/](competitors/v0/CLAUDE.md) |
| Replit | replit.com | AI cloud IDE + deployment | SMB-Mid | [competitors/replit/](competitors/replit/CLAUDE.md) |
| Figma Make | figma.com/make | Design-to-code AI | Mid-Enterprise | [competitors/figma-make/](competitors/figma-make/CLAUDE.md) |
| Bolt | bolt.new | Full-stack AI app builder, speed-focused | SMB-Mid | [competitors/bolt/](competitors/bolt/CLAUDE.md) |

## Doc Index

| File | What's in it | When to read |
|------|-------------|--------------|
| `competitors/competitive-matrix.md` | Feature comparison matrix across all competitors | Quick feature lookup, roadmap prioritization |
| `competitors/{competitor}/tldr.md` | Per-competitor summary (strengths, weaknesses, differentiation) | Understanding a specific competitor |
| `competitors/{competitor}/pricing.md` | Pricing model, tiers, and comparison to example_product | Pricing analysis for a specific competitor |

## example_product Competitive Positioning

| Dimension | example_product Advantage |
|-----------|-----------------|
| **Production-readiness** | Only platform generating deploy-ready, enterprise-grade apps |
| **Full-stack** | Frontend + backend + database + auth + deployment in one flow |
| **Customization** | Deep control over architecture, patterns, and tech stack choices |
| **Enterprise features** | SSO, audit logging, team workspaces, compliance controls |
| **Iteration speed** | Modify and redeploy without regenerating from scratch |

## Key Takeaways

1. **No single competitor covers the full stack well.** Lovable, v0, and Bolt are frontend-heavy; Replit is full-stack but design-weak; Google Stitch is ecosystem-locked; Figma Make is design-tool-bound.
2. **Production-readiness is our moat.** Most competitors generate prototypes. example_product generates production apps.
3. **Enterprise is underserved.** Only Google Stitch has enterprise credibility, but their product is early. This is our biggest opportunity.
4. **Design quality is table stakes.** Lovable and v0 set a high bar. We must match their visual quality while delivering superior architecture.

## When to Update

- After competitive deal wins/losses
- When competitors launch new features
- After sales calls where competitors are mentioned
- Quarterly review of pricing and positioning
- After each website audit (update `competitors/competitive-matrix.md`)
