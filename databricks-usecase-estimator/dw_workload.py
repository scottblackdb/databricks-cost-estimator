import streamlit as st
import math

dw_config ={
  "est": 0,
  "workload_type": "Data Warehouse"
}

def show_dw_estimator():
  st.subheader("Data Warehouse")

  #Get DW Running Hours
  dw_hours_opts = {
        "6 - 8": 1,
        "10 - 12": 1.5,
        "24": 3
    }
  
  conn_usrs_opts = {
        "1 - 5": 1,
        "5 - 10": 1.75,
        "10 - 20": 2.5,
        "20 - 35": 4,
        "35+": 6
    }

  data_size_opts = {
      "10GB - 100GB": 1,
      "100GB - 500GB": 2,
      "500GB - 1TB": 2.5,
      "1TB - 10TB": 3,
      "10TB - 50TB": 6,
      "50TB+": 12
  }

  row1 = st.container()
  row2 = st.container()

  hrs, usrs, dat = st.columns(3)

  with hrs:
    dw_hrs_sel = st.selectbox(
          "Hours Per Day Data Warehouse Active",
          list(dw_hours_opts.keys())
      )

    # Get the selected value from the dictionary
    dw_hrs = dw_hours_opts[dw_hrs_sel]

  with usrs:
    #Get DW Concurrent Users
    conn_opts_sel = st.selectbox(
          "Number of Concurrent Queries/Users",
          list(conn_usrs_opts.keys())
    )

    # Get the selected value from the dictionary
    conn_usrs = conn_usrs_opts[conn_opts_sel]

  with dat:
    #Get DW Concurrent Users
    data_opts_sel = st.selectbox(
          "Data Size",
          list(data_size_opts.keys())
    )

    # Get the selected value from the dictionary
    data_size = data_size_opts[data_opts_sel]

    # When the button is clicked, show a layout with multiple columns
    # Create a textbox to input the estimate in the first column
    dw_config["est"] = create_dw_estimate(dw_hrs, conn_usrs, data_size)

    config = {
      "dw_hours_day": dw_hrs,
      "conncurrent_users": conn_usrs,
      "data_size": data_size
    }

    dw_config['config'] = config
  
    return dw_config
  
def create_dw_estimate(dw_hrs, conn_usrs, data_size):
  #set the base 8hr rate for serverless DBSQL to be AWS Enterprise No CSP $70/day assume 100% utilization
  base_daily_rate = 70
  days_per_month = 30.5

  est = round(dw_hrs * conn_usrs * data_size * base_daily_rate * days_per_month,2)

  return est