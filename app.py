import streamlit as st
import pandas as pd
import base64
from cleaning import load_data, remove_duplicates, handle_missing_values, standardize_column_names, normalize_column, remove_outliers, convert_data_types

# **Function to Encode Image as Base64**
def get_base64(img_path):
    with open(img_path, "rb") as file:
        return base64.b64encode(file.read()).decode()

# Load background image
img_data = get_base64("d1.webp")

# **🎨 Custom CSS Styling**
st.markdown(f"""
    <style>
        /* Main App Background */
        .stApp {{
            background: linear-gradient(to right, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.1)),url('data:image/jpg;base64,{img_data}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Title Styling */
        h1 {{
            color: white !important;
            text-align: center;
            font-size: 42px;
            font-weight: bold;
            padding: 15px;
            background: #1f4e79;
            border-radius: 12px;
            margin-bottom: 20px;
        }}

        /* Sidebar Styling - Lighter Blue with Enhanced Icons */
        [data-testid="stSidebar"] {{
            background: linear-gradient(to right, rgba(200, 230, 250, 0.9), rgba(180, 220, 250, 0.9));
            color: #1f4e79;
            padding: 20px;
            border-radius: 8px;
        }}

        /* Sidebar Title & Text */
        .sidebar-text {{
            font-size: 20px;
            font-weight: bold;
            color: #1f4e79;
            text-align: center;
            padding: 10px;
        }}

        /* Sidebar Icons Styling */
        .stRadio label, .stCheckbox label, .stSelectbox label {{
            font-size: 18px;
            font-weight: bold;
            color: #144e75;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .stRadio label:before, .stCheckbox label:before, .stSelectbox label:before {{
            content: "✔️";
            font-size: 22px;
            color: #007bff;
            text-shadow: 0px 0px 8px rgba(0, 123, 255, 0.7);
            transition: transform 0.2s ease-in-out;
        }}

        /* Hover Effect on Sidebar Elements */
        .stRadio label:hover, .stCheckbox label:hover, .stSelectbox label:hover {{
            color: #0056b3;
            transform: scale(1.05);
        }}

        /* Highlight Selected Sidebar Options */
        .stRadio [aria-checked="true"] label, .stCheckbox [aria-checked="true"] label {{
            color: #ffffff;
            background: #007bff;
            padding: 5px 10px;
            border-radius: 5px;
        }}

        /* DataFrame Styling */
        .stDataFrame {{
            width: 90%;
            margin: auto;
            border-radius: 12px;
            box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.3);
        }}

        /* Button Styling */
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

        /* Expander Styling */
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
st.sidebar.markdown("<div class='sidebar-text'>📂 Upload Dataset</div>", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if isinstance(df, str):
        st.error(f"❌ Error loading file: {df}")
    else:
        st.success("✅ File uploaded successfully!")
        st.write("### Raw Data Preview")
        st.dataframe(df)

        # **📊 Dataset Summary**
        with st.expander("📊 Dataset Summary"):
            st.write(df.describe())

        # **🛠 Sidebar - Data Cleaning Options**
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

        # **📥 Download Cleaned Dataset**
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Cleaned Data", data=csv, file_name="cleaned_data.csv", mime="text/csv")
