# workers/bigquery_store.py
"""
Local stub for BigQuery insertion.
Later we will replace the stub with actual BigQuery client calls.

Functions:
- insert_review_to_bigquery(row: dict, test_mode=True)
"""

import json
import os
import uuid
from datetime import datetime, timezone

def insert_review_to_bigquery(row: dict, test_mode: bool = True):
    """
    In test_mode, simply save the row to local folder:
    examples/bq_mock/<uuid>.json
    This lets us simulate BigQuery insertion during development.
    """
    if test_mode:
        dirpath = os.path.join(os.getcwd(), "examples", "bq_mock")
        os.makedirs(dirpath, exist_ok=True)

        fname = f"bqrow-{uuid.uuid4().hex[:8]}.json"
        path = os.path.join(dirpath, fname)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(row, f, indent=2, ensure_ascii=False)

        return {"status": "mock_saved", "path": path}

    # Actual BigQuery code will be added later
    raise NotImplementedError("BigQuery real insert not implemented yet.")
