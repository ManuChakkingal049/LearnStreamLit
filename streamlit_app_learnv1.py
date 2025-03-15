import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

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
    for col in df.columns:
        current_dtype = str(dtypes[col])
        new_dtype = st.selectbox(
            f"Change '{col}' from {current_dtype} to:",
            ["object", "int64", "float64", "datetime64[ns]"],
            index=["object", "int64", "float64", "datetime64[ns]"].index(current_dtype),
            key=f"dtype_{col}"
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

# Function to create an Excel file with results
def create_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)
    output.seek(0)
    return output

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

            # Download option
            st.write("### Download Modified Data")
            if st.button("Download Excel"):
                excel_file = create_excel(df)
                st.download_button(
                    label="Download Excel",
                    data=excel_file,
                    file_name="modified_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()
