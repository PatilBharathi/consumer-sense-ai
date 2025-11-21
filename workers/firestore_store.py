# workers/firestore_store.py
"""
Firestore helper (local stub + real template).

Usage:
- save_review(doc, test_mode=True)  # during local dev, saves to examples/fs_mock/
- save_review(doc, test_mode=False) # in prod, will use Firestore client (requires credentials)

Notes:
- For production, prefer Workload Identity (no JSON keys). If you must use a key file, load it from Secret Manager.
- Install google-cloud-firestore when you switch to real mode:
    pip install google-cloud-firestore
"""

import json
import os
import uuid
from typing import Dict, Any

LOCAL_DIR = os.path.join(os.getcwd(), "examples", "fs_mock")
os.makedirs(LOCAL_DIR, exist_ok=True)

def save_review(doc: Dict[str, Any], test_mode: bool = True) -> Dict[str, Any]:
    """
    Save a review document.

    In test_mode: save locally under examples/fs_mock/<uuid>.json and return {"status":"mock_saved", "path": ...}

    In prod mode: attempts to write to Firestore and returns {"status":"ok", "doc_id": ...} or raises exception.
    """
    if test_mode:
        fname = f"fsdoc-{uuid.uuid4().hex[:8]}.json"
        path = os.path.join(LOCAL_DIR, fname)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
        return {"status": "mock_saved", "path": path}

    # --------- Real Firestore implementation (uncomment when using) ----------
    # from google.cloud import firestore
    #
    # # Option A: rely on Application Default Credentials / Workload Identity
    # client = firestore.Client()
    #
    # # Option B: if you must load a service account JSON (not recommended),
    # # set GOOGLE_APPLICATION_CREDENTIALS env var to the key file path (or use Secret Manager)
    #
    # col = client.collection("consumer_reviews")
    # doc_ref = col.document(doc.get("review_id") or str(uuid.uuid4()))
    # doc_ref.set(doc)
    # return {"status": "ok", "doc_id": doc_ref.id}
    # -----------------------------------------------------------------------

    # If execution reaches here, no real implementation was enabled.
    raise RuntimeError("save_review called with test_mode=False but Firestore code is not enabled. "
                       "Uncomment and configure Firestore client code as instructed in the file.")
