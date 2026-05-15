from src import landing_page
import streamlit as st
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


st.set_page_config(
    page_title="PDS Fraud Detection System",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'landing'

    if st.session_state['page'] == 'landing':
        landing_page.render()
    elif st.session_state['page'] == 'dashboard':
        st.title("Dashboard Placeholder")
        st.info("The Dashboard is currently being rebuilt. Click below to return.")
        if st.button("Back to Home"):
            st.session_state['page'] = 'landing'
            st.rerun()


if __name__ == "__main__":
    main()
