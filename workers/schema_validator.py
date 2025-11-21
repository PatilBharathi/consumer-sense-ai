print("DEBUG: script loaded")


import json
import os
from jsonschema import Draft7Validator, FormatChecker

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schemas", "firestore_review_schema.json")

def load_schema(path=SCHEMA_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

SCHEMA = load_schema()
VALIDATOR = Draft7Validator(SCHEMA, format_checker=FormatChecker())

def validate_review_doc(doc: dict):
    errors = []
    for err in VALIDATOR.iter_errors(doc):
        path = ".".join([str(p) for p in err.path]) if err.path else ""
        msg = f"{path}: {err.message}" if path else err.message
        errors.append(msg)
    return (len(errors) == 0, errors)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate a JSON file against Firestore review schema.")
    parser.add_argument("jsonfile", help="Path to the JSON file to validate")
    args = parser.parse_args()

    with open(args.jsonfile, "r", encoding="utf-8") as fh:
        doc = json.load(fh)

    ok, errs = validate_review_doc(doc)

    if ok:
        print("OK: document is valid.")
    else:
        print("INVALID: document failed validation.")
        for e in errs:
            print(" -", e)
        exit(2)
