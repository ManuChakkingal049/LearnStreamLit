import streamlit as st
import pandas as pd

# File uploader
st.title("CSV Data Analysis App")
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

# Check if file is uploaded
if uploaded_file is not None:
    # Read CSV file
    df = pd.read_csv(uploaded_file)

    # Display column names
    st.write("Available Columns:", list(df.columns))

    # Stress Test Name (ST1)
    stress_test_name = st.text_input("Enter Stress Test Name (e.g., ST1)")

    if stress_test_name == "ST1":
        # Select Segment and Stage columns
        segment_col = st.selectbox("Select Segment column", options=df.columns)
        stage_col = st.selectbox("Select Stage column", options=df.columns)

        # Select EAD, ECL baseline, ECL upturn, and ECL downturn columns
        ead_col = st.selectbox("Select EAD column", options=df.columns)
        ecl_baseline_col = st.selectbox("Select ECL Baseline column", options=df.columns)
        ecl_upturn_col = st.selectbox("Select ECL Upturn column", options=df.columns)
        ecl_downturn_col = st.selectbox("Select ECL Downturn column", options=df.columns)

        # Select run condition (Normal, Medium, Severe)
        run_condition = st.selectbox(
            "Select Run Condition",
            options=["Normal", "Medium", "Severe"],
            help="Choose the stress testing scenario."
        )

        # Define default weights based on the run condition
        if run_condition == "Normal":
            weights = {"Baseline": 40, "Upturn": 30, "Downturn": 30}
        elif run_condition == "Medium":
            weights = {"Baseline": 40, "Upturn": 25, "Downturn": 35}
        elif run_condition == "Severe":
            weights = {"Baseline": 40, "Upturn": 10, "Downturn": 50}

        # Display default weights
        st.write(f"Default Weights for {run_condition}:")
        st.write(f"Baseline: {weights['Baseline']}%, Upturn: {weights['Upturn']}%, Downturn: {weights['Downturn']}%")

        # Option to modify the weights
        modify_weights = st.checkbox("Modify Weights?")
        if modify_weights:
            weights["Baseline"] = st.number_input("Baseline Weight", min_value=0, max_value=100, value=weights["Baseline"])
            weights["Upturn"] = st.number_input("Upturn Weight", min_value=0, max_value=100, value=weights["Upturn"])
            weights["Downturn"] = st.number_input("Downturn Weight", min_value=0, max_value=100, value=weights["Downturn"])

        # Process and display results after grouping
        if segment_col and stage_col and ead_col and ecl_baseline_col and ecl_upturn_col and ecl_downturn_col:
            try:
                # Group by Segment and Stage columns
                grouped_data = df.groupby([segment_col, stage_col])[[ead_col, ecl_baseline_col, ecl_upturn_col, ecl_downturn_col]].sum().reset_index()

                # Calculate total ECL per group
                grouped_data['Total ECL'] = (
                    (grouped_data[ecl_baseline_col] * weights["Baseline"] / 100) +
                    (grouped_data[ecl_upturn_col] * weights["Upturn"] / 100) +
                    (grouped_data[ecl_downturn_col] * weights["Downturn"] / 100)
                )

                # Display results
                st.write("Grouped and Aggregated Data:")
                st.dataframe(grouped_data)

                # Calculate and display totals
                st.write("Totals:")
                totals = grouped_data[['Total ECL']].sum()
                total_df = pd.DataFrame(totals).T
                total_df.index = ['Total']
                st.dataframe(total_df)

                # Optional: Display grand total
                grand_total = totals.sum()
                st.write(f"Grand Total (sum of Total ECL): {grand_total}")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a valid Stress Test Name (e.g., ST1)")

# Add some basic information
st.sidebar.title("About")
st.sidebar.info("This app allows you to upload a CSV file, perform grouping and aggregation operations on the data, and calculate ECL under different stress test scenarios.")
