import streamlit as st
import pandas as pd
from cleaning import load_data, remove_duplicates, handle_missing_values, standardize_column_names, normalize_column, remove_outliers, convert_data_types

# Page title
st.set_page_config(page_title="Data Cleaning Tool", layout="wide")
st.title("🧹 Data Cleaning Tool")

# File uploader
uploaded_file = st.file_uploader("Upload your dataset (CSV or Excel)", type=["csv", "xlsx"])
if uploaded_file:
    df = load_data(uploaded_file)
    
    if isinstance(df, str):
        st.error(f"Error loading file: {df}")
    else:
        st.write("### Raw Data")
        st.dataframe(df)

        # **Data Cleaning Options**
        st.sidebar.header("🔧 Data Cleaning Options")

        # Remove duplicates
        if st.sidebar.checkbox("Remove Duplicates"):
            df = remove_duplicates(df)
            st.sidebar.success("Duplicates removed!")

        # Handle missing values
        missing_strategy = st.sidebar.radio("Handle Missing Values", ["None", "Drop", "Fill with Value", "Mean", "Median"])
        if missing_strategy == "Fill with Value":
            fill_value = st.sidebar.text_input("Enter Fill Value", value="")
            df = handle_missing_values(df, strategy="fill", fill_value=fill_value)
        elif missing_strategy in ["Mean", "Median"]:
            df = handle_missing_values(df, strategy=missing_strategy.lower())

        # Standardize column names
        if st.sidebar.checkbox("Standardize Column Names"):
            df = standardize_column_names(df)

        # Normalize numerical column
        normalize_col = st.sidebar.selectbox("Normalize Column", ["None"] + list(df.select_dtypes(include="number").columns))
        if normalize_col != "None":
            df = normalize_column(df, normalize_col)

        # Remove outliers
        outlier_col = st.sidebar.selectbox("Remove Outliers from Column", ["None"] + list(df.select_dtypes(include="number").columns))
        outlier_method = st.sidebar.radio("Outlier Removal Method", ["Z-score", "IQR"])
        if outlier_col != "None":
            df = remove_outliers(df, outlier_col, method=outlier_method.lower())

        # Convert data types
        if st.sidebar.checkbox("Convert Data Types"):
            df = convert_data_types(df)

        # **Display cleaned data**
        st.write("### Cleaned Data")
        st.dataframe(df)

        # **Download cleaned dataset**
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Cleaned Data", data=csv, file_name="cleaned_data.csv", mime="text/csv")
