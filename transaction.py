import csv
import re

def read_csv_as_matrix(file_path):
    matrix = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            matrix.append([cell.strip() for cell in row])
    return matrix

def find_column_indices(matrix):
    amount_idx, debit_idx, credit_idx = None, None, None
    for row_idx, row in enumerate(matrix):
        for col_idx, cell in enumerate(row):
            lower_cell = cell.lower().strip()
            if lower_cell == "amount":
                amount_idx = col_idx
            elif lower_cell == "debit":
                debit_idx = col_idx
            elif lower_cell == "credit":
                credit_idx = col_idx
        if any(idx is not None for idx in [amount_idx, debit_idx, credit_idx]):
            return row_idx + 1, amount_idx, debit_idx, credit_idx
    return None, None, None, None

def is_valid_number(value):
    return bool(re.match(r"^\d+(\.\d+)?$", value))

def is_valid_amount(value):
    return bool(re.match(r"^\d+(\.\d+)?\s*(cr)?$", value.lower()))

def extract_column_values(matrix):
    start_row, amount_idx, debit_idx, credit_idx = find_column_indices(matrix)
    if start_row is None:
        print("No 'amount', 'debit', or 'credit' columns found.")
        return [], []
    debit_values, credit_values = [], []
    for row in matrix[start_row:]:
        row = [cell.strip() for cell in row]
        if not any(row):
            continue
        debit, credit = 0.0, 0.0
        if amount_idx is not None and amount_idx < len(row) and row[amount_idx]:
            value = row[amount_idx]
            if is_valid_amount(value):
                if "cr" in value.lower():
                    credit = float(re.sub(r"[^\d.]", "", value))
                    debit = 0.0
                else:
                    debit = float(value)
                    credit = 0.0
        if debit_idx is not None and debit_idx < len(row) and row[debit_idx]:
            value = row[debit_idx]
            if is_valid_number(value):
                debit = float(value)
        if credit_idx is not None and credit_idx < len(row) and row[credit_idx]:
            value = row[credit_idx]
            if is_valid_number(value):
                credit = float(value)
        if debit != 0.0 or credit != 0.0:
            debit_values.append(debit)
            credit_values.append(credit)
    return debit_values, credit_values

def process_transaction_file(input_file):
    try:
        matrix = read_csv_as_matrix(input_file)
        if not matrix:
            print("No data found in the file.")
            return [], []
        debit_values, credit_values = extract_column_values(matrix)
        print("Debit Column Values:")
        print(debit_values)
        print("Credit Column Values:")
        print(credit_values)
        print(f"Size of Debit Array: {len(debit_values)}")
        print(f"Size of Credit Array: {len(credit_values)}")
        return debit_values, credit_values
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' does not exist.")
        return [], []

if __name__ == "__main__":
    input_file = input("Enter the CSV file name (including .csv extension): ").strip()
    process_transaction_file(input_file)
