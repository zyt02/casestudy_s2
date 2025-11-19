import streamlit as st
import pandas as pd

# Global CSS
CSS = """
<style>
    .cluster-card {
        padding: 10px 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        text-align: center;
    }
    .cluster-title {
        font-size: 1.0rem;
        font-weight: 600;
        margin-bottom: 2px;
    }
    .cluster-count {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    .cluster-percent {
        font-size: 0.85rem;
        color: #555;
        margin-top: 2px;
    }
    .headline-metric {
        font-size: 2.0rem;
        font-weight: 700;
        margin: 0;
    }
    .headline-label {
        font-size: 0.9rem;
        color: #666;
    }
    .filter-badge {
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .reason-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #d62728;
        margin: 10px 0;
    }
</style>
"""

@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    """Load and process data from CSV"""
    df = pd.read_csv(csv_path)
    df.columns = [c.lower().strip() for c in df.columns]
    
    if "cluster_label" not in df.columns and "cluster" in df.columns:
        cluster_name_map = {
            0: "Middle Tier",
            1: "Weaker Store",
            2: "Best stores",
            3: "Redundant"
        }
        df["cluster_label"] = df["cluster"].map(cluster_name_map)

    return df

def get_cluster_order():
    return [
        "Best stores",
        "Middle Tier",
        "Redundant",
        "Weaker Store",
    ]

def get_color_map():
    return {
        "Weaker Store": "#d62728",
        "Middle Tier": "#1f77b4",
        "Best stores": "#2ca02c",
        "Redundant": "#ff7f0e",
    }

