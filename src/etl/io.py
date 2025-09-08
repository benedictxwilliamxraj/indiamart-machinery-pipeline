import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "/Users/benedictraj/Documents/MyProjects/IndiaMartDataVis/src/storage", "")
RAW_DIR = os.path.join(DATA_DIR, "")
PROCESSED_DIR = os.path.join(DATA_DIR, "")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def read_raw():
    cat = pd.read_csv(os.path.join(DATA_DIR, "harvested_df.csv"))
    det = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
    return cat, det

def write_processed(df_products, df_companies):
    df_products.to_parquet(os.path.join(PROCESSED_DIR, "products.parquet"), index=False)
    df_companies.to_parquet(os.path.join(PROCESSED_DIR, "companies.parquet"), index=False)

def read_processed():
    p = pd.read_parquet(os.path.join(PROCESSED_DIR, "products.parquet"))
    c = pd.read_parquet(os.path.join(PROCESSED_DIR, "companies.parquet"))
    return p, c
