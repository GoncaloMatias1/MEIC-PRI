import json
import sys
import requests
from tqdm import tqdm

def index_in_chunks(input_file, solr_url, chunk_size=1000):
    """Index documents to Solr in chunks"""
    # Read the full JSON file
    print(f"Loading JSON from {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    total_docs = len(data)
    print(f"Total documents to index: {total_docs}")
    
    # Process in chunks
    for i in tqdm(range(0, total_docs, chunk_size)):
        chunk = data[i:i + chunk_size]
        
        try:
            # Send chunk to Solr
            response = requests.post(
                f"{solr_url}/update?commit=true",
                json=chunk,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error indexing chunk {i//chunk_size}: {str(e)}")
            continue
            
    print("Indexing complete!")

if __name__ == "__main__":
    solr_url = "http://localhost:8983/solr/ign_semantic"
    input_file = "data/ign_semantic.json"
    
    index_in_chunks(input_file, solr_url)