import streamlit as st
import pandas as pd

# File uploader
st.title("CSV Data Analysis App")
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

if uploaded_file is not None:
    # Read CSV file
    df = pd.read_csv(uploaded_file)
    
    # Display column names
    st.write("Available Columns:", list(df.columns))
    
    # Select columns for grouping
    group_cols = st.multiselect(
        "Select columns to group by",
        options=df.columns,
        help="Choose one or more columns to group the data"
    )
    
    # Select columns for aggregation
    agg_cols = st.multiselect(
        "Select columns to aggregate (sum)",
        options=[col for col in df.columns if col not in group_cols and df[col].dtype in ['int64', 'float64']],
        help="Choose numeric columns to sum"
    )
    
    # Process and display results
    if group_cols and agg_cols:
        try:
            # Perform grouping and aggregation
            result = df.groupby(group_cols)[agg_cols].sum().reset_index()
            
            # Display results
            st.write("Grouped and Aggregated Data:")
            st.dataframe(result)
            
            # Calculate and display totals
            if agg_cols:
                st.write("Totals:")
                totals = result[agg_cols].sum()
                total_df = pd.DataFrame(totals).T
                total_df.index = ['Total']
                st.dataframe(total_df)
                
                # Optional: Display grand total if multiple aggregation columns
                if len(agg_cols) > 1:
                    grand_total = totals.sum()
                    st.write(f"Grand Total (sum of all aggregated columns): {grand_total}")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please select at least one column for grouping and one column for aggregation")

# Add some basic information
st.sidebar.title("About")
st.sidebar.info("This app allows you to upload a CSV file and perform grouping and aggregation operations on the data.")
