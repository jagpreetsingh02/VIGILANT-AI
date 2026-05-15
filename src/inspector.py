import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ast
from src import data_manager, components

def render():
    """
    PDS Shop Vigilance Portal - Fixed Data Leaking with Strict Separation & Anti-Gravity Logic.
    """
    components.inject_tailwind()
    
    # Hero Section
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0 3rem 0;'>
            <h1 style='font-size: 2.5rem; font-weight: 700; color: #0052cc; margin-bottom: 0.5rem;'>
                🔍 PDS Shop Vigilance Portal
            </h1>
            <p style='font-size: 1.1rem; color: #666;'>
                Advanced individual shop analysis and fraud investigation
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- 1. DATA PARTITIONING (The "Anti-Gravity" Split) ---
    # Load from session state (Optimized)
    df = st.session_state.get('final_df', None)
    
    if df is None:
        st.warning("No data available. Please upload a file or return to dashboard to generate data.")
        return

    # Ensure Flag_Reasons is properly formatted as list
    if 'Flag_Reasons' in df.columns:
        def parse_flag_reasons(val):
            if isinstance(val, list):
                return val
            elif isinstance(val, str):
                try:
                    return ast.literal_eval(val)
                except:
                    return [val] if val and val != 'Normal' else ['Normal']
            else:
                return ['Normal']
        
        df['Flag_Reasons'] = df['Flag_Reasons'].apply(parse_flag_reasons)

    # IMMEDIATELY create two separate, disjoint lists
    # Logic: Any shop with at least one 'Fraud' transaction is a FRAUD SHOP.
    # Safe shops must have ZERO fraud transactions.
    
    all_fraud_shops = set(df[df['Status'] == 'Fraud']['ShopID'].unique())
    all_normal_shops = set(df[df['Status'] == 'Normal']['ShopID'].unique())
    
    # Strict Mutual Exclusivity: Safe = Normal - Fraud
    fraud_shops = sorted(list(all_fraud_shops))
    safe_shops = sorted(list(all_normal_shops - all_fraud_shops))
    
    # --- 2. THE CATEGORY SELECTOR ---
    st.markdown("### Filter Shop Category")
    category = st.radio(
        "Select Category:",
        options=["🚨 High Risk Shops", "✅ Verified Shops"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Logic Branching
    if category == "🚨 High Risk Shops":
        if not fraud_shops:
            st.success("✅ Great work! No fraud detected in this dataset.")
            st.stop()
            
        active_list = fraud_shops
        dropdown_label = "Select a Flagged Shop"
        
    else:  # Verified Shops
        if not safe_shops:
            st.warning("⚠️ No verified safe shops found (Check data integrity).")
            st.stop()
            
        active_list = safe_shops
        dropdown_label = "Select a Verified Shop"
        
    # --- 3. THE INSPECTION DROPDOWN ---
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    
    # Create the dropdown using ONLY active_list
    selected_id = st.selectbox(
        dropdown_label, 
        active_list,
        help="Select a shop ID to view detailed evidence."
    )

    # --- 4. THE REPORT VIEW ---
    
    # Filter the Main Dataframe
    shop_df = df[df['ShopID'] == selected_id].copy()
    
    if shop_df.empty:
        st.error("Shop data not found.")
        return

    # For profile details, we check the global status based on our lists
    # Since lists are disjoint, we know exactly what this shop is.
    is_fraud_shop = (selected_id in fraud_shops)
    
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    # Header Badge logic
    if is_fraud_shop:
        status_color = "#ef4444"
        avg_risk = shop_df['Risk_Score'].mean()
        header_badge = f"CRITICAL RISK (Avg Score: {avg_risk:.0f})"
        header_icon = "🚨"
    else:
        status_color = "#10b981"
        header_badge = "VERIFIED SAFE"
        header_icon = "✅"
        
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, {status_color} 0%, {status_color}dd 100%); 
                    padding: 1.5rem; border-radius: 8px; color: white; margin-bottom: 2rem;'>
            <h2 style='margin: 0; font-size: 1.8rem; font-weight: 700;'>{header_icon} {selected_id}</h2>
            <h3 style='margin: 0.5rem 0 0 0; font-weight: 600; font-size: 1.1rem; opacity: 0.9;'>{header_badge}</h3>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📋 Evidence Locker")
        
        # Evidence Logic
        if is_fraud_shop:
            st.markdown("**Violations Detected:**")
            
            # Aggregate all flags for this shop
            all_flags = []
            for flag_list in shop_df['Flag_Reasons']:
                if isinstance(flag_list, list):
                    all_flags.extend([f for f in flag_list if f != 'Normal'])
            unique_flags = sorted(list(set(all_flags)))
            
            if unique_flags:
                # Use clean HTML without indentation to avoid raw text issue
                badges_html = '<div style="margin-top: 0.5rem; display: flex; flex-wrap: wrap; gap: 8px;">'
                for flag in unique_flags:
                    badges_html += f'<span style="background-color: #ffecec; color: #ef4444; border: 1px solid #ef4444; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">🚨 {flag}</span>'
                badges_html += '</div>'
                st.markdown(badges_html, unsafe_allow_html=True)
            else:
                st.warning("High risk detected but specific flags are ambiguous.")
        else:
            st.markdown("""
                <div style='background-color: #ecfdf5; border-left: 4px solid #10b981; padding: 1rem; border-radius: 4px;'>
                    <p style='color: #065f46; margin: 0; font-weight: 500;'>
                        Transaction patterns are within normal variance.
                        No anomalous velocity or pricing detected.
                    </p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 📊 Key Metrics")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Transactions", len(shop_df))
        with m2:
            vol = shop_df['Quantity_kg'].sum() if 'Quantity_kg' in shop_df.columns else 0
            st.metric("Volume", f"{vol:,.0f} kg")
        with m3:
            amt = shop_df['Amount'].sum() if 'Amount' in shop_df.columns else 0
            st.metric("Amount", f"₹{amt:,.0f}")

    # --- 5. METRICS & CHARTS ---
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 📈 Activity Series")
    
    if 'Timestamp' in shop_df.columns:
        shop_df['Timestamp'] = pd.to_datetime(shop_df['Timestamp'], errors='coerce')
        shop_df = shop_df.sort_values('Timestamp')
        
        fig = go.Figure()
        
        # Plot Logic
        if is_fraud_shop:
            # Show Fraud vs Normal points
            fraud_pts = shop_df[shop_df['Status'] == 'Fraud']
            normal_pts = shop_df[shop_df['Status'] == 'Normal']
            
            if not normal_pts.empty:
                fig.add_trace(go.Scatter(x=normal_pts['Timestamp'], y=normal_pts['Risk_Score'], mode='markers', name='Normal', marker=dict(color='#ccc', size=6)))
            if not fraud_pts.empty:
                fig.add_trace(go.Scatter(x=fraud_pts['Timestamp'], y=fraud_pts['Risk_Score'], mode='markers+lines', name='Fraud', line=dict(color='#ef4444'), marker=dict(color='#ef4444', size=8)))
        else:
            # Show Green Line
            fig.add_trace(go.Scatter(x=shop_df['Timestamp'], y=shop_df['Risk_Score'], mode='lines', name='Risk Score', line=dict(color='#10b981')))

        fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor='white', xaxis_title="Timestamp", yaxis_title="Risk Score")
        st.plotly_chart(fig, use_container_width=True)
    
    # Raw Logs
    st.markdown("---")
    with st.expander("📄 View Transaction Logs", expanded=False):
        # Format list columns for display
        display_df = shop_df.copy()
        if 'Flag_Reasons' in display_df.columns:
             display_df['Flag_Reasons'] = display_df['Flag_Reasons'].apply(lambda x: str(x) if isinstance(x, list) else str(x))
             
        st.dataframe(display_df, use_container_width=True, hide_index=True)
