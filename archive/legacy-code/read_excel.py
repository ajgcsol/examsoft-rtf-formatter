import pandas as pd

# Read the Excel file
df = pd.read_excel('Final SU2025 Excel MC Answers.xlsx')
print("Answer key contents:")
print(df.head(10))
print(f"\nShape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
