import streamlit as st

import db_config

dw_config = {
  "est": 0,
  "workload_type": "Data Warehouse"
}

def show_dw_estimator():
  st.subheader("Data Warehouse")

  dw_hours_opts  = db_config.load_options("dw", "hours_per_day")
  conn_usrs_opts = db_config.load_options("dw", "concurrent_users")
  data_size_opts = db_config.load_options("dw", "data_size")

  hrs, usrs, dat = st.columns(3)

  with hrs:
    dw_hrs_sel = st.selectbox(
          "Hours Per Day Data Warehouse Active",
          list(dw_hours_opts.keys())
      )
    dw_hrs = dw_hours_opts[dw_hrs_sel]

  with usrs:
    conn_opts_sel = st.selectbox(
          "Number of Concurrent Queries/Users",
          list(conn_usrs_opts.keys())
    )
    conn_usrs = conn_usrs_opts[conn_opts_sel]

  with dat:
    data_opts_sel = st.selectbox(
          "Active Data Set Size",
          list(data_size_opts.keys())
    )
    data_size = data_size_opts[data_opts_sel]

    dw_config["est"] = create_dw_estimate(dw_hrs, conn_usrs, data_size)

    config = {
      "dw_hours_day": dw_hrs,
      "conncurrent_users": conn_usrs,
      "data_size": data_size
    }

    dw_config['config'] = config

    return dw_config

def create_dw_estimate(dw_hrs, conn_usrs, data_size):
  c = db_config.load_constants("dw")
  est = round(dw_hrs * conn_usrs * data_size * c["base_daily_rate"] * c["days_per_month"], 2)
  return est
