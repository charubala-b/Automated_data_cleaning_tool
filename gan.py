import streamlit as st
import pandas as pd
import re
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from scipy import stats

def generate_synthetic_data(data, num_epochs=500):
    class Generator(nn.Module):
        def __init__(self, input_dim, output_dim):
            super(Generator, self).__init__()
            self.model = nn.Sequential(
                nn.Linear(input_dim, 128),
                nn.ReLU(),
                nn.Linear(128, 128),
                nn.ReLU(),
                nn.Linear(128, output_dim)
            )
        
        def forward(self, x):
            return self.model(x)
    
    data = torch.tensor(data, dtype=torch.float32)
    input_dim = data.shape[1]
    generator = Generator(input_dim, input_dim)
    optimizer = optim.Adam(generator.parameters(), lr=0.01)
    loss_fn = nn.MSELoss()
    
    for _ in range(num_epochs):
        optimizer.zero_grad()
        synthetic_data = generator(data)
        loss = loss_fn(synthetic_data, data)
        loss.backward()
        optimizer.step()
    
    return synthetic_data.detach().numpy()

def clean_data(df):
    df = df.dropna(how='all', axis=1)  # Drop completely empty columns
    df.drop_duplicates(inplace=True)  # Remove duplicate rows
    
    # Standardizing text format (handling inconsistent categorical data)
    df = df.apply(lambda x: x.str.strip().str.lower() if x.dtype == "object" else x)
    
    # Convert numerical columns stored as objects
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].str.replace(r'[^0-9.]', '', regex=True).str.isnumeric().all():
            df[col] = pd.to_numeric(df[col].str.replace(r'[^0-9.]', '', regex=True), errors='coerce')
    
    # Handle outliers using Z-score method
    numeric_cols = df.select_dtypes(include=['number']).columns
    if not df.empty:
        df = df[(np.abs(stats.zscore(df[numeric_cols])) < 3).all(axis=1)]
    
    # Ensure dataset is not empty after outlier removal
    if df.empty:
        st.warning("All rows were removed due to outliers. Skipping normalization.")
        return df
    
    # Apply label encoding for categorical columns
    for col in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
    
    # Handle missing values using GAN-based imputation
    if df.isnull().sum().sum() > 0:
        imputer = SimpleImputer(strategy='mean')
        df_imputed = imputer.fit_transform(df)
        df_synthetic = generate_synthetic_data(df_imputed)
        df = pd.DataFrame(df_synthetic, columns=df.columns)
    
    # Normalize numerical values if dataset is not empty
    if not df.empty and not df[numeric_cols].empty:
        scaler = StandardScaler()
        df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    
    return df

def main():
    st.title("GAN-Based Dataset Cleaning App")
    uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx", "json"])  
    
    if uploaded_file:
        file_extension = uploaded_file.name.split(".")[-1]
        
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_extension == "xlsx":
            df = pd.read_excel(uploaded_file)
        elif file_extension == "json":
            df = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file format")
            return
        
        st.write("### Raw Data Preview")
        st.dataframe(df)  # Show full dataset
        
        cleaned_df = clean_data(df)
        st.write("### Cleaned Data Preview (Editable)")
        edited_df = st.data_editor(cleaned_df)  # Allow manual editing
        
        file_format = st.selectbox("Select download format", ["CSV", "Excel", "JSON"])
        
        if not edited_df.empty:
            if file_format == "CSV":
                file_data = edited_df.to_csv(index=False).encode('utf-8')
                file_name = "cleaned_data.csv"
                mime_type = "text/csv"
            elif file_format == "Excel":
                file_data = edited_df.to_excel(index=False, engine='openpyxl').encode('utf-8')
                file_name = "cleaned_data.xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif file_format == "JSON":
                file_data = edited_df.to_json(indent=4).encode('utf-8')
                file_name = "cleaned_data.json"
                mime_type = "application/json"
            
            st.download_button("Download Cleaned Data", file_data, file_name, mime_type)
        else:
            st.error("No data left after cleaning. Please check your dataset.")

if __name__ == "__main__":
    main()
