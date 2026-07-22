"""
NPA EWS Streamlit frontend.

A thin client of the FastAPI backend (src/npa_ews/api.py) over real
HTTP -- this file never imports npa_ews internals directly. Run the
backend first (`npa-ews serve`), then:

    streamlit run frontend/app.py
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import client

st.set_page_config(page_title="NPA Early Warning System", layout="wide")

# ── Sidebar: backend connection ─────────────────────────────────────
st.sidebar.title("NPA EWS")
base_url = st.sidebar.text_input("API base URL", value="http://127.0.0.1:8000").rstrip("/")

try:
    health = client.health(base_url)
    st.sidebar.success(f"Connected — status: {health.get('status')}")
    connected = True
except client.ApiError as exc:
    st.sidebar.error(f"Cannot reach API.\n\n{exc}\n\nStart it with `npa-ews serve`.")
    connected = False

st.sidebar.markdown("---")
st.sidebar.caption(
    "This system's value is driver identification and probabilistic scenario "
    "risk, not point forecasting — see the Validation tab before trusting any "
    "single number."
)

st.title("RBI NPA Early Warning System")
st.caption("SupTech prototype — driver identification, out-of-sample validation, and probabilistic macro stress testing.")

if not connected:
    st.stop()

tab_drivers, tab_validation, tab_stress, tab_custom = st.tabs(
    ["Drivers", "Validation", "Predefined Scenarios", "Custom Scenario + Narrative"]
)

# ── Tab 1: Drivers ───────────────────────────────────────────────────
with tab_drivers:
    st.subheader("What moves GNPA? Two independent methods, compared")
    drivers_data = client.get_drivers(base_url)
    df = pd.DataFrame(drivers_data["drivers"])

    col1, col2 = st.columns(2)
    col1.metric("Fixed Effects R² (within)", f"{drivers_data['fe_r_squared_within']:.3f}")
    col2.metric("Observations (n)", drivers_data["fe_n_obs"])

    fig = go.Figure()
    fig.add_bar(name="FE coefficient (|value|)", x=df["label"], y=df["fe_coefficient"].abs())
    fig.add_bar(name="SHAP importance", x=df["label"], y=df["shap_importance"])
    fig.update_layout(barmode="group", yaxis_title="Magnitude", legend_title="Method")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.info(drivers_data["note"])

# ── Tab 2: Validation ────────────────────────────────────────────────
with tab_validation:
    st.subheader('Is this actually worth it? — Walk-forward CV vs. naive baselines')
    val = client.get_validation(base_url)
    comp_df = pd.DataFrame(val["baseline_comparison"]).sort_values("mae_mean")

    fig = px.bar(
        comp_df, x="model", y="mae_mean", error_y="mae_std",
        labels={"mae_mean": "Mean Absolute Error (pp)", "model": ""},
        color="model",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    st.warning(val["note"])

    st.subheader("Data reliability by bank group")
    rel = pd.DataFrame(client.get_reliability(base_url))
    rel["flag"] = rel["reliable"].map({True: "✅ reliable", False: "⚠️ LOW CONFIDENCE"})
    st.dataframe(rel[["bank_group", "n_obs", "year_min", "year_max", "flag"]], use_container_width=True, hide_index=True)

# ── Tab 3: Predefined scenarios ──────────────────────────────────────
with tab_stress:
    st.subheader("Macro stress test — predefined historical scenarios")
    n_boot = st.slider("Bootstrap resamples", 50, 2000, 300, step=50, key="predefined_n_boot")
    stress_data = client.get_stress(base_url, n_boot=n_boot)
    results_df = pd.DataFrame(stress_data["results"])

    scenario_names = results_df["scenario"].unique().tolist()
    selected_scenario = st.selectbox("Scenario", scenario_names, index=len(scenario_names) - 1)
    scenario_df = results_df[results_df["scenario"] == selected_scenario].copy()

    fig = go.Figure()
    fig.add_bar(
        x=scenario_df["bank_group"],
        y=scenario_df["point"],
        error_y=dict(
            type="data",
            symmetric=False,
            array=scenario_df["upper"] - scenario_df["point"],
            arrayminus=scenario_df["point"] - scenario_df["lower"],
        ),
        marker_color=["#e74c3c" if "LOW" in c else "#3498db" for c in scenario_df["data_confidence"]],
    )
    fig.add_hline(y=stress_data["threshold"], line_dash="dash", line_color="black",
                  annotation_text=f"PCA Threshold ({stress_data['threshold']}%)")
    fig.update_layout(yaxis_title="Projected GNPA (%) with 90% CI")
    st.plotly_chart(fig, use_container_width=True)

    display_df = scenario_df[["bank_group", "point", "lower", "upper", "breach_probability", "data_confidence"]]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.caption("Red bars = LOW CONFIDENCE bank groups (PSB, SFB — n=4). Dashed line = PCA Risk Threshold 1.")

# ── Tab 4: Custom scenario + narrative ───────────────────────────────
with tab_custom:
    st.subheader("Build your own macro shock")
    c1, c2 = st.columns(2)
    with c1:
        gdp_shock = st.slider("GDP growth shock (pp)", -8.0, 4.0, -2.5, step=0.1)
        repo_shock = st.slider("Repo rate shock (pp)", -2.0, 3.0, 1.0, step=0.1)
    with c2:
        credit_shock = st.slider("Credit growth (t-2) shock (pp)", -12.0, 6.0, -5.0, step=0.5)
        roa_shock = st.slider("ROA shock (pp)", -1.5, 0.5, -0.3, step=0.05)

    custom_n_boot = st.slider("Bootstrap resamples", 50, 2000, 300, step=50, key="custom_n_boot")

    if st.button("Run custom stress test", type="primary"):
        with st.spinner("Running bootstrap stress test..."):
            custom_result = client.post_custom_stress(
                base_url, gdp_shock, repo_shock, credit_shock, roa_shock, n_boot=custom_n_boot
            )
        st.session_state["custom_result"] = custom_result

    if "custom_result" in st.session_state:
        cr_df = pd.DataFrame(st.session_state["custom_result"]["results"])
        fig = go.Figure()
        fig.add_bar(
            x=cr_df["bank_group"], y=cr_df["point"],
            error_y=dict(
                type="data", symmetric=False,
                array=cr_df["upper"] - cr_df["point"], arrayminus=cr_df["point"] - cr_df["lower"],
            ),
            marker_color=["#e74c3c" if "LOW" in c else "#3498db" for c in cr_df["data_confidence"]],
        )
        fig.add_hline(y=6.0, line_dash="dash", line_color="black", annotation_text="PCA Threshold (6.0%)")
        fig.update_layout(yaxis_title="Projected GNPA (%) with 90% CI")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(cr_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Generate a plain-English risk narrative")
        bank_choice = st.selectbox("Bank group", cr_df["bank_group"].tolist())
        if st.button("Generate narrative"):
            with st.spinner("Calling LLM..."):
                narr = client.post_narrative(
                    base_url, bank_choice,
                    gdp_shock=gdp_shock, repo_shock=repo_shock,
                    credit_shock=credit_shock, roa_shock=roa_shock,
                    n_boot=custom_n_boot,
                )
            if narr["generated"]:
                st.success(narr["narrative"])
                st.caption(f"Generated by {narr['model']}")
            else:
                st.info(narr["narrative"])
    else:
        st.caption("Run a custom stress test above to enable narrative generation.")
