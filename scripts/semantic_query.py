import sys
import json
import requests
from sentence_transformers import SentenceTransformer
from collections import defaultdict

def semantic_search(query_text, solr_url, k=30):  # Increased k for more candidates
    """
    Perform semantic search using vector embeddings
    """
    # Load the model and generate embedding for query
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query_text, convert_to_tensor=False).tolist()
    
    # Format the vector string properly
    vector_str = str(query_embedding).replace(' ', '')
    
    # Prepare Solr query with explicit parameters
    params = {
        "q": "{!knn f=vector topK=50}" + vector_str,  # Increased topK further
        "fl": "id,parent_id,Title,Content,Score,paragraph_num,score",
        "rows": k,
        "wt": "json",
        "sort": "score desc"
    }
    
    # Send request to Solr
    response = requests.post(
        f"{solr_url}/select",
        data=params,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    response.raise_for_status()
    
    return response.json()

def display_results(results):
    """Display search results in a readable format"""
    docs = results['response']['docs']
    print(f"\nFound {len(docs)} relevant paragraphs")
    print("-" * 80)
    
    # Group paragraphs by review
    reviews = defaultdict(list)
    for doc in docs:
        parent_id = doc['parent_id']
        if isinstance(parent_id, list):
            parent_id = parent_id[0]
            
        reviews[parent_id].append(doc)
    
    # Display top 5 reviews with their relevant paragraphs
    for parent_id, paragraphs in list(reviews.items())[:5]:
        # Sort paragraphs by their order in the review
        paragraphs.sort(key=lambda x: x['paragraph_num'])
        
        # Get review title
        title = paragraphs[0]['Title']
        if isinstance(title, list):
            title = title[0]
            
        print(f"\nReview: {title}")
        print(f"Best match score: {max(float(p.get('score', 0)) for p in paragraphs):.4f}")
        print("\nRelevant excerpts:")
        
        # Show up to 3 most relevant paragraphs from each review
        for para in paragraphs[:3]:
            content = para['Content']
            if isinstance(content, list):
                content = content[0]
            print(f"\nParagraph {para['paragraph_num']}:")
            print(content)
        
        print("-" * 80)

def main():
    solr_url = "http://localhost:8983/solr/ign_semantic"
    
    # Get query from command line or prompt
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter your search query: ")
    
    # Enhance the query to be more specific about combat mechanics
    enhanced_query = f"The combat mechanics and fighting system in this game. {query}"
    
    print(f"\nSearching for: {query}")
    
    try:
        results = semantic_search(enhanced_query, solr_url)
        display_results(results)
    except Exception as e:
        print(f"Error performing search: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()