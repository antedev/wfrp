import csv
import json

# Specify the input CSV file and output JSON file
csv_file = 'creature_traits.csv'
json_file = 'creature_traits.json'

# Create an empty list to hold the JSON data
json_data = []

# Open the CSV file for reading
with open(csv_file, mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file, delimiter=';')  # Use ';' as the delimiter
    for row in csv_reader:
        # For each row, append it to the json_data list
        json_data.append({
            "Name": row["Name"],
            "Description": row["Description"]
        })

# Write the data to a JSON file
with open(json_file, mode='w', encoding='utf-8') as file:
    json.dump(json_data, file, indent=4, ensure_ascii=False)

print(f'CSV file {csv_file} has been converted to JSON and saved as {json_file}')
