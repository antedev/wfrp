import csv
import json

def csv_to_json(input_csv, output_json):
    json_output = []
    
    # Read the CSV file
    with open(input_csv, mode='r', encoding='utf-8-sig') as csv_file:  # Use 'utf-8-sig' to automatically handle the BOM
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        
        # Process each row in the CSV
        for row in csv_reader:
            json_output.append({
                "Heading 1": row['Main heading'] + ":",
                "Heading 2": row['Sub heading'] + ":",
                "Item": row['Item'],
                "References": [f"Warhammer Fantasy Core Rule book.pdf#page={int(float(row['Page number']))}"]
            })
    
    # Write the JSON output to a file
    with open(output_json, 'w', encoding='utf-8') as json_file:
        json.dump(json_output, json_file, indent=4, ensure_ascii=False)
    
    print(f"JSON output has been saved to {output_json}")

if __name__ == "__main__":
    # Specify your CSV file and desired JSON output file here
    input_csv = 'sorted_items_final.csv'   # Replace with your CSV file path
    output_json = 'wfrp_core_rules_ref.json'  # Replace with your desired JSON output file path
    
    csv_to_json(input_csv, output_json)
