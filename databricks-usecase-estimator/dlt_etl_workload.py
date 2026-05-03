import streamlit as st

import db_config

config = {
  "est": 0,
  "workload_type": "Streaming/DLT"
}

def show_dlt_estimator():
  st.subheader("Streaming / DLT Estimator")

  num_etl_opts   = db_config.load_options("dlt", "num_jobs")
  etl_type_opts  = db_config.load_options("dlt", "complexity")
  data_size_opts = db_config.load_options("dlt", "data_size")

  hrs, usrs, dat = st.columns(3)

  with hrs:
    etl_jobs_sel = st.selectbox(
          "Number of ETL Jobs",
          list(num_etl_opts.keys())
      )
    etl_jobs = num_etl_opts[etl_jobs_sel]

  with usrs:
    type_opts_sel = st.selectbox(
          "ETL Complexity Type",
          list(etl_type_opts.keys())
    )
    etl_type = etl_type_opts[type_opts_sel]

  with dat:
    data_opts_sel = st.selectbox(
          "Data Size",
          list(data_size_opts.keys())
    )
    data_size = data_size_opts[data_opts_sel]

    config["est"] = create_dlt_estimate(etl_jobs, etl_type, data_size)

    return config

def create_dlt_estimate(etl_jobs, etl_type, data_size):
  c = db_config.load_constants("dlt")
  est = round(etl_jobs * etl_type * data_size * c["base_daily_rate"] * c["frequency"], 2)
  return est
