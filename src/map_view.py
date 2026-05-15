import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
from src import components

def render():
    components.inject_tailwind()
    # Navbar handled in app.py
    
    st.markdown("<div class='h-8'></div>", unsafe_allow_html=True)
    
    st.markdown("### 📍 Live Geospatial Intelligence (Delhi NCT)")
    
    # Load data from session state
    df = st.session_state.get('final_df', None)
    
    if df is None:
        st.warning("No data available. Please upload a file or generate demo data from the landing page.")
        return
    
    # Verify required columns exist
    if 'Lat' not in df.columns or 'Lon' not in df.columns:
        st.error("Data missing geographic coordinates (Lat/Lon). Cannot display map.")
        return
    
    # Prepare map data from actual dataset
    # Aggregate by shop to get shop-level metrics
    shop_data = df.groupby('ShopID').agg({
        'Lat': 'first',
        'Lon': 'first',
        'Risk_Score': 'mean',
        'Status': lambda x: 'Critical' if (x == 'Fraud').any() else 'Normal',
        'Amount': 'sum'
    }).reset_index()
    
    # Add visual properties
    shop_data['color'] = shop_data['Status'].apply(
        lambda x: [255, 0, 0, 200] if x == 'Critical' else [0, 255, 0, 150]
    )
    shop_data['radius'] = (shop_data['Amount'] / shop_data['Amount'].max() * 1000).fillna(100)
    shop_data['Risk Score'] = shop_data['Risk_Score'].round(0).astype(int)
    shop_data['Total Amount'] = shop_data['Amount'].round(0).astype(int)
    
    # PyDeck Map
    # Calculate center from data
    center_lat = shop_data['Lat'].mean()
    center_lon = shop_data['Lon'].mean()
    
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=10,
        pitch=40,
    )
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        shop_data,
        get_position=["Lon", "Lat"],
        get_color="color",
        get_radius="radius",
        pickable=True,
        auto_highlight=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=6,
        radius_min_pixels=5,
        radius_max_pixels=50,
    )
    
    tooltip = {
        "html": "<b>{ShopID}</b><br/>Risk Score: {Risk Score}<br/>Total Amount: ₹{Total Amount}",
        "style": {"backgroundColor": "white", "color": "black"}
    }
    
    st.pydeck_chart(
        pdk.Deck(
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip
        ),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Drill Down Interaction
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.info("Select a shop to view risk details.")
        shop_list = sorted(shop_data['ShopID'].tolist())
        selected_shop = st.selectbox("Inspect Specific Shop", shop_list)
        
        # Display selected shop stats
        shop_row = shop_data[shop_data['ShopID'] == selected_shop].iloc[0]
        color = "red" if shop_row['Status'] == 'Critical' else "green"
        components.metric_card("Current Risk Score", f"{shop_row['Risk Score']}", color=color)
        
    with c2:
        st.markdown(f"#### Transaction History: {selected_shop}")
        
        # Get actual transactions for selected shop
        shop_txns = df[df['ShopID'] == selected_shop].copy()
        
        if 'Timestamp' in shop_txns.columns:
            shop_txns['Timestamp'] = pd.to_datetime(shop_txns['Timestamp'], errors='coerce')
            shop_txns = shop_txns.sort_values('Timestamp')
            
            # Aggregate by date
            daily = shop_txns.groupby(shop_txns['Timestamp'].dt.date).size().reset_index()
            daily.columns = ['Date', 'Transactions']
            
            st.line_chart(daily.set_index('Date'))
        else:
            st.info("No timestamp data available for transaction history.")

