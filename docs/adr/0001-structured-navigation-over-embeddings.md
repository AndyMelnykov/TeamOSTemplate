# Structured navigation over embeddings for primary retrieval

Product knowledge here is addressed through a `CLAUDE.md` router tree, predictable file naming (`{feature}-prd.md`, `YYYY-MM-DD-{topic}-decision.md`), and one join table (`feature-index.yaml`) rather than a vector index. We chose this because the domain is small and stable enough to be fully addressable — an agent can construct the right path instead of searching for it — which gives cheaper, more deterministic, and more auditable retrieval than embeddings would at this size.

## Considered Options

- Vector/semantic search over all Markdown.
- Hybrid: structure for addressable content, embeddings for the rest.

Rejected/deferred because the corpus is currently small and well-labeled enough that structure alone resolves every task in `evaluation/task-set.md`. See [`reference/01-ai-native-product-os.md`](../../reference/01-ai-native-product-os.md#ai-specific-design-decisions) for the fuller rationale, including where hybrid retrieval would become the right call.

## Consequences

Two folders — `product-development/product/competitive-research/` and the customer `Insights/` folder — are closer to unstructured collections than addressable tables, and are the most likely place this decision gets revisited (see `ROADMAP.md`).
