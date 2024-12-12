import sys
import json
import requests
from sentence_transformers import SentenceTransformer

def semantic_search(query_text, solr_url, k=30):
    """Perform semantic search using vector embeddings"""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query_text, convert_to_tensor=False).tolist()
    
    params = {
        "q": "{!knn f=vector topK=50}" + str(query_embedding),
        "fl": "id,parent_id,Title,Content,Score,paragraph_num,score",
        "rows": k,
        "wt": "json"
    }
    
    response = requests.post(
        f"{solr_url}/select",
        data=params,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    response.raise_for_status()
    
    return response.json()

def save_results(results, query_name, suffix="_rewritten"):
    """Save results with specified suffix"""
    results_dir = f"results/{query_name}"
    results_file = f"{results_dir}/results_semantic{suffix}.json"
    
    # Create directory if it doesn't exist
    import os
    os.makedirs(results_dir, exist_ok=True)
    
    # Save results
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {results_file}")
    print("\nNext steps:")
    print(f"1. Review results:")
    print(f"   python3 scripts/review_results.py {results_file} {results_dir}/relevance_semantic{suffix}.txt")
    print(f"2. Generate metrics:")
    print(f"   cat {results_file} | python3 scripts/plot_pr.py --relevance {results_dir}/relevance_semantic{suffix}.txt --output {results_dir}/pr_curve_semantic{suffix}.png")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 semantic_evaluation.py <query_name> \"<query_text>\"")
        sys.exit(1)
    
    category = sys.argv[1]
    query_text = sys.argv[2]
    solr_url = "http://localhost:8983/solr/ign_semantic"
    
    # Expand query with category-specific terms
    expanded_query = query_text + " gameplay mechanics control system input response"
    print(f"Original query: {query_text}")
    print(f"Expanded query: {expanded_query}")
    
    # Get results
    results = semantic_search(expanded_query, solr_url)
    
    # Save with _rewritten suffix
    save_results(results, category, "_rewritten")

if __name__ == "__main__":
    main()