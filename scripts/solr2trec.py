#!/usr/bin/env python3

import argparse
import json
import sys


def solr_to_trec(solr_response, run_id="run0"):
    """
    Converts Solr search results to TREC format and writes the results to STDOUT.

    Format:
    qid     iter    docno       rank    sim     run_id
    0       Q0      M.EIC028    1       0.80    run0
    """
    try:
        # Extract the document results from the Solr response
        docs = solr_response["response"]["docs"]

        # Enumerate through the results and write them in TREC format
        for rank, doc in enumerate(docs, start=1):
            # Use Score instead of score, and handle Title being a list
            print(f"0 Q0 {doc['id']} {rank} {doc['Score']} {run_id}")

    except KeyError as e:
        print(f"Error: Invalid Solr response format. Key not found: {e}")
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

    solr_response = json.load(sys.stdin)
    solr_to_trec(solr_response, args.run_id)