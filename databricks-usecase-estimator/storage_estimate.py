import streamlit as st
import math

config ={
  "est": 0,
  "workload_type": "Storage"
}

def show_storage_estimator():
  st.subheader("Storage Estimator")
  storage = st.number_input("Data Size (GB)", min_value=1)
    
  # When the button is clicked, show a layout with multiple columns
  # Create a textbox to input the estimate in the first column
  config["est"] = create_storage_estimate(storage)

  return config
  
def create_storage_estimate(storage):
  #set the base monthy rate at $0.15/gb to account for storage, I/O and time travel 
  base_monthly_rate = .15

  est = round(storage * base_monthly_rate,2)

  return est