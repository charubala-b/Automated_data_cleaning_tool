import pandas as pd
import numpy as np
import re

def load_data(file):
    """Load dataset from a file (CSV, Excel)"""
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            return pd.read_excel(file)
    except Exception as e:
        return str(e)

def remove_duplicates(df):
    """Remove duplicate rows"""
    return df.drop_duplicates()

def handle_missing_values(df, strategy="drop", fill_value=None):
    """Handle missing values using different strategies"""
    if strategy == "drop":
        return df.dropna()
    elif strategy == "fill":
        return df.fillna(fill_value)
    elif strategy == "mean":
        return df.fillna(df.mean(numeric_only=True))
    elif strategy == "median":
        return df.fillna(df.median(numeric_only=True))
    return df

def standardize_column_names(df):
    """Standardize column names (lowercase, remove spaces, special chars)"""
    df.columns = [re.sub(r'\W+', '_', col.strip().lower()) for col in df.columns]
    return df

def normalize_column(df, column):
    """Normalize numerical column between 0 and 1"""
    if column in df.select_dtypes(include=np.number).columns:
        df[column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
    return df

def remove_outliers(df, column, method="zscore", threshold=3):
    """Remove outliers using Z-score or IQR method"""
    if column in df.select_dtypes(include=np.number).columns:
        if method == "zscore":
            mean, std = df[column].mean(), df[column].std()
            df = df[(np.abs((df[column] - mean) / std) < threshold)]
        elif method == "iqr":
            Q1, Q3 = df[column].quantile(0.25), df[column].quantile(0.75)
            IQR = Q3 - Q1
            df = df[(df[column] >= Q1 - 1.5 * IQR) & (df[column] <= Q3 + 1.5 * IQR)]
    return df

def convert_data_types(df):
    """Convert data types (dates, numerics)"""
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                continue
    return df