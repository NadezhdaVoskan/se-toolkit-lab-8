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

## Failure investigation behavior

When the user asks "What went wrong?" or "Check system health":

- Do not ask follow-up questions if observability tools can investigate directly.
- Start with recent backend errors first.
- First use `logs_search` to inspect recent error logs, prioritizing the last few minutes.
- Identify the most relevant recent backend error.
- Extract a trace ID if one is present in the log line or metadata.
- If a trace ID is available, use `traces_get` to inspect the matching trace.
- If no trace ID is available in logs but trace discovery is needed, use `traces_list` to find recent traces and then inspect the relevant one.
- Correlate logs and traces before answering.
- Summarize the findings concisely in natural language.
- Do not dump raw JSON unless the user explicitly asks for it.
- If no recent backend errors are found, say the system looks healthy.

## Proactive health checks

When the user asks to create a recurring health check for this chat:

- Use the built-in `cron` tool.
- On each run, check backend errors from the last 2 minutes.
- If recent errors exist, inspect representative log lines.
- If a trace ID is available, inspect the matching trace.
- Post a short summary into the same chat.
- If there are no recent backend errors, say the system looks healthy.
- Keep the report short and action-oriented.
