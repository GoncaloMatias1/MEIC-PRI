#!/usr/bin/env python3
import json
import sys
import os

def display_document(doc):
    """Display document details in a readable format"""
    print("\n" + "="*80)
    print(f"ID: {doc['id']}")
    print(f"Title: {doc['Title']}")
    if 'Subtitle' in doc:
        print(f"Subtitle: {doc['Subtitle']}")
    print(f"Score: {doc.get('Score', 'N/A')}")
    print("-"*80)
    # Display first 200 characters of content
    content = doc.get('Content', '')
    print(f"Content Preview: {content[:200]}...")
    print("="*80)

def review_results(solr_response_file, output_file):
    """Review search results and create relevance judgments file"""
    # Load Solr response
    with open(solr_response_file) as f:
        results = json.load(f)
    
    docs = results['response']['docs']
    judgments = {}
    
    print(f"\nFound {len(docs)} documents to review.")
    print("For each document, enter 1 if relevant, 0 if not relevant, or 'q' to quit.")
    
    for doc in docs:
        display_document(doc)
        
        while True:
            judgment = input("Relevant? (1/0/q): ").strip().lower()
            if judgment == 'q':
                break
            elif judgment in ('0', '1'):
                judgments[doc['id']] = judgment
                break
            else:
                print("Please enter 1 (relevant), 0 (not relevant), or q (quit)")
        
        if judgment == 'q':
            break
    
    # Save judgments
    with open(output_file, 'w') as f:
        for doc_id, relevance in judgments.items():
            f.write(f"{doc_id}\t{relevance}\n")
    
    print(f"\nSaved {len(judgments)} relevance judgments to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python review_results.py <solr_response.json> <output_file.txt>")
        sys.exit(1)
        
    review_results(sys.argv[1], sys.argv[2])