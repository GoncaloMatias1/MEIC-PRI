import csv
import json
from pathlib import Path

def csv_to_json(csv_path, json_path):
    """
    Convert a CSV file to JSON format
    
    Args:
        csv_path (str): Path to the input CSV file
        json_path (str): Path to save the output JSON file
    """
    # List to store all rows
    data = []
    
    # Read CSV file
    try:
        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            # Create CSV reader object
            csv_reader = csv.DictReader(csv_file)
            
            # Convert each row to dict and append to data list
            for row in csv_reader:
                data.append(row)
                
        # Write to JSON file
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
            
        print(f"Successfully converted {csv_path} to {json_path}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    # Define paths
    base_dir = Path(__file__).parent.parent  # Get project root directory
    csv_file = base_dir /"Project" / "src" / "webscrapper_out" / "ign.csv"
    json_file = base_dir / "csv_to_json" / "ign.json"
    
    # Create output directory if it doesn't exist
    json_file.parent.mkdir(exist_ok=True)
    
    # Convert CSV to JSON
    csv_to_json(csv_file, json_file)

if __name__ == "__main__":
    main()