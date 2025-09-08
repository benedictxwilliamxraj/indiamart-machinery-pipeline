import pandas as pd

def build_products(catalog: pd.DataFrame, details: pd.DataFrame) -> pd.DataFrame:
    # left preference to details; fallback to catalog
    keys = ["product_id"]
    pr_cols = list(set(catalog.columns) | set(details.columns))
    df = details.merge(catalog, on=keys, how="outer", suffixes=("_det","_cat"))

    def coalesce(a, b):
        return a.combine_first(b)

    out = pd.DataFrame()
    out["product_id"] = df["product_id"]
    for col in pr_cols:
        if col in ("product_id",): continue
        dc = f"{col}_det"
        cc = f"{col}_cat"
        if dc in df.columns or cc in df.columns:
            out[col] = coalesce(df.get(dc), df.get(cc))
    return out

def build_companies(products: pd.DataFrame) -> pd.DataFrame:
    keep = [c for c in ("company_name","company_url","gst_number","iec_number","location","rating") if c in products.columns]
    base = products[["product_id"] + keep].copy()
    agg = {
        "product_id": "nunique",
    }
    out = base.groupby(keep, dropna=False, as_index=False).agg(agg).rename(columns={"product_id":"product_count"})
    return out.sort_values("product_count", ascending=False)
