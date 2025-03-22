import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

# Load the CSV file into a DataFrame
def load_data(file_path):
    return pd.read_csv(file_path)

# Convert string to date
def convert_to_date(date_string):
    return datetime.strptime(date_string, "%d-%b-%Y")

# Calculate years since NPL
def calculate_years_since_npl(classification_date, run_date):
    return (run_date - classification_date).days / 365

# Main calculation function
def calculate_provisions(df, crms_issue_date_str, run_date_str):
    # Convert date columns to datetime objects
    crms_issue_date = convert_to_date(crms_issue_date_str)
    run_date = convert_to_date(run_date_str)
    
    # Calculate the years since NPL
    df['Classification Date'] = pd.to_datetime(df['Classification date'], errors='coerce')
    df['Years Since NPL'] = df['Classification Date'].apply(lambda x: calculate_years_since_npl(x, run_date))
    
    # Calculate Unsecured Portion
    df['Unsecured Portion (as whole)'] = df.apply(
        lambda row: max(row['TOTAL OS'] - row['Collateral after H.C'], 0), axis=1
    )
    
    # Calculate NET SECURED Portion
    df['NET SECURED Portion'] = df.apply(
        lambda row: min(row['Collateral after H.C'], row['TOTAL OS']), axis=1
    )
    
    # Calculate NET Unsecured Portion (NUSP)
    df['NET Unsecured Portion (NUSP)'] = df['Unsecured Portion (as whole)'] - df['Unsecured Portion Covered by ECF/DCF']
    
    # Calculate Min. Provision Required on NUSP (A)
    df['Min. Provision Required on NUSP (A)'] = df['NET Unsecured Portion (NUSP)']
    
    # Calculate Min. Provision Required on NUSP (B)
    four_years_after_crms = crms_issue_date + timedelta(days=4*365)  # Add 4 years to CRMS issue date
    df['Min. Provision Required on NUSP (B)'] = df.apply(
        lambda row: row['Unsecured Portion (as whole)'] * 1 if run_date >= four_years_after_crms else row['Unsecured Portion (as whole)'] * 0.25,
        axis=1
    )
    
    # Calculate final provision for Unsecured Portion
    df['Provision Unsecured Portion'] = df.apply(
        lambda row: max(row['Min. Provision Required on NUSP (A)'], row['Min. Provision Required on NUSP (B)']),
        axis=1
    )
    
    # Calculate Min. Provision on entire SECURED Portion
    df['Min. Provision on entire SECURED Portion'] = df.apply(
        lambda row: row['NET SECURED Portion'] * 0.25 if row['Years Since NPL'] > 4 else 0,
        axis=1
    )
    
    # Calculate FINAL Required Provision/ECL CRMS
    df['FINAL Required Provision/ECL CRMS'] = df['Provision Unsecured Portion'] + df['Min. Provision on entire SECURED Portion']
    
    # Calculate Final Calculated ECL with Q3 2024 floor
    df['Final Calculated ECL with Q3 2024 floor'] = df.apply(
        lambda row: max(row['FINAL Required Provision/ECL CRMS'], row['Existing ECL held Q3\'24']),
        axis=1
    )
    
    # Calculate ratio of Existing ECL Q3'24 to Total OS
    df['Ratio Existing ECL Q3\'24 to Total OS'] = df.apply(
        lambda row: row['Existing ECL held Q3\'24'] / row['TOTAL OS'] if row['TOTAL OS'] != 0 else 0,
        axis=1
    )
    
    # Calculate Final ECL with OS considered based on the updated condition
    df['Final ECL with OS considered'] = df.apply(
        lambda row: max(row['FINAL Required Provision/ECL CRMS'], row['TOTAL OS']) if row['Ratio Existing ECL Q3\'24 to Total OS'] > 1
        else max(row['FINAL Required Provision/ECL CRMS'], row['Existing ECL held Q3\'24']),
        axis=1
    )
    
    return df

# Streamlit app
def main():
    st.title("Provision Calculation App")

    # File upload
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        # Load the data
        df = pd.read_csv(uploaded_file)
        st.write("Data Preview:")
        st.write(df.head())

        # User inputs
        crms_issue_date_str = st.text_input("Enter CRMS Issue Date (DD-MMM-YYYY)", value="31-Oct-2024")
        run_date_str = st.text_input("Enter Run Date (DD-MMM-YYYY)", value="22-Mar-2025")

        # Button to perform calculation
        if st.button("Calculate Provisions"):
            # Ensure valid date format
            try:
                df_result = calculate_provisions(df, crms_issue_date_str, run_date_str)
                
                # Show the resulting dataframe
                st.write("Calculation Results:")
                st.write(df_result)

                # Download button for the result
                csv = df_result.to_csv(index=False)
                st.download_button(
                    label="Download Results",
                    data=csv,
                    file_name="calculated_provisions.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
