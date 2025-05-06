import streamlit as st
st.set_page_config(
    page_title="网易云用户行为分析平台",
    layout="wide",
    initial_sidebar_state="expanded"
)

from top_nav import main_page
main_page()
