import streamlit as st
from utils import CSS

st.set_page_config(
    page_title="Case Study Results",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CSS, unsafe_allow_html=True)


# Home page content
st.title(" Case Study Results")

st.markdown("""
## Welcome

This application presents the results of case study on Party City.
Use the sidebar to navigate between pages:

- **Store Closure Analysis**: View store closure recommendations, analyze at-risk stores, and explore geographic patterns
- **Forecast Analysis** : View forecast analysis results
- **Methodology**: Data processing, forecasting or clustering approach, and analytical methods used


""")


