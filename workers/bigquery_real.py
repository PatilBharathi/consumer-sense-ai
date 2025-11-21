# workers/bigquery_real.py
"""
BigQuery insertion helper.

Usage:
    from workers.bigquery_real import insert_review_to_bigquery

    # test mode (local file)
    insert_review_to_bigquery(row, test_mode=True)

    # real mode (requires google-cloud-bigquery and valid credentials)
    insert_review_to_bigquery(row, test_mode=False)

Environment & config:
    - BQ_TABLE: required for real mode. Format: project.dataset.table
      e.g. my-project.my_dataset.consumer_reviews
    - GOOGLE_APPLICATION_CREDENTIALS or Workload Identity (recommended) must provide
      authentication to BigQuery when test_mode=False.

Install real dependency when switching to real mode:
    pip install google-cloud-bigquery

Notes on production:
    - For high throughput, use the Storage Write API or batch loads (GCS -> load job).
    - insert_rows_json is fine for demo / low-to-medium traffic.
    - Use Workload Identity on Cloud Run to avoid service account JSON keys.
"""

import json
import os
import uuid
from typing import Dict, Any

# Local mock directory for test_mode (no GCP calls)
LOCAL_BQ_DIR = os.path.join(os.getcwd(), "examples", "bq_real_mock")
os.makedirs(LOCAL_BQ_DIR, exist_ok=True)

def insert_review_to_bigquery(row: Dict[str, Any], test_mode: bool = True) -> Dict[str, Any]:
    """
    Insert a row into BigQuery or save locally in test mode.

    Args:
        row: dict matching BigQuery table schema (see infra/create_bigquery_table.sql)
        test_mode: if True, save locally in examples/bq_real_mock/; if False, perform real insert.

    Returns:
        dict with status and metadata (e.g., path or insert info)
    """
    if test_mode:
        fname = f"bqreal-{uuid.uuid4().hex[:8]}.json"
        path = os.path.join(LOCAL_BQ_DIR, fname)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(row, fh, indent=2, ensure_ascii=False)
        return {"status": "mock_saved", "path": path}

    # ---------- Real BigQuery insertion ----------
    # Lazy import to avoid adding dependency during mock mode
    try:
        from google.cloud import bigquery
    except Exception as e:
        raise RuntimeError(
            "google-cloud-bigquery is required for real BigQuery inserts. "
            "Install with: pip install google-cloud-bigquery"
        ) from e

    BQ_TABLE = os.getenv("BQ_TABLE")
    if not BQ_TABLE:
        raise RuntimeError("Environment variable BQ_TABLE is required in real mode (project.dataset.table).")

    # Create client (uses ADC / Workload Identity if available)
    client = bigquery.Client()

    # Use insert_rows_json for simple inserts
    try:
        # insert_rows_json expects a table reference or table id
        errors = client.insert_rows_json(BQ_TABLE, [row])
        if errors:
            # errors is a list of error details; include them in the response
            return {"status": "error", "errors": errors}
        return {"status": "ok", "inserted": 1}
    except Exception as exc:
        # Catch and return exception message (caller can log or raise)
        return {"status": "error", "exception": str(exc)}

