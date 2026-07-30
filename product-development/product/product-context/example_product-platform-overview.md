# example_product Platform Overview

High-level architecture and system overview for the example_product platform.

# What example_product Does

example_product is an AI-powered platform that turns natural language prompts into deployable web applications. Users describe what they want to build, example_product generates the code, and with one click they can deploy it to a live URL.

# Core Systems

## AI Generation Engine
The generation engine is the core of example_product. It takes a user's natural language prompt, processes it through a fine-tuned LLM pipeline, and produces a complete, working web application.

- **Prompt processing:** Analyzes and enriches user prompts with context from their project history and selected templates
- **Code generation:** Multi-step generation pipeline that produces frontend (React), backend (Node.js/Python), and infrastructure configuration
- **Quality checks:** Automated linting, build verification, and visual regression checks before presenting output to the user
- **Model versions:** Currently on `example_product-gen-3.2`, with model upgrades managed through a staged rollout process

## Deployment Pipeline
Handles packaging and deploying generated applications to hosting providers.

- **Supported providers:** Vercel, Netlify, and example_product-managed infrastructure
- **One-Click Deploy:** Streamlined flow that handles build, environment setup, and DNS configuration automatically
- **Custom domains:** Users on Pro tier and above can connect their own domains
- **Preview deploys:** Every generation creates a temporary preview URL for testing

## Collaboration Layer
Team features that enable multi-user workflows.

- **Team workspaces:** Shared projects, role-based permissions (Owner, Editor, Viewer)
- **Shared component library:** Reusable components that team members can include in generations
- **Version history:** Full history of generations with diff view and rollback
- **Comments and feedback:** Inline commenting on generated outputs

## Admin Console
Management and configuration for Teams and Enterprise customers.

- **User management:** Invite, remove, and manage team member roles
- **Billing:** Subscription management, usage tracking, invoices
- **SSO:** SAML and OIDC integration for Enterprise customers
- **Audit logs:** Activity logging for compliance (Enterprise only)
- **Usage analytics:** Team-level generation volume, adoption metrics, cost tracking

# Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Tailwind CSS |
| Backend API | Node.js, Express, TypeScript |
| AI Pipeline | Python, custom orchestration framework |
| Database | PostgreSQL (primary), Redis (caching) |
| Data Warehouse | Snowflake |
| Infrastructure | AWS (EKS, RDS, S3), Terraform |
| CI/CD | GitHub Actions |
| Monitoring | Datadog, PagerDuty |
| Analytics | Amplitude (product), Mode + Sigma (internal) |
