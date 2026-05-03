import streamlit as st

import db_config

config = {
  "est": 0,
  "workload_type": "Storage"
}

def show_storage_estimator():
  st.subheader("Storage Estimator")
  storage = st.number_input("Data Size (GB)", min_value=1)

  config["est"] = create_storage_estimate(storage)

  return config

def create_storage_estimate(storage):
  c = db_config.load_constants("storage")
  est = round(storage * c["base_monthly_rate"], 2)
  return est
