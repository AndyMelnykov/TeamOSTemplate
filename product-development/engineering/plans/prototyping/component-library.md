# Clause & field block library

## Overview
Let users save reusable clause and field blocks (signature blocks, approval steps, standard clauses) from one workflow and drop them into new workflows, building a personal library over time.

## Steps
1. Add "Save as block" action in the workflow builder
   - Right-click a clause or field group → "Save to library"
   - Prompt for block name and optional tags
   - Extract block definition + extraction rules into `saved_blocks` table
2. Add `GET/POST /api/blocks` endpoints in `src/routes/blocks.ts`
   - List user's saved blocks with preview thumbnails
   - Create new block from selected field/clause group
3. Create `BlockLibrary` panel in `src/components/builder/`
   - Searchable grid of saved blocks with visual previews
   - Drag or click to insert into current workflow
   - Edit name/tags inline
4. Add block insertion logic
   - Insert block definition at cursor position or selected step
   - Resolve field-mapping conflicts with existing workflow fields
   - Adapt routing conditions to match workflow settings
5. Add tests
   - Save extracts correct field/clause tree and rules
   - Insert renders block correctly in new workflow
   - Search filters by name and tags
