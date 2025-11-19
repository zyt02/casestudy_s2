import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import CSS
import math

st.set_page_config(
    page_title="Forecast Analysis - Store Closure",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CSS, unsafe_allow_html=True)

st.title("Forecast Analysis")

st.markdown("""
This page presents the Q4 2022 Brand Comparable Sales Growth forecast analysis using regression-based 
and bias-adjusted methods.
""")



# FORECAST RESULTS
st.markdown("### Q4 2022 Forecast Results")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Regression-Based Forecast",
        "-9.74%",
        help="Forecast using linear regression model"
    )

with col2:
    # 95% Confidence Interval from regression model prediction
    # Values from forecast_case.ipynb last cell output
    ci_lower = -0.141  # Lower bound (95% CI)
    ci_upper = -0.053  # Upper bound (95% CI)
    st.metric(
        "95% Confidence Interval",
        f"[{ci_lower*100:.2f}%, {ci_upper*100:.2f}%]",
        help="95% confidence interval for the forecast"
    )

st.divider()


# CALIBRATION METRICS
st.markdown("### Model Calibration Metrics")

# Sample calibration data (based on notebook results)
calibration_data = {
    "quarter_end_dt": [
        "2020-12-31", "2021-03-31", "2021-06-30", "2021-09-30",
        "2021-12-31", "2022-03-31", "2022-06-30", "2022-09-30"
    ],
    "sample_yoy": [-0.052056, 0.348227, 1.206119, 0.101995, 0.147930, 0.036052, -0.106425, -0.127600],
    "reported_yoy": [-0.059, 0.359, 1.183, 0.075, 0.178, 0.021, -0.056, -0.032]
}

calib_df = pd.DataFrame(calibration_data)
calib_df["quarter_end_dt"] = pd.to_datetime(calib_df["quarter_end_dt"])

# Calculate metrics
correlation = calib_df["sample_yoy"].corr(calib_df["reported_yoy"])
bias = (calib_df["reported_yoy"] - calib_df["sample_yoy"]).mean()

def rmse(pred, true):
    return math.sqrt(((pred - true) ** 2).mean())

rmse_value = rmse(calib_df["sample_yoy"], calib_df["reported_yoy"])

# Regression model (simplified - using the coefficients from notebook)
# y = 0.0234 + 0.9533 * sample_yoy
calib_df["pred_from_model"] = 0.0234 + 0.9533 * calib_df["sample_yoy"]
rmse_reg = rmse(calib_df["pred_from_model"], calib_df["reported_yoy"])

col_met1, col_met2 = st.columns(2)

with col_met1:
    st.metric("RMSE (Raw)", f"{rmse_value:.4f}", help="Root Mean Squared Error using raw sample")

with col_met2:
    st.metric("RMSE (Regression)", f"{rmse_reg:.4f}", help="Root Mean Squared Error using regression model")



# VISUALIZATIONS
tab1, tab2 = st.tabs([" Actual vs Fitted", " Residuals"])

with tab1:
    st.markdown("#### Regression: Actual vs Fitted")
    
    # Q4 2022 forecast data
    q4_2022_date = pd.Timestamp("2022-12-31")
    q4_regression_forecast = -0.0974  # -9.74%
    
    fig_fitted = go.Figure()
    
    fig_fitted.add_trace(go.Scatter(
        x=calib_df["quarter_end_dt"],
        y=calib_df["reported_yoy"] * 100,
        mode='lines+markers',
        name='Actual Reported YoY',
        line=dict(color='#2ca02c', width=2),
        marker=dict(size=8, symbol='circle')
    ))
    
    fig_fitted.add_trace(go.Scatter(
        x=calib_df["quarter_end_dt"],
        y=calib_df["pred_from_model"] * 100,
        mode='lines+markers',
        name='Fitted (Regression)',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        marker=dict(size=8, symbol='x')
    ))
    
    # Add Q4 2022 regression-based forecast
    fig_fitted.add_trace(go.Scatter(
        x=[q4_2022_date],
        y=[q4_regression_forecast * 100],
        mode='markers',
        name='Q4 2022 Forecast (Regression-Based)',
        marker=dict(size=14, color='#9467bd', symbol='diamond', line=dict(width=2, color='white')),
        showlegend=True
    ))

    
    fig_fitted.update_layout(
        title="Regression: Actual vs Fitted Brand Comparable Sales YoY (with Q4 2022 Forecast)",
        xaxis_title="Quarter End Date",
        yaxis_title="YoY Comparable Sales (%)",
        hovermode='x unified',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_fitted, use_container_width=True)
    
    st.markdown("""

    - **Regression Model**: `reported_yoy = 0.0234 + 0.9533 × sample_yoy`
    - **R-squared**: 0.992

    """)

with tab2:
    st.markdown("#### Regression Residuals Over Time")
    
    calib_df["residual"] = (calib_df["reported_yoy"] - calib_df["pred_from_model"]) * 100
    
    fig_resid = go.Figure()
    
    fig_resid.add_trace(go.Scatter(
        x=calib_df["quarter_end_dt"],
        y=calib_df["residual"],
        mode='lines+markers',
        name='Residuals',
        line=dict(color='#d62728', width=2),
        marker=dict(size=8)
    ))
    
    fig_resid.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
        annotation_text="Zero Line"
    )
    
    fig_resid.update_layout(
        title="Regression Residuals Over Time",
        xaxis_title="Quarter End Date",
        yaxis_title="Residual (Actual - Fitted) (%)",
        hovermode='x unified',
        height=350
    )
    
    st.plotly_chart(fig_resid, use_container_width=True)
    
    st.markdown("""
    **Residual Analysis**: The residuals show the difference between actual reported values and 
    model predictions. Values close to zero indicate good model fit.
    """)

st.divider()


# CALIBRATION TABLE
st.markdown("### Calibration Data by Quarter")

display_calib = calib_df.copy()
display_calib["quarter_end_dt"] = display_calib["quarter_end_dt"].dt.strftime("%Y-%m-%d")
display_calib["sample_yoy_pct"] = (display_calib["sample_yoy"] * 100).round(2)
display_calib["reported_yoy_pct"] = (display_calib["reported_yoy"] * 100).round(2)
display_calib["pred_from_model_pct"] = (display_calib["pred_from_model"] * 100).round(2)
display_calib["residual_pct"] = ((display_calib["reported_yoy"] - display_calib["pred_from_model"]) * 100).round(2)

st.dataframe(
    display_calib[["quarter_end_dt", "sample_yoy_pct", "reported_yoy_pct", "pred_from_model_pct", "residual_pct"]].rename(columns={
        "quarter_end_dt": "Quarter End",
        "sample_yoy_pct": "Sample YoY (%)",
        "reported_yoy_pct": "Reported YoY (%)",
        "pred_from_model_pct": "Regression-based YoY (%)",
        "residual_pct": "Residual (%)"
    }),
    use_container_width=True,
    height=300
)

