# Customer Call Transcript Processing

You are an expert at processing customer call transcripts and extracting key insights for product management.

**Summary guidelines:** Read `.claude/skills/customer-call-summary/SKILL.md` for detailed formatting instructions and examples.

## Task Overview

Process a customer call transcript by:
1. Determining the product area
2. Checking for existing customer files
3. Managing action items (update existing, add new, ask about unclear status)
4. Creating separate summary and transcript files with cross-references
5. Generating a comprehensive, detailed summary

## Step 1: Determine Product Area

Ask the user which product area this call relates to (or infer from context):
- **example_product** (AI Prototyping)
- **example_product Studio**
- **example_product Deploy**
- **example_product Analytics**

Base paths for customer calls:
```
product areas/AI Prototyping (example_product)/customers/calls/
product areas/example_product Studio/customer-calls/
product areas/example_product Deploy/customer-calls/
product areas/example_product Analytics/customer-calls/
```

## Step 1.5: Granola Connectivity Check

**If the user indicates the transcript is in Granola**, run a connectivity check before proceeding:

1. Call `mcp__granola__list_meetings` with `time_range: "this_week"` as a test
2. If it fails or times out, tell the user: "Granola MCP isn't connected. Check that the Granola plugin is running, then try again. In the meantime, you can paste the transcript or provide a file path."
3. If it succeeds, proceed normally

Skip this check if the user pastes a transcript or provides a file path.

## Step 2: Check for Existing Customer Files

**ALWAYS check both folders before creating new files:**

1. Search `[product-area]/customer-calls/summaries/` for `[CustomerName].md`
2. Search `[product-area]/customer-calls/transcripts/` for `[CustomerName].md`

**If files exist:**
- Review existing Open Action Items
- Ask user about any items where status is unclear (e.g., "Was [action item] completed?")
- Append the new meeting to both files (at the top, reverse chronological order)

**If no files exist:** Create new files for this customer in both folders

## Step 3: Gather Information

Ask the user for:
- **Customer name**: The name of the customer/company
- **Meeting title**: Title of the meeting
- **Meeting date**: Date in MM/DD/YY format
- **Meeting participants**: List of attendees
- **Transcript source**: Either:
  - "I'll provide the transcript" (user will paste it)
  - "It's in Granola" (search Granola for the meeting)
  - "It's in an existing file" (user will provide the file path)

## Step 4: Process and Generate Summary Content

1. Get the transcript content from the source
2. Read the summary style guide: `.claude/skills/customer-call-summary/SKILL.md`
3. Review the example for expected level of detail: `.claude/skills/customer-call-summary/examples/acme-01-27-26.md`
4. Generate the **summary content** for this meeting. This is the analytical work - extract insights, identify feature requests, draft the narrative. Include:
   - Executive Summary (with inline quotes, topic headers, opportunity areas, key product gaps)
   - Insights / Learnings (organized by topic, table format with quotes)
   - Feature Requests (organized by area, table format with quotes)
   - Next Steps (organized by category with owners)
   - Follow-up Email draft
5. Also prepare a **bullet list of feature requests** for the tracker update (customer name, feature name, context, which section of feature-requests.md they belong in)
6. Also prepare **updated action item tables** if this is an existing file (which items to move to completed, which new items to add)
7. Run through the Quality Checklist from SKILL.md before proceeding

**IMPORTANT:** Do NOT try to generate the complete file-ready markdown in this step. Generate the summary content in sections. Agent 1 will handle assembling the final file structure.

## Step 5: Write Files and Update Tracker

The main agent writes the summary and transcript files directly. Only the feature requests update is delegated to a background Task agent.

**Why no Task agents for file writing:** Task agents add startup and context-loading overhead that makes them slower than the main agent for pure write operations. The main agent already has the content - writing directly is faster.

### 5a. Write Summary File (Main Agent)

Write the summary file directly using the Write tool.

1. Assemble the complete file content by combining:
   - The `# [CustomerName] - Meeting Summaries` heading
   - The updated action item tables (from Step 4)
   - The `---` separator
   - The new meeting heading: `# MM/DD/YY - [Meeting Title]`
   - Metadata block (Date, Participants, Transcript cross-reference link)
   - The summary content sections from Step 4
   - If existing file: the `---` separator and all previous meetings from the existing file
2. Write the assembled content to `[product-area]/customer-calls/summaries/[CustomerName].md`
3. Keep all lines under 150 characters

### 5b. Write Transcript File (Main Agent via Bash)

**Use the Write tool for the header, then Bash/Python for the transcript body.** Never pass large transcript content through the Write tool or a Task agent.

**IMPORTANT:** Never use Bash heredocs for the header. The `**Date:**` line contains a colon-asterisk (`:*`) that Claude Code's settings parser interprets as a glob pattern when the command gets saved as a permission rule, which corrupts `settings.local.json`.

**For pasted text transcripts (Write tool + Python chunked approach):**
1. Write the header to the target file via the **Write tool** (not a Bash heredoc)
2. Append the transcript body using `python3 << 'PYEOF'` with Python's `open(file, "a")` and triple-quoted strings
3. For transcripts over ~15KB, split into 2-4 chunks (each chunk is a separate `python3` call that appends)
4. If appending to existing file: add separator + existing meetings after the transcript
5. Run wrap script

**For .md file source transcripts:**
1. Write the header to a temp file
2. Append transcript content from the source file (using `tail` to skip the source file's header)
3. Add separator + existing meetings (if any)
4. Move into place
5. Run wrap script

```bash
# === PASTED TEXT: Write tool + Python chunked approach ===
# Step 1: Write header using the Write tool (NOT Bash heredoc)
# Use the Write tool to create the file with the header content:
#   # [CustomerName] - Meeting Transcripts
#
#   # MM/DD/YY - [Meeting Title]
#
#   **Date:** [Full date]
#   **Participants:** [Comma-separated list]
#   **Granola Meeting ID:** [id, only include this line if source is Granola]
#   **Summary:** [View summary](../summaries/[CustomerName].md#mmddyy---meeting-title)
#
#   **Transcript:**

# Step 2: Append transcript body via Python (handles all special chars)
python3 << 'PYEOF'
transcript = """[transcript chunk 1 here - aim for ~15KB per chunk]"""
with open("[target-transcript-file]", "a") as f:
    f.write(transcript)
PYEOF

# Step 3: For large transcripts (30KB+), repeat with additional chunks
python3 << 'PYEOF'
transcript = """[transcript chunk 2 here]"""
with open("[target-transcript-file]", "a") as f:
    f.write(transcript)
PYEOF

# Step 4: Run wrap script
python3 scripts/wrap-transcript-lines.py --in-place "[target-transcript-file]"

# === .MD FILE SOURCE: Bash concatenation ===
TMPFILE=$(mktemp)
# Write header to temp file (same HEADER heredoc as above)
# Then: tail -n +7 "/path/to/source.md" >> "$TMPFILE"
# Then: add separator + existing meetings if any
# Then: mv "$TMPFILE" "[target-transcript-file]"
# Then: run wrap script
```

### 5c. Update Feature Requests (Background Task Agent)

Launch ONE Task agent **in the background** to update the feature requests tracker while the main agent continues.

**Prompt the agent with:**
- The list of feature requests identified in Step 4 (customer name, feature name, context, which section of feature-requests.md they belong in)
- The target file: `product/customers/example_product/feature-requests/feature-requests.md`

**The agent should:**
1. Read `product/customers/example_product/feature-requests/feature-requests.md`
2. For each feature request: add/update in the appropriate section
3. Update Section 4 (customer index) with any new entries
4. Update the "Last updated" date

### After writing files

- Verify both summary and transcript files exist and cross-reference links are correct
- Verify anchor link format: lowercase, spaces become hyphens, special characters removed
- Present a brief preview of key insights to the user

## Step 6: Draft Slack Summary

Present the Slack summary draft (prepared in Step 4) to the user for review. Follow the Slack Summary format in `.claude/skills/customer-call-summary/SKILL.md`, Section 6.

## Important Notes

### Level of Detail
The summary should be detailed enough that someone who wasn't on the call understands the full picture. Include specific examples and context, capture the "why" behind insights, use real examples mentioned in the call, and note blockers and dependencies. See the example in the skill folder for the expected level of detail.

### Action Item Management
Action items tables live at the TOP of the summary file (before any meetings), split by example_product Labs and Customer ownership. Each meeting: review existing items, ask about unclear status, update tables, add new items. When moving to Completed, add the completion date. See SKILL.md for the table format.

### Anchor Links
- Standard markdown auto-generates anchors from heading text
- Anchor format: lowercase, spaces become hyphens, special characters removed
- Example heading: `# 12/04/25 - Bi-Weekly Check-in`
- Auto-generated anchor: `#120425---bi-weekly-check-in`
- Links use: `[View transcript](../transcripts/CustomerName.md#120425---bi-weekly-check-in)`

### Large Transcript Handling
Pasted transcripts over ~30KB will fail with both the Write tool (output token timeout) and Bash heredocs (shell-hostile characters like single quotes, backticks, dollar signs). Use the Python chunked approach instead:
- Write the header via a small Bash heredoc (always safe)
- Append transcript body via `python3 << 'PYEOF'` with triple-quoted strings
- Split into 2-4 chunks (~15KB each) to stay under timeout thresholds
- The quoted `'PYEOF'` delimiter disables shell expansion, and Python triple-quoted strings handle all special characters

### Granola Meeting ID
When the transcript source is Granola, include a `**Granola Meeting ID:** [uuid]` line in the transcript header, after `**Participants:**`. Omit this line entirely when the source is pasted text or a file.

### File Organization
- **Summaries** go in `summaries/` subfolder
- **Transcripts** go in `transcripts/` subfolder
- Each customer has ONE summary file and ONE transcript file (with multiple meetings inside)
- Meetings are in reverse chronological order (newest first)
- Use `---` as separator between meetings

### Adding to Existing Files
When appending to existing files:
1. Read the existing file first
2. Update action items tables at the top
3. Insert the new meeting section after the action items (before previous meetings)
4. Preserve all existing content below

### Line Length Limits
**IMPORTANT:** Keep all lines under 150 characters to prevent processing issues. When writing transcripts, wrap long speaker turns at natural sentence/clause breaks. Use 4-space indentation for continuation lines within a speaker turn.

## Execution Steps

1. Confirm product area with user
2. Check for existing customer files in both summaries/ and transcripts/ folders
3. If existing files: review Open Action Items, ask user about unclear status
4. Gather meeting information
5. Get transcript content
6. Read summary skill guidelines and example
7. Generate summary content (sections), feature request list, and action item updates
8. Launch background Task agent for feature requests update
9. Write summary file directly (Write tool)
10. Write transcript file directly (Bash concatenation + wrap script)
11. Verify files exist and cross-reference links are correct
12. Check that feature requests agent completed
13. Generate and present Slack summary draft for user review
