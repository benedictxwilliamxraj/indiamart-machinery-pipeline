import pandas as pd

def compute_kpis(products: pd.DataFrame) -> dict:
    k = {}
    k["n_products"] = int(products["product_id"].nunique()) if "product_id" in products else len(products)
    if "company_name" in products:
        k["n_companies"] = int(products["company_name"].nunique())
    if "price" in products and products["price"].notna().any():
        k["price_median"] = float(products["price"].median())
        k["price_avg"] = float(products["price"].mean())
    return k
