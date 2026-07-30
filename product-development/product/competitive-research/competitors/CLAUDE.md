# Competitors

Per-competitor research profiles and website audits for example_product competitors.

---

## Doc Index

| File | Description |
|------|-------------|
| `competitive-matrix.md` | Standardized feature comparison across all audited competitors |
| `plans/website-audit-plan.md` | Audit methodology, checklist, and standard folder structure |

---

## Competitor Index

| Folder | Type | Focus | example_product Relevance |
|--------|------|-------|-----------------|
| `lovable/` | Website audit | Full-stack AI app builder with instant deployment | Direct competitor - closest feature overlap |
| `google-stitch/` | Website audit | Google's AI prototyping tool, deep integration with Google Cloud | Direct competitor (enterprise) |
| `v0/` | Website audit | Vercel's AI UI generation, React/Next.js focused | Direct competitor - strong in frontend generation |
| `replit/` | Website audit | AI-powered cloud IDE with built-in hosting | Direct competitor - broader scope (full IDE) |
| `figma-make/` | Website audit | Figma's design-to-code AI feature | Adjacent - design-first approach, different entry point |
| `bolt/` | Website audit | Full-stack AI app builder (bolt.new) | Direct competitor - speed-focused prompt-to-app |

---

## Folder Conventions

Each `{competitor}/` folder follows a standard structure:

```
{competitor}/
├── CLAUDE.md       # Doc index + brief competitor context
├── tldr.md         # Executive summary (start here)
├── pricing.md      # Pricing model and tiers
└── images/         # Pricing screenshots
```

---

## Audit Dimensions

When auditing a competitor, evaluate across these dimensions:

| Dimension | What to Capture |
|-----------|-----------------|
| **Generation Quality** | Framework support, code quality, error handling, multi-file output |
| **Developer Experience** | Editor UX, preview speed, iteration flow, prompt interface |
| **Deployment** | Hosting options, custom domains, environment variables, CI/CD |
| **Collaboration** | Sharing, team features, permissions, commenting |
| **Pricing** | Free tier limits, paid tiers, enterprise pricing, usage-based components |
| **Templates** | Library size, categories, customization depth, community contributions |
| **Enterprise** | SSO, audit logs, admin controls, SLAs, compliance |
| **Ecosystem** | Integrations, plugins, API access, import/export |

---

## How to Use

- **Quick competitive read:** Start with `tldr.md` in any competitor folder
- **Feature comparisons:** Use `competitive-matrix.md`
- **Pricing deep dive:** Read the competitor's `pricing.md`
- **After new audits:** Update `competitive-matrix.md` and `../CLAUDE.md`
