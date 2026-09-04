# Instruction suggestions

## Overview
Show contextual starter instructions below the main input based on the user's past workflows and trending templates, replacing the static placeholder text.

## Steps
1. Create `SuggestionEngine` service in `src/services/suggestions.ts`
   - Pull user's last 5 workflow types (vendor contract, invoice, intake form, etc.)
   - Mix in 2-3 trending templates from the catalog
   - Return 4-6 instruction suggestions ranked by relevance
2. Add `GET /api/home/suggestions` endpoint in `src/routes/home.ts`
   - Call SuggestionEngine, return formatted suggestion cards
   - Cache per user for 1 hour
3. Create `SuggestionChips` component in `src/components/home/`
   - Render horizontally scrollable chips below the instruction input
   - Click fills the instruction input with the suggestion text
   - Show skeleton loader while fetching
4. Add new-user fallback path
   - If no workflow history, show category-based starters (vendor contract, invoice, intake form, purchase order)
5. Add tests
   - Suggestions reflect user workflow history
   - Fallback renders for new users
   - Click populates instruction input
