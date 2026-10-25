#!/usr/bin/env python3
"""Validate and normalize synthetic campaign metadata without sending it anywhere."""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path

REQUIRED = ("campaign_id", "utm_source", "utm_medium", "utm_campaign", "landing_page", "owner", "start_date")
ALLOWED_SOURCES = {"google", "meta", "tiktok", "linkedin", "email", "affiliate", "organic"}
ALLOWED_MEDIUMS = {"cpc", "paid_social", "email", "affiliate", "organic"}
MEDIUM_ALIASES = {"paid-social":"paid_social", "paid social":"paid_social", "cpc":"cpc", "ppc":"cpc", "e-mail":"email"}
SAFE_TOKEN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def token(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[\s-]+", "_", value)
    return re.sub(r"[^a-z0-9_]+", "", value).strip("_")


def validate_row(row: dict[str, str], seen: set[str]) -> tuple[dict, list[str]]:
    clean = {key: (row.get(key) or "").strip() for key in REQUIRED}
    issues = [f"Missing required field: {key}" for key, value in clean.items() if not value]
    clean["utm_source"] = token(clean["utm_source"])
    medium = token(clean["utm_medium"])
    clean["utm_medium"] = MEDIUM_ALIASES.get(medium.replace("_", " "), medium)
    clean["utm_campaign"] = token(clean["utm_campaign"])
    campaign_id = clean["campaign_id"]

    if clean["utm_source"] and clean["utm_source"] not in ALLOWED_SOURCES:
        issues.append(f"Unrecognized utm_source: {clean['utm_source']}")
    if clean["utm_medium"] and clean["utm_medium"] not in ALLOWED_MEDIUMS:
        issues.append(f"Unrecognized utm_medium: {clean['utm_medium']}")
    if clean["utm_campaign"] and not SAFE_TOKEN.fullmatch(clean["utm_campaign"]):
        issues.append("utm_campaign must use lowercase letters, numbers, and underscores")
    expected_prefix=f"{clean['utm_source']}_{clean['utm_medium']}_"
    if clean["utm_campaign"] and clean["utm_source"] and clean["utm_medium"] and not clean["utm_campaign"].startswith(expected_prefix):
        issues.append("utm_campaign should start with utm_source_utm_medium")
    if campaign_id and campaign_id in seen:
        issues.append(f"Duplicate campaign_id: {campaign_id}")
    elif campaign_id:
        seen.add(campaign_id)
    if clean["landing_page"] and not clean["landing_page"].startswith("https://"):
        issues.append("landing_page must use HTTPS")
    if clean["start_date"]:
        try:
            date.fromisoformat(clean["start_date"])
        except ValueError:
            issues.append("start_date must be an ISO date (YYYY-MM-DD)")
    return clean, issues


def run(source: Path) -> dict:
    seen: set[str] = set()
    accepted, rejected = [], []
    with source.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for line, row in enumerate(reader, start=2):
            normalized, issues = validate_row(row, seen)
            item = {"line": line, "record": normalized, "issues": issues}
            (rejected if issues else accepted).append(item)
    issue_count = sum(len(row["issues"]) for row in rejected)
    return {
        "source_file": source.name,
        "dry_run": True,
        "summary": {"rows_checked": len(accepted)+len(rejected), "accepted": len(accepted), "rejected": len(rejected), "issues": issue_count},
        "accepted": accepted,
        "rejected": rejected,
        "draft_alert": {
            "status": "review_required" if rejected else "ready",
            "message": f"Campaign QA checked {len(accepted)+len(rejected)} rows: {len(accepted)} ready, {len(rejected)} need review. No changes were published.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV containing campaign metadata")
    parser.add_argument("--out", type=Path, default=Path("output/qa_report.json"), help="Report JSON destination")
    args = parser.parse_args()
    report = run(args.input)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Wrote dry-run report to {args.out}; no campaigns or messages were sent.")


if __name__ == "__main__":
    main()
