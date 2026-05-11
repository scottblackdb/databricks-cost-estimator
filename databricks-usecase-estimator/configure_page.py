"""Configure page — edit the Lakebase pricing tables in place.

Lets a workshop instructor (or anyone with write access to the
`cost_estimator.*` tables) tune the magic numbers backing every estimate
without redeploying the app. Edits flow straight back to Postgres; the
estimator caches are cleared so the new values take effect immediately.
"""

import pandas as pd
import streamlit as st

import db_config


def _diff_value(old_df: pd.DataFrame, new_df: pd.DataFrame, key_cols: list[str], val_col: str):
    """Yield (key_tuple, new_value) for rows whose `val_col` changed."""
    merged = old_df.merge(new_df, on=key_cols, suffixes=("_old", "_new"))
    changed = merged[merged[f"{val_col}_old"] != merged[f"{val_col}_new"]]
    for _, row in changed.iterrows():
        yield tuple(row[c] for c in key_cols), row[f"{val_col}_new"]


def _show_rates_editor():
    st.subheader("Global Rates")
    st.caption("Storage / DBU rates and the CSP modifier. Used across all workloads.")

    df = pd.DataFrame(db_config.load_all_rates())
    edited = st.data_editor(
        df,
        key="rates_editor",
        hide_index=True,
        use_container_width=True,
        disabled=["name", "description"],
        column_config={
            "name": "Rate",
            "value": st.column_config.NumberColumn("Value", format="%.4f", step=0.01),
            "description": "Description",
        },
    )

    if st.button("Save Rates", key="save_rates"):
        updates = [
            (key[0], float(new_val))
            for key, new_val in _diff_value(df, edited, ["name"], "value")
        ]
        if not updates:
            st.info("No changes to save.")
            return
        db_config.save_rate_values(updates)
        st.cache_data.clear()
        st.success(f"Saved {len(updates)} rate change(s).")
        st.rerun()


def _show_constants_editor():
    st.subheader("Workload Constants")
    st.caption("Per-workload scalars used inside each estimate formula (e.g. `base_daily_rate`).")

    df = pd.DataFrame(db_config.load_all_constants())

    workloads = sorted(df["workload"].unique())
    selected = st.multiselect(
        "Filter to workloads",
        workloads,
        default=workloads,
        key="constants_filter",
    )
    view = df[df["workload"].isin(selected)].reset_index(drop=True)

    edited = st.data_editor(
        view,
        key="constants_editor",
        hide_index=True,
        use_container_width=True,
        disabled=["workload", "name", "description"],
        column_config={
            "workload": "Workload",
            "name": "Constant",
            "value": st.column_config.NumberColumn("Value", format="%.4f", step=0.1),
            "description": "Description",
        },
    )

    if st.button("Save Constants", key="save_constants"):
        updates = [
            (key[0], key[1], float(new_val))
            for key, new_val in _diff_value(view, edited, ["workload", "name"], "value")
        ]
        if not updates:
            st.info("No changes to save.")
            return
        db_config.save_constant_values(updates)
        st.cache_data.clear()
        st.success(f"Saved {len(updates)} constant change(s).")
        st.rerun()


def _show_options_editor():
    st.subheader("Workload Options")
    st.caption(
        "The label → multiplier mappings behind every selectbox. "
        "Edit `multiplier` to retune a dropdown choice; edit `sort_order` to reorder."
    )

    df = pd.DataFrame(db_config.load_all_options())

    workloads = sorted(df["workload"].unique())
    selected = st.multiselect("Filter to workloads", workloads, default=workloads)
    view = df[df["workload"].isin(selected)].reset_index(drop=True)

    edited = st.data_editor(
        view,
        key="options_editor",
        hide_index=True,
        use_container_width=True,
        disabled=["workload", "option_group", "label"],
        column_config={
            "workload": "Workload",
            "option_group": "Group",
            "label": "Dropdown Label",
            "multiplier": st.column_config.NumberColumn("Multiplier", format="%.2f", step=0.1),
            "sort_order": st.column_config.NumberColumn("Sort Order", format="%d", step=1),
        },
    )

    if st.button("Save Options", key="save_options"):
        key_cols = ["workload", "option_group", "label"]
        mult_changes = list(_diff_value(view, edited, key_cols, "multiplier"))
        sort_changes = list(_diff_value(view, edited, key_cols, "sort_order"))

        # Combine into the (w, g, l, mult, sort_order) tuples that the writer expects.
        # For rows changed in both, take the new values from `edited`; for rows changed
        # in only one column, carry the unchanged column forward from `view`.
        changed_keys = {k for k, _ in mult_changes} | {k for k, _ in sort_changes}
        updates = []
        for k in changed_keys:
            row = edited.merge(
                pd.DataFrame([k], columns=key_cols), on=key_cols
            ).iloc[0]
            updates.append((row["workload"], row["option_group"], row["label"],
                            float(row["multiplier"]), int(row["sort_order"])))

        if not updates:
            st.info("No changes to save.")
            return
        db_config.save_option_values(updates)
        st.cache_data.clear()
        st.success(f"Saved {len(updates)} option change(s).")
        st.rerun()


def show_configure_page():
    st.title("Configure Pricing Tables")
    st.write(
        "Adjust the rates, per-workload constants, and dropdown multipliers stored in "
        "the Lakebase `cost_estimator.*` tables. Saved changes take effect immediately "
        "for every user of this app."
    )

    rates_tab, constants_tab, options_tab = st.tabs(
        ["Rates", "Workload Constants", "Workload Options"]
    )
    with rates_tab:
        _show_rates_editor()
    with constants_tab:
        _show_constants_editor()
    with options_tab:
        _show_options_editor()
