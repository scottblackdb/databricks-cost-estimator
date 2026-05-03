import streamlit as st

import db_config


def show_batch_etl_estimator():
  st.subheader("Batch ETL Estimator")

  num_etl_opts   = db_config.load_options("batch_etl", "num_jobs")
  etl_type_opts  = db_config.load_options("batch_etl", "complexity")
  data_size_opts = db_config.load_options("batch_etl", "data_size")
  etl_feq_opts   = db_config.load_options("batch_etl", "frequency")

  hrs, usrs, dat, feq = st.columns(4)

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

  with feq:
    feq_opts_sel = st.selectbox(
          "ETL Frequency",
          list(etl_feq_opts.keys())
    )
    etl_feq = etl_feq_opts[feq_opts_sel]

  return {
      "est":           create_batch_etl_estimate(etl_jobs, etl_type, data_size, etl_feq),
      "workload_type": "Batch ETL",
  }


def create_batch_etl_estimate(etl_jobs, etl_type, data_size, etl_feq):
  c = db_config.load_constants("batch_etl")
  return round(etl_jobs * etl_type * data_size * c["base_daily_rate"] * etl_feq, 2)
