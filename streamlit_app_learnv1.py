import streamlit as st
import pandas as pd
import numpy as np

# Function to load data
def load_data(file):
    if file is not None:
        try:
            df = pd.read_csv(file)
        except Exception as e:
            st.error(f"Error: {e}")
            return None
        return df
    return None

# Function to detect and display data types with option to change
def detect_and_display_dtypes(df):
    st.write("### Detected Data Types")
    dtypes = df.dtypes
    dtype_changes = {}  # Store changes to data types

    # Display data types and provide options to change
    for col in df.columns:
        current_dtype = str(dtypes[col])
        new_dtype = st.selectbox(
            f"Change '{col}' from {current_dtype} to:",
            ["object", "int64", "float64", "datetime64[ns]"],
            index=["object", "int64", "float64", "datetime64[ns]"].index(current_dtype),
            key=f"dtype_{col}"
        )
        if new_dtype != current_dtype:
            dtype_changes[col] = new_dtype

    # Apply changes to data types
    for col, new_dtype in dtype_changes.items():
        try:
            if new_dtype == "datetime64[ns]":
                df[col] = pd.to_datetime(df[col], errors='coerce')
            else:
                df[col] = df[col].astype(new_dtype)
        except Exception as e:
            st.error(f"Error converting {col} to {new_dtype}: {e}")

    return df

# Function to calculate statistics
def calculate_statistics(df):
    st.write("### Statistics for Numerical Variables")
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    if len(numerical_cols) > 0:
        st.write(df[numerical_cols].describe())
    else:
        st.write("No numerical columns found.")

    st.write("### Frequency for Categorical Variables")
    categorical_cols = df.select_dtypes(include=["object"]).columns
    if len(categorical_cols) > 0:
        for col in categorical_cols:
            st.write(f"Frequency for {col}:")
            st.write(df[col].value_counts())
    else:
        st.write("No categorical columns found.")

    st.write("### Min and Max Dates")
    date_cols = df.select_dtypes(include=["datetime64[ns]"]).columns
    if len(date_cols) > 0:
        for col in date_cols:
            st.write(f"Min and Max dates for {col}:")
            st.write(f"Min: {df[col].min()}, Max: {df[col].max()}")
    else:
        st.write("No date columns found.")

# Function to plot data using Streamlit's built-in functions
def plot_data(df):
    st.write("### Data Visualization")

    # Plot numerical columns
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    if len(numerical_cols) > 0:
        st.write("#### Numerical Columns")
        selected_num_col = st.selectbox("Select a numerical column to plot:", numerical_cols)
        st.line_chart(df[selected_num_col])

    # Plot categorical columns
    categorical_cols = df.select_dtypes(include=["object"]).columns
    if len(categorical_cols) > 0:
        st.write("#### Categorical Columns")
        selected_cat_col = st.selectbox("Select a categorical column to plot:", categorical_cols)
        st.bar_chart(df[selected_cat_col].value_counts())

# Main function
def main():
    st.title("Data Analysis with Streamlit")
    
    # Upload file
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if df is not None:
            st.write("### Loaded Data")
            st.write(df.head())
            
            # Detect and display data types with option to change
            df = detect_and_display_dtypes(df)
            
            # Calculate statistics
            calculate_statistics(df)

            # Plot data
            plot_data(df)

if __name__ == "__main__":
    main()
