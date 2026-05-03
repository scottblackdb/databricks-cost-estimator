import streamlit as st

import db_config

config = {
  "est": 0,
  "workload_type": "Analytics / Data Engineers"
}

def show_interactive_estimator():
  st.subheader("Analytics / Data Engineers")

  num_ppl_opts   = db_config.load_options("interactive", "num_people")
  data_size_opts = db_config.load_options("interactive", "data_size")

  hrs, usrs = st.columns(2)

  with hrs:
    num_ppl_sel = st.selectbox(
          "Number of People",
          list(num_ppl_opts.keys())
      )
    num_ppl = num_ppl_opts[num_ppl_sel]

  with usrs:
    data_opts_sel = st.selectbox(
          "Active Data Size",
          list(data_size_opts.keys())
    )
    data_size = data_size_opts[data_opts_sel]

    config["est"] = create_interactive_estimate(num_ppl, data_size)

    return config

def create_interactive_estimate(num_ppl, data_size):
  c = db_config.load_constants("interactive")
  est = round(num_ppl * data_size * c["base_daily_rate"] * c["days_per_month"], 2)
  return est
