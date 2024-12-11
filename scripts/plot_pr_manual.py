#!/usr/bin/env python3

import argparse
import sys
import json
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import auc

def calculate_metrics(precision, recall):
    """Calculate MAP, AUC, and AVP"""
    map_score = np.mean(precision)
    auc_score = auc(recall, precision)
    avp = np.mean([p for p, r in zip(precision, recall)]) 
    return map_score, auc_score, avp

def main(input_json, relevance_file: str, output_file: str):
    # Read relevance judgments
    relevant_docs = {}
    with open(relevance_file, 'r') as f:
        for line in f:
            doc_id, relevance = line.strip().split('\t')
            relevant_docs[doc_id] = int(relevance)
    
    # Parse input JSON
    results = json.loads(input_json)
    retrieved_docs = [doc['id'] for doc in results['response']['docs']]
    
    # Calculate metrics
    precision = []
    recall = []
    relevant_count = 0
    total_relevant = sum(1 for rel in relevant_docs.values() if rel == 1)
    
    for i, doc_id in enumerate(retrieved_docs, 1):
        if doc_id in relevant_docs and relevant_docs[doc_id] == 1:
            relevant_count += 1
        precision.append(relevant_count / i)
        recall.append(relevant_count / total_relevant if total_relevant > 0 else 0)

    # Calculate metrics
    map_score, auc_score, avp = calculate_metrics(precision, recall)
    
    # Plot step curve
    plt.figure(figsize=(10, 6))
    plt.step(recall, precision, 'b-', where='post', 
             label=f'AVP: {avp:.3f}, MAP: {map_score:.3f}, AUC: {auc_score:.3f}')
    
    # Calculate P@k values
    p_at_k = {}
    for k in [5, 10, 15, 20]:
        if k <= len(precision):
            p_at_k[k] = precision[k-1]
    
    # Add P@k values to plot
    p_at_k_text = ", ".join([f"P@{k}:{v:.2f}" for k, v in p_at_k.items()])
    plt.figtext(0.5, 0.01, p_at_k_text, wrap=True, horizontalalignment='center', fontsize=8)
    
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.grid(True)
    plt.legend(loc='lower left')
    plt.ylim(0, 1.2)
    plt.xlim(0, 1.2)
    plt.savefig(output_file, bbox_inches='tight', dpi=300)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Step-Style Precision-Recall curve")
    parser.add_argument('--relevance', required=True, help='File containing manual relevance judgments')
    parser.add_argument('--output', required=True, help='Output PNG file path')
    args = parser.parse_args()
    
    # Read JSON from stdin
    input_json = sys.stdin.read()
    main(input_json, args.relevance, args.output)