import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import get_estimate
import dw_workload
import batch_etl_workload
import dlt_etl_workload
import interactive_workload
import ml_training_workload
import ml_serving
import storage_estimate

def add_workload_estimate(cfg):
    if 'workloads' in st.session_state:
        st.session_state['workloads'].append(cfg) 
    else:
        st.session_state['workloads'] = [cfg]

def remove_workload(workload_name):
    cfgs = []

    for w in st.session_state.workloads:
        #if w['workload_name'] == workload_name:
        #    st.session_state.workloads.remove(w)
        #    workload_df = pd.DataFrame(st.session_state.workloads)
        if w['workload_name'] != workload_name:
            cfgs.append(w)

    st.session_state.remove('workloads')
    #st.session_state['workloads'] = cfgs
        
st.set_page_config(layout="wide")


image = "https://cdn.prod.website-files.com/601064f495f4b4967f921aa9/64246984585c9225aa4e4fc4_databricks.png"

col1, col2 = st.columns([1, 12])

with col1:
    st.image(image, width=40)

with col2:
    st.title("Databricks Workload Estimator")


st.markdown("<br>", unsafe_allow_html=True)
st.write("Costs are for general budget purposes only and are not guaranteed to be accurate.")
st.write("All workloads assume default pricing with serverless compute using best practices.")
st.write("Estimates does not include any discounts or security addons.")
st.write("Testing should be performed to determine more precise workload costs.")
st.markdown("<br>", unsafe_allow_html=True)

workload_options = {
        "": 0,
        "Data Warehouse": 1,
        "Batch ETL": 2,
        "Streaming/DLT": 3,
        "Analytics / Data Engineers": 4,
        "ML Training": 5,
        "ML Inference": 6,
        "Storage": 7
    }

workload_type = st.selectbox(
        "Select Workload",
        list(workload_options.keys())
    )

# Get the selected value from the dictionary
workload_sel = workload_options[workload_type]

row_show_est = st.container()
raw_show_wrk = st.container()

with row_show_est:
    match workload_sel:
        case 1:
            est = dw_workload.show_dw_estimator()
        case 2:
            est = batch_etl_workload.show_batch_etl_estimator()
        case 3:
            est = dlt_etl_workload.show_dlt_estimator()
        case 4:
            est = interactive_workload.show_interactive_estimator()
        case 5:
            est = ml_training_workload.show_ml_training_estimator()
        case 6:
            est = ml_serving.show_ml_serving_estimator()
        case 7:
            est = storage_estimate.show_storage_estimator()
    
    if 'est' in locals():
        st.write(f"**Estimated Monthly Cost: ${est['est']}**")
        
        with st.form("Add Workload"):
            wrk_name = st.text_input("Enter Workload Name", max_chars=25)
            # Create a button to submit the estimate in the second column    
            if st.form_submit_button("Add Workload"):
                st.write("Workload Added Successfully!")
                # When the submit button is clicked, display a message
                if 'config' in est.keys():
                    config = {
                        "workload_name": wrk_name,
                        "cost": est['est'],
                        "workload_type": est["workload_type"],
                        "config": est["config"]
                    }
                else:
                    config = {
                        "workload_name": wrk_name,
                        "cost": est['est'],
                        "workload_type": est["workload_type"]
                    }
                
                add_workload_estimate(config)
                st.session_state.workload_type = None
           
with raw_show_wrk:
    if 'workloads' in st.session_state:
        workload_df = pd.DataFrame(st.session_state.workloads)
        total_estimate = workload_df['cost'].sum()
        st.subheader(f"Total Monthly Estimate: ${total_estimate}")

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(workload_df)
        with col2:
            with st.form("Remove Workload"):
                workload_name = st.selectbox('Select the row to remove', workload_df)
                if st.form_submit_button("Remove Workload"):
                    remove_workload(workload_name)  