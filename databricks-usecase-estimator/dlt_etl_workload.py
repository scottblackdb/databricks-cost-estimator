import streamlit as st
import math

config ={
  "est": 0,
  "workload_type": "Streaming/DLT"
}

def show_dlt_estimator():
  st.subheader("Streaming / DLT Estimator")

  #Get Num ETL Jobs
  num_etl_opts = {
        "1 - 10": 1,
        "10 - 30": 3,
        "30 - 50": 5,
        "50+": 15
    }
  
  etl_type_opts = {
        "No Joins & Append Only": 1,
        "Simple Joins & Append Only": 3,
        "Complex Joins or Merge or SCD Type 2": 8,
    }

  data_size_opts = {
      "100MB - 1GB": 1,
      "1GB- 10GB": 1.5,
      "10GB - 100GB": 3,
      "100GB+": 4
  }

  row1 = st.container()
  row2 = st.container()

  hrs, usrs, dat = st.columns(3)

  with hrs:
    etl_jobs_sel = st.selectbox(
          "Number of ETL Jobs",
          list(num_etl_opts.keys())
      )

    # Get the selected value from the dictionary
    etl_jobs = num_etl_opts[etl_jobs_sel]

  with usrs:
    #Get ETL Complexity Type
    type_opts_sel = st.selectbox(
          "ETL Complexity Type",
          list(etl_type_opts.keys())
    )

    # Get the selected value from the dictionary
    etl_type = etl_type_opts[type_opts_sel]

  with dat:
    #Get DW Concurrent Users
    data_opts_sel = st.selectbox(
          "Data Size",
          list(data_size_opts.keys())
    )

    # Get the selected value from the dictionary
    data_size = data_size_opts[data_opts_sel]

    # When the button is clicked, show a layout with multiple columns
    # Create a textbox to input the estimate in the first column
    config["est"] = create_dlt_estimate(etl_jobs, etl_type, data_size)
  
    return config
  
def create_dlt_estimate(etl_jobs, etl_type, data_size):
  #set the base rate streaming dlt at $20
  base_daily_rate = 20
  etl_feq = 30

  est = round(etl_jobs * etl_type * data_size * base_daily_rate * etl_feq,2)

  return est