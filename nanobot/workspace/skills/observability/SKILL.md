# Observability

Use these tools when the user asks about:
- recent errors
- backend failures
- incidents
- logs
- traces
- database issues
- 500 errors
- whether anything is broken

## Available tools
- `logs_search`
- `logs_error_count`
- `traces_list`
- `traces_get`

## Instructions
1. For questions like "Any errors in the last hour?", start with `logs_error_count`.
2. If errors are found, use `logs_search` to inspect representative log lines.
3. If log lines or prior investigation reveal a trace ID, use `traces_get`.
4. If you need to discover recent traces first, use `traces_list`.
5. Summarize findings briefly and clearly.
6. Do not dump raw JSON unless the user explicitly asks for it.
7. Mention:
   - affected service
   - likely cause
   - whether the issue appears ongoing
   - one or two representative symptoms
