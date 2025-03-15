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

# Function to detect and display data types
def detect_and_display_dtypes(df):
    st.write("### Detected Data Types")
    dtypes = df.dtypes
    st.write(dtypes)
    return dtypes

# Function to allow changing data types
def change_dtypes(df, dtypes):
    st.write("### Change Data Types")
    for col in df.columns:
        current_dtype = str(dtypes[col])
        new_dtype = st.selectbox(
            f"Change '{col}' from {current_dtype} to:",
            ["object", "int64", "float64", "datetime64[ns]"],
            key=col
        )
        if new_dtype != current_dtype:
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
            
            # Detect and display data types
            dtypes = detect_and_display_dtypes(df)
            
            # Allow changing data types
            df = change_dtypes(df, dtypes)
            
            # Calculate statistics
            calculate_statistics(df)

if __name__ == "__main__":
    main()
