import pandas as pd

# Step 1: Load the Excel file
xlsx_file = 'updated_nationalities.xlsx'  # Replace with your actual XLSX file path
df = pd.read_excel(xlsx_file)

# Step 2: Define a function to clean up the values in the fifth column
def clean_column_value(value):
    if isinstance(value, str):  # Check if the value is a string
        # Split the string by " ~ " and filter out empty values
        parts = [part.strip() for part in value.split("~") if part.strip()]
        # Join the non-empty parts back together with " ~ "
        return " ~ ".join(parts)
    else:
        # If it's not a string (e.g., NaN or other), return the value as is (likely empty)
        return ''

# Step 3: Apply the function to the fifth column (assuming it's column index 4)
df.iloc[:, 4] = df.iloc[:, 4].apply(clean_column_value)

# Step 4: Save the modified DataFrame back to a new Excel file
output_file = 'cleaned_up.xlsx'
df.to_excel(output_file, index=False)

print(f"Cleaned Excel file saved to {output_file}")
