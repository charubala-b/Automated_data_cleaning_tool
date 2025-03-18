import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from cleaning import (
    load_data, remove_duplicates, handle_missing_values, 
    standardize_column_names, normalize_column, remove_outliers, 
    convert_data_types
)

# **Function to Encode Image as Base64**
def get_base64(img_path):
    with open(img_path, "rb") as file:
        return base64.b64encode(file.read()).decode()

# Load background image
img_data = get_base64("d1.webp")

# **Custom CSS Styling**
# background_style = """
    
# """

st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient(to right, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.1)),url('data:image/jpg;base64,{img_data}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        [data-testid="stSidebar"] {{
            background: rgba(173, 216, 230, 0.85); /* Light blue with transparency */
            padding: 20px;
            border-radius: 10px;
        }}

        .sidebar-text {{
            font-size: 18px;
            font-weight: bold;
            color: #004e89;
            text-align: center;
            padding: 5px;
        }}

        .stButton>button {{
            background-color: #1f4e79 !important;
            color: white !important;
            font-size: 18px !important;
            border-radius: 10px !important;
            padding: 12px 24px !important;
            transition: all 0.3s ease;
            border: none;
        }}

        .stButton>button:hover {{
            background-color: #13395a !important;
            transform: scale(1.05);
        }}

        .stExpander {{
            border-radius: 12px;
            border: 2px solid #1f4e79;
            background: rgba(255, 255, 255, 0.8);
        }}
    </style>
""", unsafe_allow_html=True)

# **📌 Title**
st.markdown("<h1>🧹 Data Cleaning Tool</h1>", unsafe_allow_html=True)

# **📂 Sidebar - File Upload**
st.sidebar.markdown("<div class='sidebar-text'>📂 Upload Datasets</div>", unsafe_allow_html=True)
uploaded_files = st.sidebar.file_uploader("Upload one or more CSV/Excel files", type=["csv", "xlsx"], accept_multiple_files=True)

dfs = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        df = load_data(uploaded_file)
        if isinstance(df, str):
            st.error(f"❌ Error loading file {uploaded_file.name}: {df}")
        else:
            dfs.append(df)

    if len(dfs) > 1:
        # **🔄 Merge Multiple Datasets**
        st.sidebar.markdown("<div class='sidebar-text'>🔄 Merge Options</div>", unsafe_allow_html=True)
        common_columns = list(set.intersection(*[set(df.columns) for df in dfs]))

        if common_columns:
            merge_col = st.sidebar.selectbox("🔗 Select Common Column to Merge On", common_columns)
            merge_type = st.sidebar.radio("⚖️ Merge Type", ["Inner", "Outer", "Left", "Right"])

            merged_df = dfs[0]
            for df in dfs[1:]:
                merged_df = merged_df.merge(df, on=merge_col, how=merge_type.lower())

            df = merged_df
            st.success(f"✅ {len(dfs)} files merged successfully using **{merge_type} Join** on **{merge_col}**!")

    elif len(dfs) == 1:
        df = dfs[0]
        st.success("✅ File uploaded successfully!")

    # **📊 Show Raw Data**
    st.write("### Raw Data Preview")
    st.dataframe(df)

    # **📊 Dataset Summary**
    with st.expander("📊 Dataset Summary"):
        st.write(df.describe())

    # **🛠 Data Cleaning Options**
    st.sidebar.markdown("<div class='sidebar-text'>🛠 Data Cleaning Options</div>", unsafe_allow_html=True)

    # **🗑 Remove Duplicates**
    if st.sidebar.checkbox("🗑 Remove Duplicates"):
        df = remove_duplicates(df)
        st.sidebar.success("✔️ Duplicates removed!")

    # **⚠️ Handle Missing Values**
    missing_strategy = st.sidebar.radio("⚠️ Handle Missing Values", ["None", "Drop", "Fill with Value", "Mean", "Median"])
    if missing_strategy == "Fill with Value":
        fill_value = st.sidebar.text_input("Enter Fill Value", value="")
        df = handle_missing_values(df, strategy="fill", fill_value=fill_value)
    elif missing_strategy in ["Mean", "Median"]:
        df = handle_missing_values(df, strategy=missing_strategy.lower())

    # **🔤 Standardize Column Names**
    if st.sidebar.checkbox("🔤 Standardize Column Names"):
        df = standardize_column_names(df)

    # **📏 Normalize a Numerical Column**
    normalize_col = st.sidebar.selectbox("📏 Normalize Column", ["None"] + list(df.select_dtypes(include="number").columns), key="normalize_column")
    if normalize_col != "None":
        df = normalize_column(df, normalize_col)

    # **📉 Remove Outliers**
    outlier_col = st.sidebar.selectbox("📉 Remove Outliers", ["None"] + list(df.select_dtypes(include="number").columns), key="outlier_column")
    outlier_method = st.sidebar.radio("⚖️ Outlier Removal Method", ["Z-score", "IQR"])
    if outlier_col != "None":
        df = remove_outliers(df, outlier_col, method=outlier_method.lower())

    # **🔄 Convert Data Types**
    if st.sidebar.checkbox("🔄 Convert Data Types"):
        df = convert_data_types(df)

    # **✨ Show Cleaned Data**
    st.write("### ✨ Cleaned Data Preview")
    st.dataframe(df)

    # **📥 File Download Options**
    st.sidebar.markdown("<div class='sidebar-text'>📥 Export Cleaned Data</div>", unsafe_allow_html=True)

    def convert_df(df, file_type):
        buffer = BytesIO()
        if file_type == "CSV":
            df.to_csv(buffer, index=False)
        elif file_type == "Excel":
            df.to_excel(buffer, index=False, engine='xlsxwriter')
        elif file_type == "JSON":
            df.to_json(buffer, orient="records")
        elif file_type == "Parquet":
            df.to_parquet(buffer, index=False)
        buffer.seek(0)
        return buffer

    file_format = st.sidebar.selectbox("📁 Choose Format", ["CSV", "Excel", "JSON", "Parquet"])
    file_data = convert_df(df, file_format)

    st.download_button(
        f"📥 Download as {file_format}",
        data=file_data,
        file_name=f"cleaned_data.{file_format.lower()}",
        mime="text/csv" if file_format == "CSV" else
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if file_format == "Excel" else
        "application/json" if file_format == "JSON" else
        "application/octet-stream"
    )
