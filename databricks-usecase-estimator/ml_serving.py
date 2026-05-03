import streamlit as st

import db_config

config = {
  "est": 0,
  "workload_type": "ML Serving"
}

def show_ml_serving_estimator():
  st.subheader("ML Serving")

  c = db_config.load_constants("ml_serving")
  num_models = st.slider(
      "Select number of model CPU endpoints",
      min_value=0,
      max_value=int(c["max_models"]),
      value=0,
      step=1,
  )
  config['est'] = create_serving_estimate(num_models)
  config['config'] = {'num_models': num_models}
  return config


def create_serving_estimate(num_models):
  c = db_config.load_constants("ml_serving")
  est = round(c["base_daily_rate"] * num_models * c["model_uptime"] * c["days_per_month"], 2)
  return est
