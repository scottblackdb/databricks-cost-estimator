import streamlit as st
import math

config ={
  "est": 0,
  "workload_type": "Batch ETL"
}

def show_batch_etl_estimator():
  st.subheader("Batch ETL Estimator")

  #Get Num ETL Jobs
  num_etl_opts = {
        "10 - 20": 1,
        "20 - 49": 2,
        "50 - 99": 6,
        "99+": 12
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

  etl_feq_opts = {
      "Daily": 30,
      "Weekly": 4,
      "Monthly": 1
  }

  row1 = st.container()
  row2 = st.container()

  hrs, usrs, dat, feq = st.columns(4)

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

  with feq:
    #Get DW Concurrent Users
    feq_opts_sel = st.selectbox(
          "ETL Frequency",
          list(etl_feq_opts.keys())
    )

    # Get the selected value from the dictionary
    etl_feq = etl_feq_opts[feq_opts_sel]

    # When the button is clicked, show a layout with multiple columns
    # Create a textbox to input the estimate in the first column
    config["est"] = create_batch_etl_estimate(etl_jobs, etl_type, data_size, etl_feq)
  
    return config
  
def create_batch_etl_estimate(etl_jobs, etl_type, data_size, etl_feq):
  #set the base rate for once per run 15 serverless jobs, smallest data size, simple job at $30
  base_daily_rate = 30

  est = round(etl_jobs * etl_type * data_size * base_daily_rate * etl_feq,2)

  return est