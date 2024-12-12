import streamlit as st
import math

config = {
  "est": 0,
  "workload_type": "ML Training"
}

def show_ml_training_estimator():
  st.subheader("ML Training")

  #Get Num ETL Jobs
  num_ppl_opts = {
        "1 - 5": 1,
        "5 - 15": 3,
        "15+": 6
    }
  
  data_size_opts = {
      "10GB - 100GB": 1,
      "100GB - 1TB": 4,
      "1TB - 10TB": 10,
      "10TB+": 20
  }

  row1 = st.container()
  row2 = st.container()

  hrs, usrs, gput = st.columns(3)

  with hrs:
    num_ppl_sel = st.selectbox(
          "Number of Data Scientists",
          list(num_ppl_opts.keys())
      )

    # Get the selected value from the dictionary
    num_ppl = num_ppl_opts[num_ppl_sel]

  with usrs:
    #Get ETL Complexity Type
    data_opts_sel = st.selectbox(
          "Active Training Data Size",
          list(data_size_opts.keys())
    )
    
    # Get the selected value from the dictionary
    data_size = data_size_opts[data_opts_sel]

  with gput:
    #Create a checkbox for GPU training
    gpu_trn = st.checkbox("Train on GPU")

    # When the button is clicked, show a layout with multiple columns
    # Create a textbox to input the estimate in the first column
    config["est"] = create_training_estimate(num_ppl, data_size, gpu_trn)
  
    return config
  
def create_training_estimate(num_ppl, data_size, gpu_trn):
  #set the base day rate of classic CPI training at $30
  base_daily_rate = 30
  days_month = 20
  gpu_modifier = 4 if gpu_trn else 1

  est = round(num_ppl * data_size * base_daily_rate * days_month * gpu_modifier,2)

  return est