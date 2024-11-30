import pandas as pd

# Load the uploaded files
sales_file_path = 'sales.xls'
purchase_file_path = 'purchase.xls'
stock_file_path = 'stock.xls'

# Load each file into a DataFrame, handling different file types with error handling
def load_and_clean_data(file_path):
    try:
        data = pd.read_excel(file_path, engine='xlrd')
        # Start checking for the value "Entry No." in column A and "Entry Date" in column B, and remove rows until both are found in the same row
        for index in range(len(data)):  # Start from the first row (0-based index)
            if data.iloc[index, 0] == "Entry No." and data.iloc[index, 1] == "Entry Date":  # Check if column A (index 0) has value "Entry No." and column B (index 1) has value "Entry Date"
                data = data.iloc[index:].reset_index(drop=True)  # Keep rows from the row containing both "Entry No." and "Entry Date"
                break
        # Drop rows with all values as NaN or named "Unnamed"
        data = data.dropna(axis=0, how='all').reset_index(drop=True)  # Drop rows with all NaN values and reset index
        # Remove the first row if it contains "Manuhar Amber Sadan" in column A
        if data.iloc[0, 0] == "Manuhar Amber Sadan":
            data = data.iloc[1:].reset_index(drop=True)
        # Remove all blank, null, or unnamed values in column B
        data = data[data.iloc[:, 1].notna()]  # Keep rows where column B is not NaN
        data = data[data.iloc[:, 1] != '']  # Remove rows where column B is an empty string
        data = data[~data.iloc[:, 1].astype(str).str.contains('^Unnamed', na=False)]  # Remove rows where column B contains 'Unnamed'
        data = data.reset_index(drop=True)  # Reset index after filtering
        return data
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return None

# Load and clean each dataset
sales_data = load_and_clean_data(sales_file_path)
purchase_data = load_and_clean_data(purchase_file_path)
stock_data = load_and_clean_data(stock_file_path)

# Clean the Sales Data if loaded successfully
if sales_data is not None:
    sales_data = sales_data.reset_index(drop=True)
    sales_data = sales_data.dropna(how='all')  # Drop rows with all missing values

# Clean the Purchase Data if loaded successfully
if purchase_data is not None:
    purchase_data = purchase_data.reset_index(drop=True)
    purchase_data = purchase_data.dropna(how='all')  # Drop rows with all missing values

# Clean the Stock Data if loaded successfully
if stock_data is not None:
    stock_data = stock_data.reset_index(drop=True)
    stock_data = stock_data.dropna(how='all')  # Drop rows with all missing values

# Display each cleaned DataFrame to the user
if sales_data is not None:
    print("Cleaned Sales Data:")
    print(sales_data.head())
if purchase_data is not None:
    print("Cleaned Purchase Data:")
    print(purchase_data.head())
if stock_data is not None:
    print("Cleaned Stock Data:")
    print(stock_data.head())