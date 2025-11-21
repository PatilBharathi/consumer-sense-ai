# workers/bq_mapper.py
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

def _ensure_ts(value: Optional[str]) -> Optional[str]:
    """
    Ensure timestamp string is in an ISO-8601 form BigQuery can ingest.
    If value is falsy, return current UTC time.
    """
    if value:
        return value
    return datetime.now(timezone.utc).isoformat()

def map_doc_to_bq_row(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a Firestore-style document into a BigQuery row dict.

    Expected input (example fields):
      - review_id
      - extracted_text or raw_text
      - analysis: { sentiment, score, themes, action_items, intent, confidence }
      - source, model, processing_latency_ms, created_at, processed_at, metadata

    Output schema keys (matching infra/create_bigquery_table.sql):
      review_id, text, sentiment, score, themes, action_items,
      intent, confidence, source, model, created_at, processed_at,
      processing_latency_ms, metadata
    """
    analysis = doc.get("analysis", {}) or {}

    # normalize arrays
    themes = analysis.get("themes") or []
    action_items = analysis.get("action_items") or []

    row = {
        "review_id": doc.get("review_id"),
        "text": doc.get("extracted_text") or doc.get("raw_text") or "",
        "sentiment": analysis.get("sentiment"),
        "score": float(analysis.get("score")) if analysis.get("score") is not None else None,
        "themes": list(themes) if isinstance(themes, (list, tuple)) else [str(themes)],
        "action_items": list(action_items) if isinstance(action_items, (list, tuple)) else [str(action_items)] if action_items else [],
        "intent": analysis.get("intent"),
        "confidence": float(analysis.get("confidence")) if analysis.get("confidence") is not None else None,
        "source": doc.get("source"),
        "model": doc.get("model"),
        "created_at": _ensure_ts(doc.get("created_at")),
        "processed_at": _ensure_ts(doc.get("processed_at")),
        "processing_latency_ms": int(doc.get("processing_latency_ms")) if doc.get("processing_latency_ms") is not None else None,
        "metadata": {
            "app_version": (doc.get("metadata") or {}).get("app_version"),
            "region": (doc.get("metadata") or {}).get("region"),
            "upload_method": (doc.get("metadata") or {}).get("upload_method")
        }
    }

    return row
