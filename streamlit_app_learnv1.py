import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

# Function to plot numerical data
def plot_numerical_data(df, col, plot_type):
    st.write(f"### {plot_type.capitalize()} Plot for {col}")
    fig, ax = plt.subplots()
    if plot_type == "box plot":
        sns.boxplot(df[col], ax=ax)
    elif plot_type == "line plot":
        sns.lineplot(data=df, x=df.index, y=col, ax=ax)
    elif plot_type == "violin plot":
        sns.violinplot(df[col], ax=ax)
    st.pyplot(fig)
    return fig

# Function to plot categorical data
def plot_categorical_data(df, col):
    st.write(f"### Frequency Plot for {col}")
    fig, ax = plt.subplots()
    sns.countplot(y=df[col], ax=ax)
    st.pyplot(fig)
    return fig

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

# Function to create an Excel file with results and plots
def create_excel(df, plots):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)
        for i, (col, fig) in enumerate(plots.items()):
            fig.savefig(f"{col}_plot.png")
            worksheet = writer.book.add_worksheet(f"{col}_plot")
            worksheet.insert_image('A1', f"{col}_plot.png")
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

            # Plotting options
            plots = {}
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=["object"]).columns

            if len(numerical_cols) > 0:
                st.write("### Plotting Options for Numerical Columns")
                selected_num_col = st.selectbox("Select a numerical column to plot:", numerical_cols)
                plot_type = st.selectbox("Select plot type:", ["box plot", "line plot", "violin plot"])
                if st.button("Plot"):
                    fig = plot_numerical_data(df, selected_num_col, plot_type)
                    plots[selected_num_col] = fig

            if len(categorical_cols) > 0:
                st.write("### Plotting Options for Categorical Columns")
                selected_cat_col = st.selectbox("Select a categorical column to plot:", categorical_cols)
                if st.button("Plot Frequency"):
                    fig = plot_categorical_data(df, selected_cat_col)
                    plots[selected_cat_col] = fig

            # Download option
            if len(plots) > 0:
                st.write("### Download Results and Plots")
                if st.button("Download Excel"):
                    excel_file = create_excel(df, plots)
                    st.download_button(
                        label="Download Excel",
                        data=excel_file,
                        file_name="analysis_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

if __name__ == "__main__":
    main()
