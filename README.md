# MarTech Ops Toolkit — Campaign QA & Safe Automation

A small, practical toolkit for catching campaign-tagging errors before launch. It combines a dependency-free Python validator with an importable n8n webhook workflow. The demo data is synthetic; the workflow returns a validation result and **does not send messages or change campaigns**.

## Run the local validator

```bash
python campaign_tag_qc.py sample/campaigns.csv --out output/qa_report.json
```

The output contains normalized rows, rejected rows, rule-level findings, and a draft alert payload for a human to review.
An example output is included at `examples/sample_qa_report.json`.

## Import the n8n workflow

1. In n8n, choose **Import from File** and select `n8n/campaign-tag-qa-webhook.json`.
2. Activate the workflow after reviewing the Code node.
3. Send a JSON payload to the webhook path shown in the workflow.
4. Inspect the JSON response; add your approved destination or CRM action only after mapping and testing it in your own environment.

Example payload:

```json
{
  "campaign_id": "cmp_1042",
  "utm_source": "Meta",
  "utm_medium": "paid-social",
  "utm_campaign": "instamart_q4_launch",
  "landing_page": "https://example.com/collections/weekly-box",
  "owner": "Growth",
  "start_date": "2026-11-01"
}
```

## Checks included

- Required campaign fields and valid dates
- Source and medium normalization
- Duplicate campaign IDs
- UTM naming convention (`source_medium_campaign`)
- HTTPS landing pages
- A clear pass/review status with issue reasons

## Safety and setup

- All examples are fabricated and contain no customer data.
- The workflow has no credentials or live Slack/CRM nodes.
- The default output is a reviewable JSON result; no notification or campaign launch occurs.
- For real use, add credentials through n8n's credential manager. Never commit tokens, webhook secrets, customer exports, or production campaign data.
