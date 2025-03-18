import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# MySQL Database Configuration
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root@123"
MYSQL_DB = "data_cleaning"

# Create MySQL Engine
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}")

# Function to save data to MySQL
def save_to_db(df, table_name="cleaned_data"):
    """
    Saves cleaned data to MySQL.
    """
    try:
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)
        st.success(f"✅ Data saved to MySQL table: {table_name}")
    except Exception as e:
        st.error(f"❌ Error saving data to MySQL: {e}")

# Function to load data from MySQL
def load_from_db(table_name="cleaned_data"):
    """
    Loads data from MySQL table.
    """
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", con=engine)
        st.success(f"✅ Data loaded from MySQL table: {table_name}")
        return df
    except Exception as e:
        st.error(f"❌ Error loading data from MySQL: {e}")
        return pd.DataFrame()  # Return empty DataFrame to avoid crashes
