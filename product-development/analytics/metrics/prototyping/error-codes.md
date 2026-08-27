# Generation Error Codes

Values for the `error_code` column on the `project-generations` table (see `../../schemas/prototyping/project-generations.md`).

| Code | Meaning |
|------|---------|
| `TIMEOUT` | Generation exceeded the model's max processing time |
| `FRAMEWORK_DETECTION_FAILED` | Could not determine the target framework from the prompt or existing project files |
| `SYNTAX_ERROR` | Generated code failed to parse |
| `DEPENDENCY_CONFLICT` | Generated code requires a package version incompatible with the project's existing dependencies |
| `CONTEXT_LIMIT_EXCEEDED` | Project context exceeded the model's input limit |
| `MODEL_ERROR` | Upstream model provider returned an error |
| `null` | Generation was cancelled by the user before completion (see `../../schemas/prototyping/project-generations.md`, Notes) |
