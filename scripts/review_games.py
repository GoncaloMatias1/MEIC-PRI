import json

def main():
    # Load results
    with open('potential_relaxing.json', 'r') as f:
        data = json.load(f)
    
    docs = data['response']['docs']
    print(f"Found {len(docs)} potential relaxing games")
    
    relevant_ids = []
    
    # Review each game
    for doc in docs:
        print(f"\nTitle: {doc['Title']}")
        print("Content preview:", doc['Content'][:200], "...")
        
        choice = input("\nIs this a relaxing game? (y/n/q to quit): ").lower()
        if choice == 'q':
            break
        if choice == 'y':
            relevant_ids.append(doc['id'])
    
    # Save qrels in TREC format
    with open('queries/relaxing/qrels.txt', 'w') as f:
        for doc_id in relevant_ids:
            f.write(f"0 0 {doc_id} 1\n")
    
    print(f"\nSaved {len(relevant_ids)} relevant games to qrels.txt")

if __name__ == "__main__":
    main()