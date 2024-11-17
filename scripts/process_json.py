import json
import hashlib

def generate_consistent_id(title):
    """Gera um ID consistente baseado no título"""
    # Remove espaços extras e converte para minúsculas
    normalized_title = title.strip().lower()
    # Cria um hash do título
    return hashlib.md5(normalized_title.encode()).hexdigest()

def process_json_file():
    # Lê o arquivo JSON original
    with open('csv_to_json/ign_fixed.json', 'r') as f:
        data = json.load(f)
    
    # Processa cada documento
    for doc in data:
        # Gera ID consistente baseado no título
        doc['id'] = generate_consistent_id(doc['Title'])
    
    # Salva o novo JSON com IDs consistentes
    with open('csv_to_json/ign_processed.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    process_json_file()
    print("JSON processado com IDs consistentes!")