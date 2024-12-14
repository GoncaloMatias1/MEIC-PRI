from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from collections import defaultdict
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from sentence_transformers import SentenceTransformer

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

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        query = data.get('query', '')
        search_type = data.get('searchType', 'boosted')
        category = data.get('category', 'all')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
            
        # Get appropriate core name
        core = CORES.get(search_type, CORES['boosted'])
        
        # Construct Solr query based on search type
        solr_query = construct_solr_query(query, search_type, category)
        
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

def construct_solr_query(query, search_type, category):
    """Construct appropriate Solr query based on search parameters"""
    base_query = {
        "params": {
            "fl": "id,Title,Content,Score,Subtitle,Subheader",
            "rows": 30
        }
    }
    
    if search_type == 'semantic':
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_vector = model.encode(query, convert_to_tensor=False).tolist()
        
        base_query["params"].update({
            "q": "{!knn f=vector topK=50}" + str(query_vector),
            "rows": 30
        })
    else:  # boosted
        # Clean and prepare the query
        clean_query = query.strip()
        terms = clean_query.split()
        
        if len(terms) > 1:
            # For multi-word queries (like game titles), prioritize exact matches
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
            # For single-word queries
            base_query["params"].update({
                "defType": "edismax",
                "q": f"Title:({clean_query})^5 OR Content:({clean_query})^3",
                "qf": "Title^4 Content^2 Subtitle",
                "mm": "100%"
            })

        # Add category-specific boosts if category is not 'all'
        if category != 'all':
            base_query["params"]["bq"] = f"Content:({category})^2"
    
    return base_query

def cluster_results(docs, num_clusters=3):
    if not docs:
        return {}, {}
        
    try:
        # Create TF-IDF matrix
        vectorizer = TfidfVectorizer(stop_words='english')
        contents = [doc.get('Content', '') for doc in docs]
        tfidf_matrix = vectorizer.fit_transform(contents)
        
        # Perform clustering
        n_clusters = min(num_clusters, len(docs))
        kmeans = KMeans(n_clusters=n_clusters)
        clusters = kmeans.fit_predict(tfidf_matrix)
        
        # Group documents by cluster
        clustered_results = defaultdict(list)
        for doc, cluster_id in zip(docs, clusters):
            clustered_results[int(cluster_id)].append(doc)
        
        # Generate cluster labels
        cluster_labels = {}
        feature_names = vectorizer.get_feature_names_out()
        for cluster_id, cluster_center in enumerate(kmeans.cluster_centers_):
            top_terms_idx = cluster_center.argsort()[-3:][::-1]
            top_terms = [feature_names[idx] for idx in top_terms_idx]
            cluster_labels[cluster_id] = ", ".join(top_terms)
        
        return dict(clustered_results), cluster_labels
    except Exception as e:
        app.logger.error(f"Clustering error: {str(e)}")
        return {'0': docs}, {'0': 'All Results'}

if __name__ == '__main__':
    app.run(debug=True, port=5000)