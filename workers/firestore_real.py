# workers/firestore_real.py
"""
Firestore save helper.

Usage:
    from workers.firestore_real import save_review_to_firestore

    # test mode (local)
    save_review_to_firestore(doc, test_mode=True)

    # real mode (requires google-cloud-firestore and credentials / Workload Identity)
    save_review_to_firestore(doc, test_mode=False)

Notes:
- For production prefer Workload Identity / Application Default Credentials.
- To use service account JSON locally, set GOOGLE_APPLICATION_CREDENTIALS env var to the key file path.
- Install real dependency when switching to real mode:
    pip install google-cloud-firestore
"""

import json
import os
import uuid
from typing import Dict, Any

LOCAL_DIR = os.path.join(os.getcwd(), "examples", "fs_real_mock")
os.makedirs(LOCAL_DIR, exist_ok=True)

def save_review_to_firestore(doc: Dict[str, Any], test_mode: bool = True) -> Dict[str, Any]:
    """
    Save review document to Firestore (real) or to local mock folder (test_mode).

    Returns:
      - test_mode: {"status":"mock_saved", "path": ...}
      - real mode: {"status":"ok", "doc_id": "<firestore-id>"} or raises/returns error info.
    """
    if test_mode:
        fname = f"fsreal-{uuid.uuid4().hex[:8]}.json"
        path = os.path.join(LOCAL_DIR, fname)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
        return {"status": "mock_saved", "path": path}

    # ---------- Real Firestore insertion ----------
    try:
        from google.cloud import firestore
    except Exception as e:
        raise RuntimeError(
            "google-cloud-firestore is required for real Firestore saves. "
            "Install with: pip install google-cloud-firestore"
        ) from e

    # Option A: use ADC / Workload Identity (recommended on Cloud Run)
    client = firestore.Client()

    # collection name
    collection = os.getenv("FIRESTORE_COLLECTION", "consumer_reviews")

    # Use provided review_id or generate one
    doc_id = doc.get("review_id") or str(uuid.uuid4())

    try:
        col_ref = client.collection(collection)
        col_ref.document(doc_id).set(doc)
        return {"status": "ok", "doc_id": doc_id}
    except Exception as exc:
        return {"status": "error", "exception": str(exc)}
