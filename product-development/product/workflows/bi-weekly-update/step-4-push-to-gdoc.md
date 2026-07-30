# Step 4: Push to Google Doc

## Goal

Auto-push the compiled bi-weekly update to a shared Google Doc using the Google Workspace MCP. This eliminates manual copy-paste and ensures the team's shared document is always in sync with the source markdown.

---

## Process

### 1. Read the compiled output file

Read the complete dated output file (`product/meetings/team-bi-weekly/docs/YYYY-MM-DD.md`). Verify all sections are present:
- What the Team Is Building Now (from Step 1)
- Customer Calls (from Step 2)
- Customer Updates / Pilot Sections (from Step 3)

If any section is missing, stop and flag to the PM before pushing.

### 2. Locate the target Google Doc

The example_product Bi-Weekly Google Doc ID should be stored in the workflow config. If not available, search for it:

```
mcp__google_workspace__search_docs({
  user_google_email: "pm@example_productlabs.dev",
  query: "example_product Bi-Weekly Update"
})
```

### 3. Prepare the content for Google Docs

Convert the markdown output to a format suitable for Google Docs:
- Preserve heading hierarchy (H1 -> Title style, H2 -> Heading 2, H3 -> Heading 3)
- Convert markdown tables to Google Docs tables
- Preserve bold, italic, and quote formatting
- Maintain link references

### 4. Push to Google Doc

Use the Google Workspace MCP to update the document:

**Option A: Append to existing doc (default)**
```
mcp__google_workspace__inspect_doc_structure({
  user_google_email: "pm@example_productlabs.dev",
  document_id: "<DOC_ID>"
})
```

Then insert the new bi-weekly content at the appropriate position (typically at the top, before previous updates):

```
mcp__google_workspace__modify_doc_text({
  user_google_email: "pm@example_productlabs.dev",
  document_id: "<DOC_ID>",
  start_index: <insertion_point>,
  text: "<formatted_content>"
})
```

**Option B: Create new doc per cycle**
```
mcp__google_workspace__create_doc({
  user_google_email: "pm@example_productlabs.dev",
  title: "example_product Bi-Weekly - YYYY-MM-DD",
  content: "<full_content>"
})
```

The PM chooses Option A or B during workflow setup. Default is Option A (single rolling doc).

### 5. Apply formatting

After inserting raw text, apply formatting in a batch:

```
mcp__google_workspace__batch_update_doc({
  user_google_email: "pm@example_productlabs.dev",
  document_id: "<DOC_ID>",
  operations: [
    { "type": "update_paragraph_style", "start_index": X, "end_index": Y, "heading_level": 1 },
    { "type": "format_text", "start_index": X, "end_index": Y, "bold": true },
    ...
  ]
})
```

### 6. Share link

After pushing, retrieve and present the doc link:

```
mcp__google_workspace__get_drive_shareable_link({
  user_google_email: "pm@example_productlabs.dev",
  file_id: "<DOC_ID>"
})
```

Present to PM: **"Bi-weekly update pushed to Google Doc: [link]. Ready for Step 5 (review)."**

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Google Doc not found | Search Drive, ask PM for doc ID |
| Auth failure | Prompt `mcp__google_workspace__start_google_auth` and retry |
| Content too large for single insert | Split into section-by-section inserts |
| Formatting fails | Push raw text first, note formatting issues for PM to fix in Google Docs |

---

## Notes

- The markdown file in `product/meetings/team-bi-weekly/docs/` remains the source of truth. The Google Doc is a distribution copy.
- If the PM prefers manual transfer (clipboard copy), skip this step and proceed directly to Step 5.
- Tables are the most fragile element in markdown-to-Google-Docs conversion. Use `create_table_with_data` for reliability.
- Always verify the push succeeded by reading back the first few lines of the doc before declaring success.
