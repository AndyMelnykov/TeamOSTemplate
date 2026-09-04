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
| `pandadoc/` | Website audit | Fast document/proposal builder with e-signature | Direct competitor - closest feature overlap |
| `conga/` | Website audit | Enterprise document automation, deep integration with Salesforce | Direct competitor (enterprise) |
| `dropbox-sign/` | Website audit | Lightweight e-signature, narrow but fast | Direct competitor - strong in signature UX |
| `ironclad/` | Website audit | Contract lifecycle management platform with built-in workflow | Direct competitor - broader scope (full lifecycle) |
| `adobe-acrobat-sign/` | Website audit | Adobe's signature/workflow feature bolted onto Acrobat/PDF | Adjacent - PDF-tool-first approach, different entry point |
| `docusign/` | Website audit | Full-stack document workflow + signature (docusign.com) | Direct competitor - brand-recognition-focused |

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
| **Extraction Quality** | Format support, OCR/field extraction accuracy, error handling, multi-page output |
| **Workflow Building Experience** | Builder UX, preview speed, refinement flow, instruction interface |
| **Publishing** | Hosting options, custom domains, environment variables, CI/CD |
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
