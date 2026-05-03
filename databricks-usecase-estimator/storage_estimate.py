import streamlit as st

import db_config


def show_storage_estimator():
  st.subheader("Storage Estimator")
  storage = st.number_input("Data Size (GB)", min_value=1)

  return {
      "est":           create_storage_estimate(storage),
      "workload_type": "Storage",
  }


def create_storage_estimate(storage):
  c = db_config.load_constants("storage")
  return round(storage * c["base_monthly_rate"], 2)
