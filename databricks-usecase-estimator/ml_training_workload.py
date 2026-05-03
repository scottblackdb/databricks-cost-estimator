import streamlit as st

import db_config

config = {
  "est": 0,
  "workload_type": "ML Training"
}

def show_ml_training_estimator():
  st.subheader("ML Training")

  num_ppl_opts   = db_config.load_options("ml_training", "num_people")
  data_size_opts = db_config.load_options("ml_training", "data_size")

  hrs, usrs, gput = st.columns(3)

  with hrs:
    num_ppl_sel = st.selectbox(
          "Number of Data Scientists",
          list(num_ppl_opts.keys())
      )
    num_ppl = num_ppl_opts[num_ppl_sel]

  with usrs:
    data_opts_sel = st.selectbox(
          "Active Training Data Size",
          list(data_size_opts.keys())
    )
    data_size = data_size_opts[data_opts_sel]

  with gput:
    gpu_trn = st.checkbox("Train on GPU")

    config["est"] = create_training_estimate(num_ppl, data_size, gpu_trn)

    return config

def create_training_estimate(num_ppl, data_size, gpu_trn):
  c = db_config.load_constants("ml_training")
  gpu_modifier = c["gpu_modifier"] if gpu_trn else 1
  est = round(num_ppl * data_size * c["base_daily_rate"] * c["days_per_month"] * gpu_modifier, 2)
  return est
