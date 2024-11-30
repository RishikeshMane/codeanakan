import streamlit as st
import pandas as pd
from openai import OpenAI

import os
import json

# Set Streamlit page configuration
st.set_page_config(
    page_title="Fashion Sales Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# Load data from the uploaded files
@st.cache
def load_data():
    purchase_data = pd.read_excel('https://etlcno01.blob.core.windows.net/client3input/ankan/cleaned_purchase_data.xlsx?sp=r&st=2024-11-30T14:47:21Z&se=2024-11-30T22:47:21Z&sv=2022-11-02&sr=b&sig=oXo35sHvOjDDZsVOpKoR6D0ws4gGEKOAVuk17xx2B4Q%3D')
    sales_data = pd.read_excel('https://etlcno01.blob.core.windows.net/client3input/ankan/cleaned_sales_data.xlsx?sp=racwdy&st=2024-11-30T14:43:37Z&se=2024-11-30T22:43:37Z&sv=2022-11-02&sr=b&sig=uYg9DGX8BaZtMrJy1HaaxDE0LHJIy4fpPoObvpmHAB0%3D')
    stock_data = pd.read_excel('https://etlcno01.blob.core.windows.net/client3input/ankan/cleaned_stock_data.xlsx?sp=r&st=2024-11-30T14:45:03Z&se=2024-11-30T22:45:03Z&sv=2022-11-02&sr=b&sig=OXeaudoxqEDg%2F95oob%2FPsSxGMB7tiPFjweDINbYP9As%3D')
    
    # Extract Month_Name from 'Entry Date'
    if 'Entry Date' in sales_data.columns:
        sales_data['Month'] = pd.to_datetime(sales_data['Entry Date']).dt.strftime('%B')
        sales_data['Entry Date'] = pd.to_datetime(sales_data['Entry Date']).astype(str)
    
    # Ensure 'Quantity In Stock' column exists
    if 'Quantity In Stock' not in stock_data.columns:
        stock_data['Quantity In Stock'] = 0
    
    return purchase_data, sales_data, stock_data

purchase_data, sales_data, stock_data = load_data()

# Set up OpenAI API key manually (you can replace '<YOUR_API_KEY>' with your actual key or set it as an environment variable)
  # Replace with your OpenAI API key or set it as an environment variable

# Sidebar for navigation
st.sidebar.title("Navigation")
pages = {
    "Sales Dashboard": "dashboard",
    "Inventory Management": "inventory",
    "Executive Insights": "insights"
}
page = st.sidebar.radio("Go to", list(pages.keys()))

# Define each page function
def sales_dashboard():
    st.title("📈 Sales Dashboard")
    st.markdown("### Analyze sales trends and performance metrics.")

    # Filter data
    if not sales_data.empty:
        marketing_group = st.sidebar.selectbox("Select Marketing Group", sales_data['Marketing Group'].dropna().astype(str).unique())
        category = st.sidebar.selectbox("Select Category", sales_data['Category'].dropna().astype(str).unique())
        filtered_data = sales_data[
            (sales_data['Marketing Group'] == marketing_group) &
            (sales_data['Category'] == category)
        ]
        st.dataframe(filtered_data)

        # Sales Trend Analysis
        st.subheader("Sales Trend Analysis")
        if not filtered_data.empty:
            monthly_sales = filtered_data.groupby(['Month', 'Brand'])['Qty(Unit1)'].sum().reset_index()
            if not monthly_sales.empty:
                monthly_sales_pivot = monthly_sales.pivot(index='Month', columns='Brand', values='Qty(Unit1)').fillna(0)
                st.line_chart(monthly_sales_pivot)

                # Pass sales_data to OpenAI API for analysis
                try:
                    sales_data_json = sales_data.to_dict(orient='records')
                    sales_data_str = json.dumps(sales_data_json)

                    prompt = (
                        "This is data from a fashion retail store which has purchase, sales, and stocks datasets. "
                        "Below is a JSON representation of sales data. "
                        "As a retail expert, analyze the data and provide insights on trends, performance, and opportunities for improvement. "
                        "Your response should include specific brand names and actionable insights based on the monthly quantities.\n\n"
                        f"Sales Data JSON:\n{sales_data_str}"
                    )

                    response = client.chat.completions.create(model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300)
                    st.subheader("AI-Powered Insights from Sales Data")
                    st.text(response['choices'][0]['message']['content'].strip())
                except Exception as e:
                    st.error(f"Error generating AI insights: {e}")
            else:
                st.write("No data available for the selected filters.")
        else:
            st.write("No data available for the selected filters.")
    else:
        st.write("No sales data available.")

def inventory_management():
    st.title("📦 Inventory Management")
    st.markdown("### Monitor stock levels and inventory turnover.")
    
    # Display stock data
    st.subheader("Inventory Overview")
    st.dataframe(stock_data)

    # Stock-Out Alerts
    st.subheader("Stock-Out Summary by Category")
    stock_summary = stock_data.groupby(['Category', 'Brand'])['Quantity In Stock'].sum().reset_index()
    st.table(stock_summary)

def executive_insights():
    st.title("💡 Executive Insights")
    st.markdown("### Gain insights and recommendations powered by AI.")
    
    # Get sales and inventory data
    try:
        sales_data['Entry Date'] = pd.to_datetime(sales_data['Entry Date']).astype(str)  # Convert Timestamps to strings
        sales_data_json = sales_data.to_dict(orient='records')
        inventory_data_json = stock_data.to_dict(orient='records')
        sales_data_str = json.dumps(sales_data_json)
        inventory_data_str = json.dumps(inventory_data_json)

        prompt = (
            "This is data from a fashion retail store which has purchase, sales, and stocks datasets. "
            "Below are JSON representations of sales and inventory data. "
            "As a retail expert, analyze the data and provide detailed insights on trends, performance, stock levels, and opportunities for improvement. "
            "Your response should include specific brand names, categories mentioned in the data, and actionable insights based on the quantities.\n\n"
            f"Sales Data JSON:\n{sales_data_str}\n\nInventory Data JSON:\n{inventory_data_str}"
        )

        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500)
        st.subheader("AI-Powered Insights from Sales and Inventory Data")
        st.text(response['choices'][0]['message']['content'].strip())
    except Exception as e:
        st.error(f"Error generating insight: {e}")

# Page routing
if page == "Sales Dashboard":
    sales_dashboard()
elif page == "Inventory Management":
    inventory_management()
elif page == "Executive Insights":
    executive_insights()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("This is a multi-page Streamlit application for fashion sales analytics using uploaded data.")
