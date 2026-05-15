import streamlit as st
from src import landing_page, dashboard, map_view, inspector, components, data_manager, ml_engine

# Page Config
st.set_page_config(
    page_title="PDS Fraud Detection System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # --- STATE INITIALIZATION ---
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'Home'
    
    if 'final_df' not in st.session_state:
        st.session_state['final_df'] = None
    
    # --- SMART LOADING BLOCK ---
    # Check if we need to load/process data
    uploaded_file = st.session_state.get('uploaded_file', None)
    
    # Only compute if we don't have data yet, or if file changed
    if st.session_state['final_df'] is None:
        with st.spinner('Loading and processing data...'):
            # Load data (already includes ML fraud detection internally)
            processed_df = data_manager.load_data(uploaded_file)
            
            # Store in session state for instant access
            st.session_state['final_df'] = processed_df
    
    # --- NAVIGATION ---
    # Render navbar (sticky header)
    current_page = components.navbar()
    
    # --- PAGE ROUTING ---
    # All pages now use st.session_state['final_df'] - zero latency!
    if current_page == 'Home':
        landing_page.render()
    elif current_page == 'Dashboard':
        dashboard.render()
    elif current_page == 'Live Map':
        map_view.render()
    elif current_page == 'Shop Inspector':
        inspector.render()
    else:
        # Fallback to home
        landing_page.render()

if __name__ == "__main__":
    main()
