# Architecture and operating boundaries

```text
CSV export or webhook request
            │
            ▼
Normalize source / medium / campaign tokens
            │
            ▼
Validate required fields, dates, URLs, and duplicate IDs
      ┌─────┴─────┐
      ▼           ▼
Accepted rows   Review queue + issue reasons
      └─────┬─────┘
            ▼
       JSON result
```

The Python CLI and n8n webhook use the same basic rules. The workflow returns a response for human review. It does not call an email provider, CRM, Slack, or ad platform, and it does not create or launch campaigns. A production extension should add authenticated connectors, audit logging, idempotency, and an explicit human approval step before any write action.
