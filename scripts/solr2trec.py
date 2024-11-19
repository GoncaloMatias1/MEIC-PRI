#!/usr/bin/env python3

import argparse
import json
import sys


def solr_to_trec(solr_response, run_id="run0"):
    try:
        docs = solr_response["response"]["docs"]
        print(f"Processing {len(docs)} documents", file=sys.stderr)
        
        for rank, doc in enumerate(docs, start=1):
            doc_id = doc['id']
            score = doc.get('Score', 1.0)
            print(f"Doc ID: {doc_id}, Score: {score}", file=sys.stderr)
            print(f"0 Q0 {doc_id} {rank} {score} {run_id}")

    except KeyError as e:
        print(f"Error: Invalid Solr response format. Key not found: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Solr results to TREC format.")
    parser.add_argument(
        "--run-id",
        type=str,
        default="run0",
        help="Experiment or system identifier (default: run0).",
    )
    args = parser.parse_args()

    try:
        solr_response = json.load(sys.stdin)
        solr_to_trec(solr_response, args.run_id)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}", file=sys.stderr)
        sys.exit(1)