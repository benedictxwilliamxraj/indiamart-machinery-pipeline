import re
import pandas as pd



def clean_catalog(catalog: pd.DataFrame) -> pd.DataFrame:
    df = catalog.copy()
    for col in ("product_id","product_url","company_name"):       # "product_name",
        #print(df.columns)
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df.drop_duplicates(subset=["product_id"]).reset_index(drop=True)

def clean_details(details: pd.DataFrame) -> pd.DataFrame:
    df = details.copy()
    # if "price" in df.columns:
        # df["price"] = df["price"].map(_to_price)
    # normalize exports_to to a comma-joined list
    if "exports_to" in df.columns:
        df["exports_to"] = df["exports_to"].fillna("").astype(str)
        df["exports_list"] = df["exports_to"].apply(
            lambda s: [t.strip() for t in s.split(",") if t.strip()]
        )
    # flatten spec table if present (keep as JSON string)
    if "spec" in df.columns and df["spec"].map(lambda v: isinstance(v, dict)).any():
        df["spec_json"] = df["spec"].apply(lambda d: d if isinstance(d, dict) else {})
    return df
