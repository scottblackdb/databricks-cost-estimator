import streamlit as st
import math

config = {
  "est": 0,
  "workload_type": "ML Serving"
}

def show_ml_serving_estimator():
  st.subheader("ML Serving")

  num_models = st.slider("Select number of model CPU endpoints", min_value=0, max_value=25, value=0, step=1)
  config['est'] = create_serving_estimate(num_models)
  config['config'] = {'num_models': num_models}
  return config


def create_serving_estimate(num_models):
  #set the base day rate of classic CPI training at $30
  base_daily_rate = 7
  model_uptime = .8
  #gpu_modifier = 4 if gpu_trn else 1

  est = round(base_daily_rate * num_models * model_uptime * 30,2)

  return est