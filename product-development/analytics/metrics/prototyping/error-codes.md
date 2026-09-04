# Automation Run Error Codes

Values for the `error_code` column on the `project-generations` table (see `../../schemas/prototyping/project-generations.md`).

| Code | Meaning |
|------|---------|
| `TIMEOUT` | Automation run exceeded the model's max processing time |
| `FRAMEWORK_DETECTION_FAILED` | Could not determine the document type (contract, invoice, intake form, etc.) from the instruction or uploaded document |
| `SYNTAX_ERROR` | Extracted field/clause data failed to validate against the expected schema |
| `DEPENDENCY_CONFLICT` | Extracted routing instructions conflict with the workflow's existing approval routing configuration |
| `CONTEXT_LIMIT_EXCEEDED` | Document page count/content exceeded the model's input limit |
| `MODEL_ERROR` | Upstream AI extraction model provider returned an error |
| `null` | Automation run was cancelled by the user before completion (see `../../schemas/prototyping/project-generations.md`, Notes) |
