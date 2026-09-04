# example_product Platform Overview

High-level architecture and system overview for the example_product platform.

# What example_product Does

example_product is an AI-powered platform that turns uploaded documents into automated workflows. Users upload a document (or drop in a template), example_product's AI extracts the structured data and routes it through approvals and signature, and with one click they can publish it as a live, branded portal.

# Core Systems

## AI Extraction Engine
The extraction engine is the core of example_product. It takes an uploaded document, processes it through a fine-tuned OCR + LLM pipeline, and produces structured, validated field and clause data.

- **Document processing:** Analyzes and enriches uploaded documents with context from prior workflow runs and selected templates
- **Field & clause extraction:** Multi-step extraction pipeline that identifies form fields, table data, and contract clauses across PDF, scanned image, and DOCX inputs
- **Quality checks:** Automated confidence scoring, validation-rule checks, and human-review flagging before presenting output to the user
- **Model versions:** Currently on `example_product-extract-3.2`, with model upgrades managed through a staged rollout process

## Publishing Pipeline
Handles packaging and publishing workflows as live, signer-facing portals.

- **Supported delivery channels:** Hosted portal links, embeddable forms, and example_product-managed infrastructure
- **One-Click Publish:** Streamlined flow that handles portal provisioning, branding, and DNS configuration automatically
- **Custom domains:** Users on Pro tier and above can connect their own domains
- **Preview environments:** Every workflow draft creates a temporary preview URL for testing before publish

## Collaboration Layer
Team features that enable multi-user workflows.

- **Team workspaces:** Shared workflows, role-based permissions (Owner, Editor, Viewer)
- **Shared clause/field block library:** Reusable extraction rules and clause blocks that team members can include in workflows
- **Version history:** Full history of workflow edits with diff view and rollback
- **Comments and feedback:** Inline commenting on workflow steps and extracted output

## Admin Console
Management and configuration for Teams and Enterprise customers.

- **User management:** Invite, remove, and manage team member roles
- **Billing:** Subscription management, usage tracking, invoices
- **SSO:** SAML and OIDC integration for Enterprise customers
- **Audit logs:** Activity logging for compliance (Enterprise only)
- **Usage analytics:** Team-level automation run volume, adoption metrics, cost tracking

# Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Tailwind CSS |
| Backend API | Node.js, Express, TypeScript |
| Extraction Pipeline | Python, OCR (custom-trained + Tesseract fallback), custom orchestration framework |
| Database | PostgreSQL (primary), Redis (caching) |
| Data Warehouse | Snowflake |
| Infrastructure | AWS (EKS, RDS, S3), Terraform |
| CI/CD | GitHub Actions |
| Monitoring | Datadog, PagerDuty |
| Analytics | Amplitude (product), Mode + Sigma (internal) |
