import streamlit as st
import math

config = {
  "est": 0,
  "workload_type": "Analytics / Data Engineers"
}

def show_interactive_estimator():
  st.subheader("Analytics / Data Engineers")

  #Get Num ETL Jobs
  num_ppl_opts = {
        "5 - 10": 1,
        "10 - 20": 3,
        "20 - 35": 5,
        "35+": 15
    }
  
  data_size_opts = {
      "10GB - 100GB": 1,
      "100GB - 1TB": 4,
      "1TB - 10TB": 10,
      "10TB+": 20
  }

  row1 = st.container()
  row2 = st.container()

  hrs, usrs = st.columns(2)

  with hrs:
    num_ppl_sel = st.selectbox(
          "Number of People",
          list(num_ppl_opts.keys())
      )

    # Get the selected value from the dictionary
    num_ppl = num_ppl_opts[num_ppl_sel]

  with usrs:
    #Get ETL Complexity Type
    data_opts_sel = st.selectbox(
          "Active Data Size",
          list(data_size_opts.keys())
    )

    # Get the selected value from the dictionary
    data_size = data_size_opts[data_opts_sel]

    # When the button is clicked, show a layout with multiple columns
    # Create a textbox to input the estimate in the first column
    config["est"] = create_interactive_estimate(num_ppl, data_size)
  
    return config
  
def create_interactive_estimate(num_ppl, data_size):
  #set the base rate of interactive at $60
  base_daily_rate = 60
  days_month = 20

  est = round(num_ppl * data_size * base_daily_rate * days_month,2)

  return est