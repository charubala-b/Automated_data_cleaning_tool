import streamlit as st
import pandas as pd
import numpy as np
import re
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Custom CSS for better UI
st.markdown("""
    <style>
    /* Background Color */
    .main {
        background-color: #f5f7fa;
    }
    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #2c3e50 !important;
        color: white;
    }
    /* Font Styling */
    h1, h2, h3 {
        font-family: 'Arial', sans-serif;
        color: #2c3e50;
    }
    /* Animations */
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    .element-container {
        animation: fadeIn 1s ease-in-out;
    }
    </style>
""", unsafe_allow_html=True)

# Page Configuration
st.set_page_config(page_title="Data Cleaning Tool", layout="wide")
st.title("🧹 Data Cleaning & Visualization Tool")

# Function to load data
def load_data(file):
    """Load dataset from a file (CSV, Excel)"""
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            return pd.read_excel(file)
    except Exception as e:
        return str(e)

# File uploader
uploaded_file = st.file_uploader("Upload your dataset (CSV or Excel)", type=["csv", "xlsx"])
if uploaded_file:
    df = load_data(uploaded_file)
    
    if isinstance(df, str):
        st.error(f"Error loading file: {df}")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.write("### Raw Data")
            st.dataframe(df)

        # **Data Cleaning Options**
        st.sidebar.header("🔧 Data Cleaning Options")

        # Remove duplicates
        if st.sidebar.checkbox("Remove Duplicates"):
            df = df.drop_duplicates()
            st.sidebar.success("Duplicates removed!")

        # Handle missing values
        missing_strategy = st.sidebar.radio("Handle Missing Values", ["None", "Drop", "Fill with Value", "Mean", "Median"])
        if missing_strategy == "Fill with Value":
            fill_value = st.sidebar.text_input("Enter Fill Value", value="")
            df = df.fillna(fill_value)
        elif missing_strategy in ["Mean", "Median"]:
            df = df.fillna(df.mean(numeric_only=True) if missing_strategy == "Mean" else df.median(numeric_only=True))

        # Standardize column names
        if st.sidebar.checkbox("Standardize Column Names"):
            df.columns = [re.sub(r'\W+', '_', col.strip().lower()) for col in df.columns]

        # Normalize numerical column
        normalize_col = st.sidebar.selectbox("Normalize Column", ["None"] + list(df.select_dtypes(include="number").columns))
        if normalize_col != "None":
            df[normalize_col] = (df[normalize_col] - df[normalize_col].min()) / (df[normalize_col].max() - df[normalize_col].min())

        # Remove outliers
        outlier_col = st.sidebar.selectbox("Remove Outliers from Column", ["None"] + list(df.select_dtypes(include="number").columns))
        outlier_method = st.sidebar.radio("Outlier Removal Method", ["Z-score", "IQR"])
        if outlier_col != "None":
            if outlier_method == "Z-score":
                mean, std = df[outlier_col].mean(), df[outlier_col].std()
                df = df[(np.abs((df[outlier_col] - mean) / std) < 3)]
            elif outlier_method == "IQR":
                Q1, Q3 = df[outlier_col].quantile(0.25), df[outlier_col].quantile(0.75)
                IQR = Q3 - Q1
                df = df[(df[outlier_col] >= Q1 - 1.5 * IQR) & (df[outlier_col] <= Q3 + 1.5 * IQR)]

        # Convert data types
        if st.sidebar.checkbox("Convert Data Types"):
            for col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    try:
                        df[col] = pd.to_numeric(df[col])
                    except:
                        continue

        # **Display cleaned data**
        with col2:
            st.write("### Cleaned Data")
            st.dataframe(df)

        # **Download cleaned dataset**
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Cleaned Data", data=csv, file_name="cleaned_data.csv", mime="text/csv")

        # **Dashboard Visualization**
        st.sidebar.header("📊 Data Visualization")

        if st.sidebar.checkbox("Show Dataset Summary"):
            st.write("### Dataset Summary")
            st.write(df.describe())

        if st.sidebar.checkbox("Show Missing Values"):
            st.write("### Missing Values")
            st.write(df.isnull().sum())

        # Visualization Selection
        visualization = st.sidebar.selectbox("Select Visualization", ["None", "Histogram", "Box Plot", "Correlation Heatmap"])
        if visualization != "None":
            numeric_cols = df.select_dtypes(include="number").columns

            if numeric_cols.any():
                selected_col = st.sidebar.selectbox("Select Column", numeric_cols)

                if visualization == "Histogram":
                    fig = px.histogram(df, x=selected_col, title=f"Histogram of {selected_col}")
                    st.plotly_chart(fig)

                elif visualization == "Box Plot":
                    fig = px.box(df, y=selected_col, title=f"Box Plot of {selected_col}")
                    st.plotly_chart(fig)

                elif visualization == "Correlation Heatmap":
                    plt.figure(figsize=(10, 6))
                    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
                    st.pyplot(plt)
