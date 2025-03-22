import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

# Write-up explaining the calculation
st.markdown("""
# Minimum Provision Calculation based on CRMS (CBUAE Guidelines)

This app calculates the minimum provision required for Stage 3 (Wholesale Obligors) under the CRMS guidelines published by the Central Bank of the UAE (CBUAE). The calculation follows the steps outlined in **Article 9.23 - Minimum provision for Stage 3 (Wholesale Obligors)**.

### Required Columns:
To perform the calculation, the following columns are required in your input data (CSV file):

1. **Classification Date**: 
   - This represents the classification date of the loan and serves as the **default classification date**.
   - It is used to determine the age of the loan (how long it has been classified) and helps in calculating the minimum provision.
   
2. **TOTAL OS** (Total Outstanding):
   - This represents the total outstanding loan amount.
   
3. **Collateral after H.C.** (Collateral after Haircut):
   - This represents the value of the collateral after applying a haircut, which reduces its value to account for risks like market fluctuations.
   
4. **Unsecured Portion Covered by ECF/DCF**:
   - This represents the portion of the unsecured loan that is covered by **Expected Cash Flows (ECF)** or **Discounted Cash Flows (DCF)**.
   
   
5. **Existing ECL held Q3'24**:
   - This represents the **Existing ECL held in Q3 2024**. 
   - It is used as input to ensure that no **ECL release** occurs solely due to the implementation of the new CRMS guidelines.
   - If the **outstanding loan (OS)** decreases or the **collateral value increases**, it might lead to a reduction in ECL. The **ECL from Q3 2024** acts as a safeguard to avoid any unintended ECL release.

### Input Data Format:
Below is the sample format for the input data that you should upload:
""")
# Use st.image() to display an image of the input data format
st.image("https://github.com/ManuChakkingal049/LearnStreamLit/blob/main/input_data_sample.png?raw=true", caption="Input Data Format Example")

st.markdown("""

### Key Steps:

1. **Unsecured Portion Calculation**: 
   - The **Unsecured Portion (as whole)** is calculated by subtracting the **Collateral after H.C.** (haircut) from the **TOTAL OS** (total outstanding loan). 
   - If this value is negative, it’s set to zero.

2. **Unsecured Portion Covered by ECF/DCF**:
   - This portion is subtracted from the unsecured portion to calculate the **NET Unsecured Portion (NUSP)**.
   - If part of the unsecured portion is covered by expected cash flows (ECF/DCF), that part does not require provision.

3. **Provision Calculation for Unsecured Portion**:
   - **Approach 1**: 
     - For loans that are **less than 4 years old**, a **25% provision** is applied to the **Unsecured Portion**.
     - For loans that are **older than 4 years**, a **100% provision** is applied to the **Unsecured Portion**.
     
   - **Approach 2**:
     - **No provision** is required for the portion of the unsecured loan that is **covered by expected cash flows (ECF/DCF)**.
     - **100% provision** is applied to the portion that is **not covered by expected cash flows**.

   - The final provision for the **Unsecured Portion** is the **maximum** of the provisions calculated from **Approach 1** and **Approach 2**.

4. **NET SECURED Portion Calculation**:
   - The **NET SECURED Portion** is the minimum value between the **Collateral after H.C.** and the **TOTAL OS** (outstanding loan).
   
5. **Provision for SECURED Portion**:
   - If the loan is **less than 4 years old**, **no provision** is required for the secured portion.
   - If the loan is **older than 4 years**, a **25% provision** is applied to the **NET SECURED Portion**.
   
6. **Final Required Provision/ECL**:
   - The **final provision required** is the sum of the **Provision for Unsecured Portion** and the **Provision for SECURED Portion**.

7. **Final ECL Calculation**:
   - The **Final Calculated ECL with Q3 2024 floor** compares the calculated provision with the **Existing ECL held Q3 2024** and ensures that the result is no less than the existing ECL.
   
8. **Final ECL with OS considered**:
   - If the **ratio of Existing ECL to Total OS** exceeds 1, the **Final ECL with OS considered** is calculated as the maximum between the calculated provision and the total outstanding loan.
   - Otherwise, it takes the maximum between the calculated provision and the existing ECL.

### How This App Works:
This app performs the above steps to calculate the **minimum provision required** for each loan in the uploaded dataset and provides the results, along with an option to download the updated data.

The app applies the CRMS guidelines for provision calculation and takes into account both the **age of the loan** (for unsecured and secured portions) and whether part of the unsecured portion is **covered by expected cash flows (ECF/DCF)**.

You can upload your dataset (CSV file format), enter the **CRMS Issue Date** and **Run Date**, and click "Calculate Provisions" to get the results.

---
The calculation logic is implemented using the following code.
""")

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
    
    # Fill missing values in key columns with 0 (or use other default values based on the use case)
    df['TOTAL OS'] = df['TOTAL OS'].fillna(0)
    df['Collateral after H.C'] = df['Collateral after H.C'].fillna(0)
    df['Unsecured Portion Covered by ECF/DCF'] = df['Unsecured Portion Covered by ECF/DCF'].fillna(0)
    df['Existing ECL held Q3\'24'] = df['Existing ECL held Q3\'24'].fillna(0)
    
    # Ensure 'Classification Date' column is in datetime format, fill any NaT (Not a Time) values with a default date if necessary
    df['Classification Date'] = pd.to_datetime(df['Classification date'], errors='coerce').fillna(pd.to_datetime('01-Jan-2000'))

    # Calculate the years since NPL
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
