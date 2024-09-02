import csv

def print_csv_headers(input_csv):
    # Read the CSV file and print the headers
    with open(input_csv, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        
        # Print the header row to check the column names
        headers = csv_reader.fieldnames
        print("CSV Headers:", headers)  # Debugging: prints the actual headers

if __name__ == "__main__":
    # Specify your CSV file here
    input_csv = 'sorted_items_final.csv'  # Replace with your CSV file path
    
    print_csv_headers(input_csv)
