# Global search (Cmd+K)

| Field | Value |
|-------|-------|
| Related PRD | `product/PRDs/home-page/project-search-prd.md` |
| Related RFC | `engineering/rfcs/home-page/project-search-rfc.md` |

## Overview
Build the global search modal triggered by Cmd+K that lets users find workflows, templates, and recent automation runs from anywhere in the app.

## Steps
1. Add `GET /api/search` endpoint in `src/routes/search.ts`
   - Full-text search across workflow names, descriptions, and template titles
   - Return results grouped by type: workflows, templates, runs
   - Debounce-friendly with fast response (<200ms p95)
2. Create `SearchModal` component in `src/components/search/`
   - Modal with text input, keyboard nav (arrow keys + enter)
   - Result sections: Recent, Workflows, Templates
   - Highlight matching text in results
3. Add keyboard shortcut registration
   - Register Cmd+K globally in `src/hooks/useKeyboardShortcuts.ts`
   - Esc or click-outside to dismiss
   - Focus input immediately on open
4. Add recent searches
   - Store last 5 searches in localStorage
   - Show as suggestions when modal opens with empty input
5. Add tests
   - Search returns relevant results across all types
   - Keyboard navigation cycles through results
   - Cmd+K opens and Esc closes
