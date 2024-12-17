from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from collections import defaultdict
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from sentence_transformers import SentenceTransformer
import random

app = Flask(__name__)
CORS(app)

# Configure Solr endpoints
SOLR_BASE_URL = "http://localhost:8983/solr"
CORES = {
    'boosted': 'ign_boosted',
    'semantic': 'ign_semantic'
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/latest')
def get_latest_reviews():
    try:
        # Query Solr for latest reviews
        solr_url = f"{SOLR_BASE_URL}/ign_boosted/select"
        query = {
            "params": {
                "q": "Subheader:*2024*",  # Find reviews from 2024
                "fl": "id,Title,Content,Score,Subtitle,Subheader",
                "rows": 20,  # Get more to randomly select from
                "sort": "random_1234 desc"  # Random sort
            }
        }
        
        response = requests.post(solr_url, json=query)
        response.raise_for_status()
        
        results = response.json()
        if results['response']['docs']:
            # Select 6 random reviews from the results
            latest_reviews = random.sample(results['response']['docs'], min(6, len(results['response']['docs'])))
            return jsonify(latest_reviews)
        else:
            return jsonify([])
            
    except Exception as e:
        app.logger.error(f"Error fetching latest reviews: {str(e)}")
        return jsonify([]), 500

@app.route('/review/<review_id>')
def get_review(review_id):
    try:
        # Query Solr for the specific review
        solr_url = f"{SOLR_BASE_URL}/ign_boosted/select"
        query = {
            "params": {
                "q": f"id:{review_id}",
                "fl": "*",
                "rows": 1
            }
        }
        
        response = requests.post(solr_url, json=query)
        response.raise_for_status()
        
        results = response.json()
        if results['response']['docs']:
            return jsonify(results['response']['docs'][0])
        else:
            return jsonify({'error': 'Review not found'}), 404
            
    except Exception as e:
        app.logger.error(f"Error fetching review: {str(e)}")
        return jsonify({'error': 'Failed to fetch review'}), 500

@app.route('/more-like-this/<review_id>')
def get_similar_reviews(review_id):
    try:
        # First get the original review from boosted core
        solr_url = f"{SOLR_BASE_URL}/ign_boosted/select"
        
        # Get the original review
        query = {
            "params": {
                "q": f"id:{review_id}",
                "fl": "*"
            }
        }
        
        response = requests.post(solr_url, json=query)
        review = response.json()['response']['docs'][0]
        
        # Now find similar reviews using mlt query
        similar_query = {
            "params": {
                "q": f"{review['Content']}",  # Use the content for similarity
                "defType": "edismax",
                "qf": "Content^4 Title^2",
                "pf": "Content^2",
                "fq": f"-id:{review_id}",  # Exclude the current review
                "fl": "id,Title,Score,Subtitle,Content",
                "rows": "5",
                "sort": "score desc"
            }
        }
        
        similar_response = requests.post(solr_url, json=similar_query)
        similar_response.raise_for_status()
        
        return jsonify(similar_response.json()['response']['docs'])
        
    except Exception as e:
        app.logger.error(f"Error fetching similar reviews: {str(e)}")
        return jsonify([]), 500

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        query = data.get('query', '')
        search_type = data.get('searchType', 'boosted')
        category = data.get('category', 'all')
        min_score = float(data.get('minScore', 0)) if data.get('minScore') else None
        
        # Don't require query if category is selected
        if not query and category == 'all':
            return jsonify({'error': 'Query is required when no category is selected'}), 400
            
        # Get appropriate core name
        core = CORES.get(search_type, CORES['boosted'])
        
        # Construct Solr query based on search type
        solr_query = construct_solr_query(query, search_type, category, min_score)
        
        # Send request to Solr
        solr_url = f"{SOLR_BASE_URL}/{core}/select"
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(solr_url, json=solr_query, headers=headers)
        response.raise_for_status()
        
        results = response.json()
        
        if results['response']['docs']:
            docs = results['response']['docs']
            
            # Cluster results if we have enough documents
            if len(docs) >= 3:
                clustered_results, cluster_labels = cluster_results(docs)
            else:
                clustered_results = {'0': docs}
                cluster_labels = {'0': 'All Results'}
                
            return jsonify({
                'clusters': clustered_results,
                'cluster_labels': cluster_labels,
                'total': results['response']['numFound']
            })
        else:
            return jsonify({
                'clusters': {'0': []},
                'cluster_labels': {'0': 'No Results'},
                'total': 0
            })
            
    except requests.RequestException as e:
        app.logger.error(f"Solr request failed: {str(e)}")
        return jsonify({'error': 'Failed to connect to search server'}), 503
    except Exception as e:
        app.logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def construct_solr_query(query, search_type, category, min_score=None):
    """Construct appropriate Solr query based on search parameters"""
    base_query = {
        "params": {
            "fl": "id,Title,Content,Score,Subtitle,Subheader",
            "rows": 30
        }
    }
    
    # Add score filter if specified
    if min_score is not None and min_score > 0:
        base_query["params"]["fq"] = f"Score:[{min_score} TO *]"

    # If no query but category selected, search by category
    if not query and category != 'all':
        category_terms = {
            'controls': 'Content:(controls OR gameplay OR mechanics OR handling)',
            'multiplayer': 'Content:(multiplayer OR "co-op" OR "online multiplayer" OR "pvp" OR "player vs player" OR "competitive multiplayer" OR "online mode" OR "multiplayer mode" OR "cooperative" OR "online play" OR "team-based" OR "battle royale")',
            'relaxing': 'Content:(relaxing OR peaceful OR calm OR casual)',
            'story': 'Content:(story OR narrative OR plot OR characters)',
            'technical': 'Content:(graphics OR performance OR fps OR resolution)'
        }
        base_query["params"]["q"] = category_terms.get(category, '*:*')
        base_query["params"]["sort"] = "Score desc"  # Sort by score when searching by category only
    
    elif search_type == 'semantic':
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_vector = model.encode(query, convert_to_tensor=False).tolist()
        base_query["params"].update({
            "q": "{!knn f=vector topK=50}" + str(query_vector),
            "rows": 30
        })
    else:  # boosted with query
        # Clean and prepare the query
        clean_query = query.strip()
        terms = clean_query.split()
        
        if len(terms) > 1:
            base_query["params"].update({
                "defType": "edismax",
                "q": f"Title:\"{clean_query}\"^10 OR Content:\"{clean_query}\"^8 OR "
                     f"Title:({clean_query})^5 OR Content:({clean_query})^4",
                "qf": "Title^5 Content^3 Subtitle^2",
                "pf": "Title^10 Content^8",
                "mm": "75%",
                "tie": "0.1"
            })
        else:
            base_query["params"].update({
                "defType": "edismax",
                "q": f"Title:({clean_query})^5 OR Content:({clean_query})^3",
                "qf": "Title^4 Content^2 Subtitle",
                "mm": "100%"
            })

        # If category is selected with a query, add it as a filter
        if category != 'all':
            category_terms = {
                'controls': '(controls OR gameplay OR mechanics OR handling)',
                'multiplayer': '(multiplayer OR cooperative OR online OR pvp)',
                'relaxing': '(relaxing OR peaceful OR calm OR casual)',
                'story': '(story OR narrative OR plot OR characters)',
                'technical': '(graphics OR performance OR fps OR resolution)'
            }
            if category in category_terms:
                filter_query = f"Content:({category_terms[category]})"
                if 'fq' in base_query["params"]:
                    base_query["params"]["fq"] += f" AND {filter_query}"
                else:
                    base_query["params"]["fq"] = filter_query
    
    return base_query

def cluster_results(docs, num_clusters=5):
    if not docs:
        return {}, {}
        
    # Predefined categories and their associated keywords
    categories = {
        'Tight Controls': [
            'combat', 'controls', 'gameplay', 'mechanics', 'handling', 'movement',
            'responsive', 'fluid', 'precise', 'tight', 'combat system'
        ],
        'Story & Narrative': [
            'story', 'narrative', 'plot', 'character', 'dialogue', 'writing',
            'cutscene', 'storytelling', 'campaign', 'lore', 'world-building'
        ],
        'Multiplayer & Social': [
            'multiplayer', 'co-op', 'cooperative', 'pvp', 'online',
            'competitive', 'team', 'social', 'battle royale', 'community'
        ],
        'Technical & Graphics': [
            'graphics', 'performance', 'fps', 'resolution', 'visual',
            'frame rate', 'optimization', 'texture', 'rendering', 'technical'
        ],
        'Relaxing': [
            'atmosphere', 'immersive', 'beautiful', 'peaceful', 'relaxing',
            'ambient', 'environment', 'mood', 'aesthetic', 'experience'
        ]
    }

    def calculate_category_score(text, keywords):
        """Calculate how well a text matches a category's keywords"""
        text = text.lower()
        score = 0
        for keyword in keywords:
            # Count occurrences and weight them
            count = text.count(keyword.lower())
            if count > 0:
                # Add extra weight for keyword appearances in title
                score += count * (3 if keyword in text[:100] else 1)
        return score

    # Initialize results dictionary
    clustered_results = defaultdict(list)
    
    # Process each document
    for doc in docs:
        content = f"{doc.get('Title', '')} {doc.get('Content', '')}"
        
        # Calculate scores for each category
        category_scores = {}
        for category, keywords in categories.items():
            score = calculate_category_score(content, keywords)
            category_scores[category] = score
        
        # Assign document to highest scoring category
        # Only if the score is above a threshold
        max_category = max(category_scores.items(), key=lambda x: x[1])
        if max_category[1] > 2:  # Minimum threshold to be included in a category
            clustered_results[max_category[0]].append(doc)
        else:
            # Create a "Mixed" category for documents that don't strongly match any category
            clustered_results['Other Games'].append(doc)
    
    # Remove empty categories and sort by number of documents
    clustered_results = {k: v for k, v in clustered_results.items() if v}
    
    # Sort documents within each cluster by Score
    for category in clustered_results:
        clustered_results[category].sort(key=lambda x: float(x.get('Score', 0)), reverse=True)
    
    # Create labels dictionary
    cluster_labels = {category: category for category in clustered_results.keys()}
    
    return dict(clustered_results), cluster_labels

if __name__ == '__main__':
    app.run(debug=True, port=5000)