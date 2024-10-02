import pandas as pd
import ast

# Step 1: Load the Excel file
xlsx_file = 'Complete Data.xlsx'  # Replace with your actual XLSX file path
df = pd.read_excel(xlsx_file)

# Step 2: Define a function to convert the list format to the desired string format
def format_nationality(nationality_str):
    try:
        # Convert string representation of list to a Python list
        nationalities = ast.literal_eval(nationality_str)
        # Join the list elements with " ~ "
        return " ~ ".join(nationalities)
    except (ValueError, SyntaxError):
        # In case it's not a list-like string, return it as is
        return nationality_str

# Step 3: Apply the conversion to the 'nationality' column
df['nationality'] = df['nationality'].apply(format_nationality)

# Step 4: Save the modified DataFrame back to a new Excel file
output_file = 'updated_nationalities.xlsx'
df.to_excel(output_file, index=False)

print(f"Updated Excel file saved to {output_file}")
