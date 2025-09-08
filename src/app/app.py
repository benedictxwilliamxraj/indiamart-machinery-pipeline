import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import pandas as pd
from etl.io import read_processed
from etl.kpi import compute_kpis

st.set_page_config(page_title="IndiaMart Dashboard", layout="wide")

@st.cache_data
def load():
    return read_processed()

products, companies = load()

k = compute_kpis(products)
c1, c2, c3 = st.columns(3)
c1.metric("Products", f"{k.get('n_products', 0):,}")
c2.metric("Companies", f"{k.get('n_companies', 0):,}")
c3.metric("Median Price", f"{k.get('price_median', 0):,.0f}")

st.subheader("Products")
st.dataframe(products.head(100), use_container_width=True, hide_index=True)

st.subheader("Companies")
st.dataframe(companies.head(100), use_container_width=True, hide_index=True)

