import streamlit as st
import pandas as pd
from io import BytesIO
import numpy as np

st.set_page_config(page_title="Excel File Generator", layout="centered")
st.title("Excel File Generator for Data Cleaning Agent")

# Create a sample DataFrame with uncleaned data
data = {
    'InvoiceID': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    'CustomerID': ['A1', 'A2', 'A3', 'A4', 'A1', 'A5', 'A6', 'A7', 'A8', 'A9'],
    'ProductName': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Laptop', 'Webcam', 'Mouse', 'Keyboard', 'Tablet', 'Laptop'],
    'Price': [1200, 25, 75, np.nan, 1200, 45, 25, 75, 500, 1200],
    'Quantity': [1, 2, 1, 1, 1, 1, np.nan, 1, 2, 1],
    'OrderDate': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-01', '2023-01-05', '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09']
}
df = pd.DataFrame(data)

# Add some more uncleaned data
df.loc[6, 'Price'] = np.nan  # Another missing price
df.loc[9, 'ProductName'] = 'laptop' # Case inconsistency
df = pd.concat([df, pd.DataFrame({
    'InvoiceID': [111, 112],
    'CustomerID': ['A1', 'A10'],
    'ProductName': ['Headphones', 'Tablet'],
    'Price': [80, 500],
    'Quantity': [1, 2],
    'OrderDate': ['2023-01-10', '2023-01-11']
})], ignore_index=True)


# Save the DataFrame to a BytesIO object
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')
excel_data = output.getvalue()

st.markdown("""
This is a sample Excel file (`uncleaned_sales_data.xlsx`) that contains several common data cleaning issues:
- **Missing values:** In the `Price` and `Quantity` columns.
- **Duplicate rows:** Rows with `InvoiceID` 101 and 105 are exact duplicates.
- **Case inconsistency:** "Laptop" vs. "laptop" in the `ProductName` column.
- **Potential duplicates based on key columns:** `CustomerID` 'A1' appears multiple times with different products, which may be a duplicate record or a valid repeat customer.

You can use this file to test the AI agent from the previous response.
""")

st.download_button(
    label="📥 Download Uncleaned Excel File",
    data=excel_data,
    file_name="uncleaned_sales_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)