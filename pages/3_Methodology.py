import streamlit as st
import pandas as pd
from utils import load_data, get_cluster_order, CSS

st.set_page_config(
    page_title="Methodology - Store Closure Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CSS, unsafe_allow_html=True)


st.title("Store Closure Analysis Methodology")

st.markdown("""
This analysis uses K-Means clustering to identify stores that are likely candidates for closure 
based on their characteristics, market positioning, and geographic footprint.
""")


with st.expander("1. Data Processing", expanded=True):
    st.markdown("""
    **Feature Engineering:**
    
    The `store_services` column contained long descriptive strings, so I parsed it into binary indicator columns 
    (e.g., whether a store is Next Gen, has curbside pickup, same-day delivery, etc.).
    
    **Distance Calculations:**
    
    - I calculated each store's distance to its nearest Party City store, which helps measure market density and 
      cannibalization risk.
    
    - I also computed the number of other stores within 3 and 6 miles, giving a clear view of how overlapped or 
      isolated each store is.
    
    **Key Features Created:**
    - `has_next_gen`: Binary indicator for Next Generation store format
    - `is_flagship`: Binary indicator for flagship locations
    - `num_omni_features`: Count of omni-channel services (pickup, curbside, same-day, balloon delivery)
    - `nearest_neighbor_miles`: Distance to closest Party City store
    - `stores_within_3_miles`: Count of stores within 3 miles
    - `stores_within_6_miles`: Count of stores within 6 miles
    """)


with st.expander("2. Fitting the Model", expanded=False):
    st.markdown("""
    **Feature Selection:**
    
    I selected meaningful features that capture store format quality, service capability, and local market density:
    
    **Store Quality & Services:**
    - `has_next_gen`: Next Generation store format indicator
    - `is_flagship`: Flagship location indicator
    - `num_omni_features`: Number of omni-channel service capabilities
    
    **Market Density:**
    - `nearest_neighbor_miles`: Distance to nearest competitor store
    - `stores_within_3_miles`: Market saturation within 3 miles
    - `stores_within_6_miles`: Market saturation within 6 miles
    
    **Clustering Algorithm:**
    
    Using these features, I ran **K-Means clustering** to group stores into distinct, interpretable store types. 
    The features were standardized using StandardScaler to ensure equal weighting in the clustering process.
    """)


with st.expander("3. Choosing the Number of Clusters", expanded=False):
    st.markdown("""
    **Evaluation Methods:**
    
    I evaluated different values of k using two methods:
    
    1. **Elbow Method**: The Elbow plot shows diminishing improvements after k = 4 (even though there is a drop 
       at 6–7, it likely reflects over-segmentation).
    
    2. **Silhouette Score**: The Silhouette Score peaks at k = 4, indicating it produces the most coherent and 
       separated clusters.
    
    **Final Selection:**
    
    To balance statistical fit with business interpretability, I selected **k = 4** as the optimal number of clusters.
    
    **Cluster Interpretations:**
    - **Best stores**: High-performing stores with strong omni-channel capabilities
    - **Middle Tier**: Average-performing stores with moderate capabilities
    - **Redundant**: Stores with high geographic overlap
    - **Weaker Store**: Underperforming stores with limited capabilities
    """)


with st.expander("4. Cluster Profiles & Feature Analysis", expanded=False):
    df = load_data("closure_strategy.csv")
    cluster_order = get_cluster_order()
    
    cluster_features = [
        "has_next_gen",
        "is_flagship",
        "num_omni_features",
        "nearest_neighbor_miles",
        "stores_within_3_miles",
        "stores_within_6_miles",
    ]
    
    usable_features = [c for c in cluster_features if c in df.columns]
    
    if usable_features:
        feature_name_map = {
            "has_next_gen": "Next Gen Store",
            "is_flagship": "Flagship Store",
            "num_omni_features": "Number of Omni Features",
            "nearest_neighbor_miles": "Nearest Neighbor (miles)",
            "stores_within_3_miles": "Stores Within 3 Miles",
            "stores_within_6_miles": "Stores Within 6 Miles"
        }
        
        col_mean, col_median = st.columns(2)
        
        with col_mean:
            st.markdown("#### Mean Values")
            cluster_mean = (
                df.groupby("cluster_label")[usable_features]
                .mean()
                .round(3)
                .reindex(cluster_order)
            )
            cluster_mean_display = cluster_mean.rename(columns=feature_name_map)
            st.dataframe(cluster_mean_display, use_container_width=True)
        
        with col_median:
            st.markdown("#### Median Values")
            cluster_median = (
                df.groupby("cluster_label")[usable_features]
                .median()
                .round(3)
                .reindex(cluster_order)
            )
            cluster_median_display = cluster_median.rename(columns=feature_name_map)
            st.dataframe(cluster_median_display, use_container_width=True)
        
        st.markdown("""
        **Feature Descriptions:**
        
        - **has_next_gen**: Whether the store is a Next Generation store format
        - **is_flagship**: Whether the store is a flagship location
        - **num_omni_features**: Number of additional services available (e.g., in-store pickup, curbside, same-day delivery, balloon delivery)
        - **nearest_neighbor_miles**: Distance in miles to the nearest other Party City store
        - **stores_within_3_miles**: Number of other Party City stores within 3 miles
        - **stores_within_6_miles**: Number of other Party City stores within 6 miles
        """)


with st.expander("5. Closure Recommendations Logic", expanded=False):
    st.markdown("""
    **Priority 1: Weaker Stores**
    
    These stores are identified for closure because they:
    - Lack modern store formats (Next Gen or flagship)
    - Have limited omni-channel capabilities
    - Underperform relative to other stores in the network
    - Represent the lowest-performing segment
    
    **Priority 2: Redundant Stores**
    
    These stores are identified for closure because they:
    - Have high geographic overlap with nearby stores (within 3-6 miles)
    - Create market cannibalization
    - Can be consolidated without losing market coverage
    - Represent inefficient geographic footprint
    
    **Evaluation: Middle Tier Stores**
    
    Middle Tier stores should be evaluated on a case-by-case basis:
    - Some may be candidates for closure if they're in saturated markets
    - Others may be candidates for upgrade to improve performance
    - Geographic context and local market conditions should be considered
    """)

st.markdown("""
**Note**: This analysis provides data-driven recommendations. Final closure decisions should consider 
additional factors such as lease terms, local market conditions, and strategic business objectives.
""")

st.divider()

st.title("Forecast Analysis Methodology")

with st.expander("Data Processing", expanded=False):
    st.markdown("""
    ### 1. Data Processing
    
    **Quarterly Sales Aggregation:**
    - Monthly transaction data is aggregated to quarterly sales per store
    - Each quarter is matched with its prior-year quarter (same calendar quarter, one year before)
    - Only quarters with full 3 months of sales data are included
    
    **Comparable Store Definition:**
    A store is considered "comparable" if it meets all of the following criteria:
    - Has prior-year quarter sales data available
    - Has 3 months of sales in both current and prior-year quarters
    - Store was open before the prior-year quarter started
    - Store was not closed before the current quarter ended
    """)
    
with st.expander("Same-Store Sales Calculation", expanded=False):
    st.markdown("""
    ### 2. Same-Store Sales (SSS) Calculation
    
    **Quarter-Level SSS YoY:**
    - For each quarter, sum sales across all comparable stores for current and prior-year periods
    - Calculate: `SSS YoY = (Current Quarter Sales / Prior Year Quarter Sales) - 1`
    - This provides a sample-based estimate of Brand Comparable Sales Growth 
    """)

 
with st.expander("Model Calibration", expanded=False):
    st.markdown(
    """### 3. Model Calibration
    
    **Calibration Process:**
    - Compare sample SSS YoY against reported Brand Comparable Sales Growth
    - Calculate correlation, bias, and RMSE metrics
    - Use historical quarters (2020 Q4 through 2022 Q3) for calibration
    
    **Key Metrics:**
    - **Correlation**: Measures linear relationship strength (target: >0.95)
    - **Bias**: Average difference between reported and sample (used for bias adjustment)
    - **RMSE**: Root Mean Squared Error (measures prediction accuracy)
   """)

with st.expander("Forecasting Methods", expanded=False):
    st.markdown(
    """### 4. Forecasting Methods
    
    **Method 1: Bias-Adjusted Forecast**
    - Formula: `Forecast = Sample YoY + Average Bias`
    - Simple adjustment based on historical mean difference
    
    **Method 2: Regression-Based Forecast**
    - Build linear regression: `reported_yoy = α + β × sample_yoy`
    - Use regression coefficients to predict from sample YoY
    - Provides more sophisticated adjustment that accounts for scale differences
    """)

with st.expander("Results", expanded=False):
    st.markdown(
    """
    | Method           | What It Uses                                         | Value                                    | 
| -------------------- | ---------------------------------------------------- | ---------------------------------------- |
| **Sample-Only**      | Raw transaction data                                 | -12.68%                                  | 
| **Regression-Based** | Historical mapping between sample YoY → reported YoY | -9.74%                                   | 
| **Bias-Adjusted**    | Regression output + historical error correction      | -11.24% | 

    **Forecast Process:**
    1. Calculate Q4 2022 sample SSS YoY from 655 comparable stores
    2. Apply both bias-adjusted and regression-based methods
    3. Report forecast range with methodology notes
    
    **Model Quality:**
    - R-squared: 0.992 (excellent fit)
    - High correlation (0.996) between sample and reported
    - Low RMSE indicates strong predictive power
    """)

st.divider()