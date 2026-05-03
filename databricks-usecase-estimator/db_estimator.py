import streamlit as st
import pandas as pd

import dw_workload
import batch_etl_workload
import dlt_etl_workload
import interactive_workload
import ml_training_workload
import ml_serving
import storage_estimate
import configure_page


def add_workload_estimate(cfg):
    st.session_state.setdefault('workloads', []).append(cfg)


def remove_workload(workload_name):
    if 'workloads' not in st.session_state:
        return
    st.session_state['workloads'] = [
        w for w in st.session_state.workloads
        if w['workload_name'] != workload_name
    ]


def _render_header():
    """Logo, title, and the top-right menu popover. Returns nothing — sets
    st.session_state.page when the user navigates."""
    image = "https://cdn.prod.website-files.com/601064f495f4b4967f921aa9/64246984585c9225aa4e4fc4_databricks.png"
    logo_col, title_col, menu_col = st.columns([1, 11, 1])
    with logo_col:
        st.image(image, width=40)
    with title_col:
        st.title("Databricks Workload Estimator")
    with menu_col:
        with st.popover("☰", help="Menu"):
            if st.session_state.page != "main":
                if st.button("Estimator", key="nav_main", use_container_width=True):
                    st.session_state.page = "main"
                    st.rerun()
            if st.session_state.page != "configure":
                if st.button("Configure", key="nav_configure", use_container_width=True):
                    st.session_state.page = "configure"
                    st.rerun()


def show_main_page():
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("Costs are for general budget purposes only and are not guaranteed to be accurate.")
    st.write("All workloads assume default pricing with serverless compute using best practices.")
    st.write("Estimates does not include any discounts or security addons.")
    st.write("Testing should be performed to determine more precise workload costs.")
    st.markdown("<br>", unsafe_allow_html=True)

    workloads = {
        "": None,
        "Data Warehouse":             dw_workload.show_dw_estimator,
        "Batch ETL":                  batch_etl_workload.show_batch_etl_estimator,
        "Streaming/DLT":              dlt_etl_workload.show_dlt_estimator,
        "Analytics / Data Engineers": interactive_workload.show_interactive_estimator,
        "ML Training":                ml_training_workload.show_ml_training_estimator,
        "ML Inference":               ml_serving.show_ml_serving_estimator,
        "Storage":                    storage_estimate.show_storage_estimator,
    }

    workload_type = st.selectbox("Select Workload", list(workloads.keys()))
    show_estimator = workloads[workload_type]

    row_show_est = st.container()
    row_show_wrk = st.container()

    with row_show_est:
        est = show_estimator() if show_estimator else None

        if est:
            st.write(f"**Estimated Monthly Cost: ${est['est']:,.2f}**")

            with st.form("Add Workload"):
                wrk_name = st.text_input("Enter Workload Name", max_chars=25)
                if st.form_submit_button("Add Workload"):
                    cfg = {
                        "workload_name": wrk_name,
                        "cost": est['est'],
                        "workload_type": est["workload_type"],
                    }
                    if 'config' in est:
                        cfg["config"] = est["config"]
                    add_workload_estimate(cfg)
                    st.success("Workload Added Successfully!")

    with row_show_wrk:
        saved = st.session_state.get('workloads') or []
        if saved:
            workload_df = pd.DataFrame(saved)
            total_estimate = workload_df['cost'].sum()
            st.subheader(f"Total Monthly Estimate: ${total_estimate:,.2f}")

            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(workload_df)
            with col2:
                with st.form("Remove Workload"):
                    workload_name = st.selectbox(
                        'Select the row to remove',
                        workload_df['workload_name'].tolist(),
                    )
                    if st.form_submit_button("Remove Workload"):
                        remove_workload(workload_name)


st.set_page_config(layout="wide")
st.session_state.setdefault("page", "main")

_render_header()

if st.session_state.page == "configure":
    configure_page.show_configure_page()
else:
    show_main_page()
