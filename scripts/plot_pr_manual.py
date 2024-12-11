#!/usr/bin/env python3
import argparse
import sys
import json
import matplotlib.pyplot as plt
import numpy as np

def calculate_metrics(y_pred, y_true):
    """
    Calculate precision, recall, and metrics for relevant documents
    """
    precision = []
    recall = []
    relevant_ranks = []  # For MAP calculation
    relevant_count = 0
    
    for i, doc_id in enumerate(y_pred, start=1):
        # Check if document is relevant
        if doc_id in y_true:
            relevant_count += 1
            relevant_ranks.append(relevant_count / i)  # Precision at this relevant rank
            
        # Calculate precision and recall at this position
        precision.append(relevant_count / i)
        recall.append(relevant_count / len(y_true))
    
    # Calculate MAP as mean of precision values at relevant ranks
    map_score = np.sum(relevant_ranks) / len(y_true) if relevant_ranks else 0
    
    # Calculate interpolated precision values at 11 standard recall levels
    recall_levels = np.linspace(0.0, 1.0, 11)
    interpolated_precision = [
        max([p for p, r in zip(precision, recall) if r >= r_level], default=0)
        for r_level in recall_levels
    ]
    
    # Calculate AUC using trapezoidal rule
    auc_score = np.trapz(interpolated_precision, recall_levels)
    
    return recall_levels, interpolated_precision, map_score, auc_score

def main(input_json, relevance_file, output_file):
    """
    Process Solr results and relevance judgments to create precision-recall curve
    """
    # Read relevance judgments
    with open(relevance_file, "r") as f:
        y_true = {
            line.strip().split()[0] for line in f 
            if line.strip().split()[1] == "1"
        }
    
    # Parse Solr results
    results = json.loads(input_json)
    y_pred = [doc['id'] for doc in results['response']['docs']]
    
    # Handle empty inputs
    if not y_pred or not y_true:
        print("Error: No predictions or relevant documents found.")
        sys.exit(1)
    
    # Calculate metrics
    recall_levels, interpolated_precision, map_score, auc_score = calculate_metrics(y_pred, y_true)
    
    # Create the plot
    plt.figure(figsize=(8, 6))
    plt.plot(
        recall_levels,
        interpolated_precision,
        drawstyle="steps-post",
        label=f"MAP: {map_score:.4f}, AUC: {auc_score:.4f}",
        linewidth=1
    )
    
    # Customize plot appearance
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc="lower left", prop={"size": 10})
    
    # Save plot
    plt.savefig(output_file, format="png", dpi=300, bbox_inches='tight')
    print(f"Precision-Recall plot saved to {output_file}")
    
    # Print metrics
    print(f"\nMetrics:")
    print(f"MAP: {map_score:.4f}")
    print(f"AUC: {auc_score:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Precision-Recall curve from Solr results and relevance judgments"
    )
    parser.add_argument(
        "--relevance",
        type=str,
        required=True,
        help="Path to the relevance judgments file"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to save the output PNG file"
    )
    args = parser.parse_args()
    
    # Read JSON from stdin
    input_json = sys.stdin.read()
    main(input_json, args.relevance, args.output)