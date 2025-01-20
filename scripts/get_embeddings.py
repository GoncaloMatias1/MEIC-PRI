import sys
import json
import re
from sentence_transformers import SentenceTransformer

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """Generate embedding for given text"""
    return model.encode(text, convert_to_tensor=False).tolist()

def split_content_into_paragraphs(content):
    """Split content into paragraphs using multiple possible delimiters"""
    # Remove any excessive whitespace first
    content = ' '.join(content.split())
    
    # Try various ways to split into paragraphs
    # 1. Split on periods followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    # Group sentences into paragraphs (e.g., 3-4 sentences per paragraph)
    paragraphs = []
    current_paragraph = []
    for sentence in sentences:
        current_paragraph.append(sentence)
        # Create a new paragraph after every 3 sentences or if sentence is very long
        if len(current_paragraph) >= 3 or len(''.join(current_paragraph)) > 500:
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []
    
    # Add any remaining sentences as the last paragraph
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    
    return paragraphs

if __name__ == "__main__":
    # Read JSON from STDIN
    data = json.load(sys.stdin)
    processed_data = []
    
    # Process each document
    for document in data:
        # Split content into paragraphs
        paragraphs = split_content_into_paragraphs(document['Content'])
        
        # Create a document for each paragraph
        for i, paragraph in enumerate(paragraphs):
            # Skip empty paragraphs
            if not paragraph.strip():
                continue
                
            # Create combined text for embedding
            combined_text = f"{document['Title']} {document.get('Subtitle', '')} {paragraph}"
            
            # Create new document
            new_doc = {
                'id': f"{document['id']}_{i}",  # Unique ID for each paragraph
                'parent_id': document['id'],     # Original document ID
                'Title': document['Title'],
                'Subtitle': document.get('Subtitle', ''),
                'Score': document.get('Score', 0.0),
                'Content': paragraph,            # Store just the paragraph
                'paragraph_num': i,              # Keep track of paragraph order
                'vector': get_embedding(combined_text)
            }
            processed_data.append(new_doc)
    
    # Output updated JSON to STDOUT
    json.dump(processed_data, sys.stdout, indent=2, ensure_ascii=False)