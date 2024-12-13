import sys
import json
from collections import Counter
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('stopwords')

def load_results_and_judgments(category):
    """Load results and relevance judgments for a category"""
    # Load results
    with open(f"results/{category}/results_semantic_rewritten.json") as f:
        results = json.load(f)
    
    # Load relevance judgments
    relevant_docs = {}
    with open(f"results/{category}/relevance_semantic_rewritten.txt") as f:
        for line in f:
            doc_id, relevance = line.strip().split('\t')
            relevant_docs[doc_id] = int(relevance)
    
    return results, relevant_docs

def extract_terms(text):
    """Extract important terms from text"""
    # Tokenize and convert to lowercase
    tokens = word_tokenize(text.lower())
    
    # Remove stopwords and punctuation
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    
    return tokens

def get_important_terms(results, relevant_docs, top_n=10):
    """Get most important terms from relevant documents"""
    term_counter = Counter()
    
    # Count terms in relevant documents
    for doc in results['response']['docs']:
        if doc['id'] in relevant_docs and relevant_docs[doc['id']] == 1:
            terms = extract_terms(doc['Content'])
            term_counter.update(terms)
    
    # Get top terms
    return [term for term, count in term_counter.most_common(top_n)]

def create_enhanced_query(category, original_query, important_terms):
    """Create enhanced query using original query and important terms"""
    if category == 'technical':
        base = "games with impressive graphics visual quality performance and technical features"
    elif category == 'controls':
        base = "responsive precise controls and good handling gameplay mechanics"
    elif category == 'multiplayer':
        base = "multiplayer online games with co-op or competitive gameplay features"
    elif category == 'relaxing':
        base = "peaceful calming relaxing games with soothing gentle gameplay"
    elif category == 'story_narrative':
        base = "games with excellent story narrative writing characters and plot"
    
    term_string = " ".join(important_terms)
    enhanced_query = f"{base} {term_string}"
    
    return enhanced_query

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 relevance_feedback.py <category>")
        sys.exit(1)
    
    category = sys.argv[1]
    
    # Load data
    results, relevant_docs = load_results_and_judgments(category)
    
    # Get important terms
    important_terms = get_important_terms(results, relevant_docs)
    print("\nMost important terms from relevant documents:")
    print(", ".join(important_terms))
    
    # Create enhanced query
    enhanced_query = create_enhanced_query(category, "", important_terms)
    print("\nEnhanced query:")
    print(enhanced_query)
    
    # Save enhanced query for semantic search
    output_file = f"results/{category}/query_semantic_feedback.txt"
    with open(output_file, 'w') as f:
        f.write(enhanced_query)
    
    print(f"\nSaved enhanced query to {output_file}")
    print("\nNext steps:")
    print(f"1. Run semantic search with enhanced query:")
    print(f"   python3 scripts/semantic_evaluation.py {category} \"{enhanced_query}\"")

if __name__ == "__main__":
    main()