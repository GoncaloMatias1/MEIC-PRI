import sys
import json
import requests
from sentence_transformers import SentenceTransformer
from pathlib import Path

def semantic_search(query_text, solr_url, k=30):
    """Perform semantic search using vector embeddings"""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query_text, convert_to_tensor=False).tolist()
    
    vector_str = str(query_embedding).replace(' ', '')
    
    params = {
        "q": "{!knn f=vector topK=50}" + vector_str,
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

def convert_to_evaluation_format(semantic_results):
    """Convert semantic results to format expected by evaluation scripts"""
    converted = {
        "responseHeader": {
            "status": 0,
            "QTime": 0
        },
        "response": {
            "numFound": len(semantic_results['response']['docs']),
            "start": 0,
            "docs": []
        }
    }
    
    # Group by parent_id to get complete reviews
    reviews = {}
    for doc in semantic_results['response']['docs']:
        parent_id = doc['parent_id']
        if isinstance(parent_id, list):
            parent_id = parent_id[0]
            
        if parent_id not in reviews:
            reviews[parent_id] = {
                "id": parent_id,
                "Title": doc['Title'] if isinstance(doc['Title'], str) else doc['Title'][0],
                "Content": "",
                "Score": doc.get('Score', 0),
                "score": doc.get('score', 0)
            }
        
        # Append paragraph content
        content = doc['Content'] if isinstance(doc['Content'], str) else doc['Content'][0]
        reviews[parent_id]["Content"] += content + "\n\n"
    
    converted['response']['docs'] = list(reviews.values())
    return converted

def save_results(results, query_name):
    """Save results for evaluation"""
    # Create results directory if it doesn't exist
    results_dir = Path(f"results/{query_name}")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Save results file
    results_file = results_dir / "results_semantic.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {results_file}")
    print("\nNext steps:")
    print("1. Review results using:")
    print(f"   python3 scripts/review_results.py {results_file} {results_dir}/relevance_semantic.txt")
    print("2. Generate metrics using:")
    print(f"   cat {results_file} | python3 scripts/plot_pr.py --relevance {results_dir}/relevance_semantic.txt --output {results_dir}/pr_curve_semantic.png")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 semantic_evaluation.py <query_name> \"<query_text>\"")
        sys.exit(1)
    
    query_name = sys.argv[1]
    query_text = sys.argv[2]
    solr_url = "http://localhost:8983/solr/ign_semantic"
    
    print(f"Running semantic search for: {query_text}")
    
    # Get semantic results
    results = semantic_search(query_text, solr_url)
    
    # Convert to evaluation format
    converted_results = convert_to_evaluation_format(results)
    
    # Save for evaluation
    save_results(converted_results, query_name)

if __name__ == "__main__":
    main()