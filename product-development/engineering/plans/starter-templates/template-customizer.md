# Template customizer

## Overview
Add a preview and customization step between selecting a template and starting a workflow, so users can tweak branding, fields, and routing before committing.

## Steps
1. Create `TemplatePreview` page at `/templates/:id/preview`
   - Full-width live preview of the template's portal in an iframe
   - Sidebar with customization controls
   - "Use this template" button creates a workflow with applied customizations
2. Add customization panel in `src/components/templates/`
   - Color picker: primary, secondary, accent, background (portal branding)
   - Font selector: heading and body font from curated list
   - Content fields: replace placeholder text (company name, clause wording, CTA)
3. Build preview update pipeline
   - Apply customizations in real time to the iframe preview
   - Use CSS custom properties for color/font swaps
   - Text replacements via DOM manipulation in the preview frame
4. Add "Start with AI" option
   - Instead of manual customization, user describes changes in an instruction (e.g., "route POs over $5K to procurement")
   - AI applies requested modifications to the template as a starting point
5. Add tests
   - Color changes reflect immediately in preview
   - Font swap applies to correct elements
   - Created workflow contains all customizations
