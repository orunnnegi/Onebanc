import csv
import re
from datetime import datetime
from transaction import process_transaction_file

VALID_COLUMNS = {"date", "name", "transaction description", "amount", "debit", "credit"}
FOREIGN_CURRENCIES = {"USD", "POUND", "EUR", "AUD", "CAD", "YEN", "CNY", "SGD", "CHF"}
EXCLUDE_WORDS = {"international transactions", "domestic transactions", "transaction description", "transaction details"}

def read_csv_as_matrix(file_path):
    matrix = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            matrix.append([cell.strip() if cell else "" for cell in row])
    return matrix

def clean_text(text):
    return re.sub(r"\s+", " ", text.strip())

def is_date(value):
    return bool(re.match(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})$", value))

def parse_date(value):
    try:
        return datetime.strptime(value, "%d-%m-%Y")
    except ValueError:
        try:
            return datetime.strptime(value, "%m/%d/%y")
        except ValueError:
            return None

def is_name(value, headers):
    if value.lower() in VALID_COLUMNS or value.replace(".", "").isdigit():
        return False
    return value.isalpha()

def is_transaction_description(value):
    if value.lower() in EXCLUDE_WORDS or re.match(r"^\d+(\.\d+)?\s*cr$", value.lower()):
        return False
    return len(value.split()) >= 2

def extract_transaction_details(transaction_description):
    words = transaction_description.split()
    if len(words) < 2:
        return "unknown", "Domestic", "INR"
    last_word, second_last_word = words[-1].upper(), words[-2].title()
    if last_word in FOREIGN_CURRENCIES:
        return second_last_word.lower(), "International", last_word
    else:
        return last_word.lower(), "Domestic", "INR"

def identify_and_store_details(matrix, debit_values, credit_values):
    transaction_data = []
    headers = {cell.lower(): idx for idx, cell in enumerate(matrix[0])}
    current_name = None
    debit_index, credit_index = 0, 0
    for row in matrix[1:]:
        row_data = {"Date": "", "Transaction Description": "", "Debit": 0.0, "Credit": 0.0, "Currency": "", "CardName": "", "Transaction": "", "Location": ""}
        date_found = False
        for idx, cell in enumerate(row):
            cleaned_cell = clean_text(cell)
            if not cleaned_cell:
                continue
            if is_transaction_description(cleaned_cell):
                row_data["Transaction Description"] = cleaned_cell
                location, transaction, currency = extract_transaction_details(cleaned_cell)
                row_data["Location"] = location
                row_data["Transaction"] = transaction
                row_data["Currency"] = currency
            elif is_date(cleaned_cell):
                row_data["Date"] = cleaned_cell
                row_data["CardName"] = current_name if current_name else "Unknown"
                date_found = True
            elif is_name(cleaned_cell, headers):
                current_name = cleaned_cell
        if date_found:
            if debit_index < len(debit_values):
                row_data["Debit"] = float(debit_values[debit_index])
                debit_index += 1
            if credit_index < len(credit_values):
                row_data["Credit"] = float(credit_values[credit_index])
                credit_index += 1
            if row_data["Date"] and row_data["Transaction Description"]:
                transaction_data.append(row_data)
    transaction_data.sort(key=lambda x: parse_date(x["Date"]) or datetime.min)
    return transaction_data

def print_table(data):
    headers = ["Date", "Transaction Description", "Debit", "Credit", "Currency", "CardName", "Transaction", "Location"]
    table_data = [[row[h] for h in headers] for row in data]
    from tabulate import tabulate
    print("\nExtracted Transaction Details (Sorted by Date):\n")
    print(tabulate(table_data, headers=headers, tablefmt="grid", floatfmt=".2f"))

def StandardizeStatement(inputFile, outputFile=None):
    if outputFile is None:
        outputFile = inputFile.replace("Input", "Output")
    debit_values, credit_values = process_transaction_file(inputFile)
    matrix = read_csv_as_matrix(inputFile)
    if not matrix:
        print("No data found in the file.")
        return
    transaction_data = identify_and_store_details(matrix, debit_values, credit_values)
    headers = ["Date", "Transaction Description", "Debit", "Credit", "Currency", "CardName", "Transaction", "Location"]
    with open(outputFile, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in transaction_data:
            d = parse_date(row["Date"])
            formatted_date = d.strftime("%d-%m-%Y") if d else row["Date"]
            row["Date"] = formatted_date
            writer.writerow([row[h] for h in headers])
    print(f"Processed file saved as '{outputFile}'")
    return outputFile

if __name__ == "__main__":
    in_file = input("Enter the input CSV file name (including .csv extension): ").strip()
    StandardizeStatement(in_file)
