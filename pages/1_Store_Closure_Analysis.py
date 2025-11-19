import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, get_cluster_order, get_color_map, CSS

st.set_page_config(
    page_title="Store Closure Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CSS, unsafe_allow_html=True)



st.title("Store Closure Analysis")

df = load_data("closure_strategy.csv")
cluster_order = get_cluster_order()
color_map = get_color_map()

df["cluster_label"] = pd.Categorical(df["cluster_label"], categories=cluster_order, ordered=True)

total_stores = len(df)
cluster_count = df["cluster_label"].value_counts().reindex(cluster_order).fillna(0).astype(int)
cluster_pct = (cluster_count / total_stores * 100).round(1)

at_risk_clusters = ["Redundant", "Weaker Store"]
at_risk_count = cluster_count.loc[at_risk_clusters].sum()
at_risk_pct = (at_risk_count / total_stores * 100).round(1)

col_summary, col_metrics = st.columns([2, 1])

with col_summary:
    st.markdown("### Which Stores Will Close?")
    st.markdown(
        f"""
        <p class="headline-metric">{at_risk_count} stores ({at_risk_pct}%)</p>
        <p class="headline-label">
            are <b>high-priority candidates</b> for closure evaluation.
        </p>
        """,
        unsafe_allow_html=True,
    )

with col_metrics:
    st.metric("Total Stores", total_stores)
    st.metric("At Risk Stores", at_risk_count)

# Cluster cards in a row
st.markdown("#### Store Clusters")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="cluster-card" style="background-color:#e8f5e9;">
            <div class="cluster-title" style="color:#2ca02c;">Best Stores</div>
            <div class="cluster-count">{cluster_count['Best stores']}</div>
            <div class="cluster-percent">{cluster_pct['Best stores']}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="cluster-card" style="background-color:#e3f2fd;">
            <div class="cluster-title" style="color:#1f77b4;">Middle Tier</div>
            <div class="cluster-count">{cluster_count['Middle Tier']}</div>
            <div class="cluster-percent">{cluster_pct['Middle Tier']}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class="cluster-card" style="background-color:#fff3e0;">
            <div class="cluster-title" style="color:#ff7f0e;">Redundant</div>
                    <div class="cluster-count">{cluster_count['Redundant']}</div>
                    <div class="cluster-percent">{cluster_pct['Redundant']}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        f"""
        <div class="cluster-card" style="background-color:#ffebee;">
            <div class="cluster-title" style="color:#d62728;">Weaker</div>
                    <div class="cluster-count">{cluster_count['Weaker Store']}</div>
                    <div class="cluster-percent">{cluster_pct['Weaker Store']}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()


st.markdown("### Why These Stores Will Close")

tab1, tab2, tab3 = st.tabs(["Overview", "Geographic Analysis", "Store Details"])

with tab1:
    st.markdown("#### Closure Reasons by Cluster")
    
    col_reason1, col_reason2 = st.columns(2)
    
    with col_reason1:
        st.markdown(
            """
            <div class="reason-box">
                <h4 style="color:#d62728; margin-top:0;"> Weaker Stores</h4>
                <ul style="margin-bottom:0;">
                    <li>Lack of omni-channel capabilities (i.e. in-store pickup, same-day delivery) </li>
                    <li>Lack Next Gen or flagship features</li>
                    <li>Limited service offering (i.e. ballon delivery)</li>
                    <li>Low competitive positioning</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with col_reason2:
        st.markdown(
            """
            <div class="reason-box">
                <h4 style="color:#ff7f0e; margin-top:0;"> Redundant Stores</h4>
                <ul style="margin-bottom:0;">
                    <li>High market overlap with nearby stores</li>
                    <li>Cannibalization risk (stores within 3-6 miles)</li>
                    <li>Inefficient geographic footprint</li>
                    <li>Potential to consolidate without coverage loss</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
            "has_next_gen": "Next Gen (%)",
            "is_flagship": "Flagship (%)",
            "num_omni_features": "Omni Features (%)",
            "nearest_neighbor_miles": "Nearest Store (mi)",
            "stores_within_3_miles": "Stores < 3mi",
            "stores_within_6_miles": "Stores < 6mi"
        }
        
        cluster_mean = (
            df.groupby("cluster_label")[usable_features]
            .mean()
            .round(2)
            .reindex(cluster_order)
        )
        
        # Convert binary features to percentages
        if "has_next_gen" in cluster_mean.columns:
            cluster_mean["has_next_gen"] = cluster_mean["has_next_gen"] * 100
        if "is_flagship" in cluster_mean.columns:
            cluster_mean["is_flagship"] = cluster_mean["is_flagship"] * 100
        if "num_omni_features" in cluster_mean.columns:
            # Calculate percentage of stores with omni features (num_omni_features > 0)
            omni_pct = df.groupby("cluster_label").apply(
                lambda x: (x["num_omni_features"] > 0).mean() * 100 if "num_omni_features" in x.columns else 0
            ).reindex(cluster_order)
            cluster_mean["num_omni_features"] = omni_pct
        
        cluster_mean_display = cluster_mean.rename(columns=feature_name_map)
        
        # Apply color coding to specific rows
        def color_rows(row):
            cluster_name = row.name
            if cluster_name == "Redundant":
                return ['background-color: #fff3e0'] * len(row)  # Light orange
            elif cluster_name == "Weaker Store":
                return ['background-color: #ffebee'] * len(row)  # Light red
            else:
                return [''] * len(row)
        
        styled_df = cluster_mean_display.style.apply(color_rows, axis=1)
        
        st.markdown("#### Cluster Characteristics (Mean Values)")
        st.dataframe(styled_df, use_container_width=True)

with tab2:
    st.markdown("#### Store Geographic Distribution")
    
    if "latitude" in df.columns and "longitude" in df.columns:
        selected_clusters = st.multiselect(
            "Select clusters to display",
            options=cluster_order,
            default=at_risk_clusters,
            format_func=lambda x: f"{x}"
        )
        
        map_df = df[df["cluster_label"].isin(selected_clusters)]
        
        # Create figure with traces for each cluster with larger, more visible markers
        fig_map = go.Figure()
        
        for cluster in selected_clusters:
            cluster_data = map_df[map_df["cluster_label"] == cluster]
            if not cluster_data.empty:
                fig_map.add_trace(go.Scattermapbox(
                    lat=cluster_data["latitude"],
                    lon=cluster_data["longitude"],
                    mode='markers',
                    marker=dict(
                        size=18,  # Larger markers for better visibility
                        color=color_map[cluster],
                        opacity=0.9,  # Higher opacity for better visibility
                        symbol='circle'  # Use circle symbol
                    ),
                    name=cluster,  # Cluster name in legend
                    text=cluster_data["cluster_label"],
                    hovertemplate='<b>%{text}</b><br>' +
                                'Address: %{customdata[0]}<br>' +
                                'City: %{customdata[1]}<br>' +
                                'State: %{customdata[2]}<br>' +
                                'Nearest Store: %{customdata[3]:.2f} mi<extra></extra>',
                    customdata=cluster_data[["address", "city", "state", "nearest_neighbor_miles"]].values,
                    showlegend=True
                ))
        
        fig_map.update_layout(
            mapbox=dict(
                style="open-street-map",
                zoom=4,
                center=dict(
                    lat=map_df["latitude"].mean() if not map_df.empty else 39.5,
                    lon=map_df["longitude"].mean() if not map_df.empty else -98.5
                )
            ),
            height=500,
            legend=dict(
                title=dict(text="Cluster Labels", font=dict(size=11, color="black")),
                font=dict(size=9, color="black"),
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="black",
                borderwidth=1,
                x=1.01,
                y=1,
                xanchor="left",
                yanchor="top",
                itemsizing="constant"
            ),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Geographic data not available.")

with tab3:
    st.markdown("#### Store Details")
    
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        cluster_filter = st.selectbox(
            "Filter by cluster",
            options=["All"] + cluster_order,
            index=0,
        )
    
    with col_filter2:
        search_text = st.text_input(
            "Search stores",
            value="",
            placeholder="Address, city, state..."
        )
    
    detail_df = df.copy()
    
    if cluster_filter != "All":
        detail_df = detail_df[detail_df["cluster_label"] == cluster_filter]
    
    if search_text:
        detail_df = detail_df[
            detail_df.apply(
                lambda r: r.astype(str).str.contains(search_text, case=False).any(),
                axis=1,
            )
        ]
    
    preferred_cols = [
        "address",
        "city",
        "state",
        "cluster_label",
        "nearest_neighbor_miles",
        "stores_within_3_miles",
        "stores_within_6_miles",
        "num_omni_features",
        "has_next_gen",
        "is_flagship",
    ]
    
    final_cols = [c for c in preferred_cols if c in detail_df.columns]
    
    st.info(f"Showing **{len(detail_df)}** stores")
    st.dataframe(detail_df[final_cols], use_container_width=True, height=400)

