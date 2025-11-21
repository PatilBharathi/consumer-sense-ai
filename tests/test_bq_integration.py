# tests/test_bq_integration.py
import sys, json, os
sys.path.insert(0, ".")

from workers.bq_mapper import map_doc_to_bq_row
from workers.bigquery_store import insert_review_to_bigquery

EXAMPLE_PATH = os.path.join("examples", "sample_review.json")

def main():
    with open(EXAMPLE_PATH, "r", encoding="utf-8") as f:
        doc = json.load(f)

    print("Loaded document:", doc.get("review_id"))

    row = map_doc_to_bq_row(doc)
    print("Mapped row preview:")
    for k in ["review_id", "text", "sentiment", "score", "themes", "intent", "confidence", "processed_at"]:
        print(f"  {k}: {row.get(k)}")

    res = insert_review_to_bigquery(row, test_mode=True)
    print("BigQuery mock insert result:", res)
    print("Mock file saved in examples/bq_mock/ (if test_mode=True)")

if __name__ == "__main__":
    main()
