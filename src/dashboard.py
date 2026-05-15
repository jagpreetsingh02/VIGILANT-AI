import streamlit as st
import pandas as pd
from src import data_manager, components


def clear_cache():
    """Clears cached data when new file is uploaded."""
    st.cache_data.clear()


def render():

    components.inject_tailwind()

    with st.sidebar:
        st.header("Data Controls")

        if 'uploaded_file' in st.session_state and st.session_state['uploaded_file'] is not None:
            st.info(
                f"📁 Using uploaded file: {st.session_state['uploaded_file'].name}")
            if st.button("Clear Uploaded File"):
                del st.session_state['uploaded_file']
                st.session_state['final_df'] = None
                st.rerun()

        template = data_manager.get_csv_template()
        csv = template.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="Download CSV Template",
            data=csv,
            file_name="pds_template_v2.csv",
            mime="text/csv",
            help="Download the required schema for uploading data."
        )

    df = st.session_state.get('final_df', None)

    if df is None:
        st.warning(
            "No data loaded. Please return to home and upload a file or generate demo data.")
        return

    total_scanned = len(df)
    fraud_df = df[df['Status'] == 'Fraud'].copy()
    fraud_detected = len(fraud_df)

    fraud_rate = (fraud_detected / total_scanned *
                  100) if total_scanned > 0 else 0

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
            <div style='background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                <h3 style='margin: 0; font-size: 0.9rem; color: #666; text-transform: uppercase;'>Total Scanned</h3>
                <h1 style='margin: 0.5rem 0; font-size: 2.5rem; font-weight: 700; color: #1f2937;'>{:,}</h1>
                <p style='margin: 0; color: #10b981; font-size: 0.85rem;'>🟢 Real-Time Buffer Active</p>
            </div>
        """.format(total_scanned), unsafe_allow_html=True)

    with col2:

        if fraud_rate < 2:
            bar_color = "success"  # Green
            health_label = "Healthy"
        elif fraud_rate < 5:
            bar_color = "warning"  # Yellow
            health_label = "Moderate"
        else:
            bar_color = "error"  # Red
            health_label = "Critical"

        st.markdown("""
            <div style='background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                <h3 style='margin: 0; font-size: 0.9rem; color: #666; text-transform: uppercase;'>Fraud Detected</h3>
                <h1 style='margin: 0.5rem 0; font-size: 2.5rem; font-weight: 700; color: #ef4444;'>{:,}</h1>
            </div>
        """.format(fraud_detected), unsafe_allow_html=True)

        # Health progress bar
        st.progress(min(fraud_rate / 100, 1.0),
                    text=f"Current Fraud Rate: {fraud_rate:.2f}% - {health_label}")

    st.markdown("<div class='h-8'></div>", unsafe_allow_html=True)

    # --- FRAUD ANALYTICS MODULE ---
    # First filter for actual fraud status (not just high risk score)
    fraud_df = df[df['Status'] == 'Fraud'].copy()

    if not fraud_df.empty:
        st.markdown("### 📊 Fraud Composition Analysis")

        # Extract Primary Cause (first flag in list) - CRITICAL FIX
        fraud_df['Primary_Cause'] = fraud_df['Flag_Reasons'].apply(
            lambda x: x[0] if isinstance(x, list) and len(
                x) > 0 and x[0] != 'Normal' else 'Unknown'
        )

        # Create two side-by-side pie charts
        import plotly.express as px

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # PIE CHART 1: Fraud vs Normal Distribution
            st.markdown("##### System Health Overview")

            normal_count = len(df[df['Status'] == 'Normal'])
            fraud_count = len(fraud_df)

            health_data = pd.DataFrame({
                'Status': ['Normal', 'Fraud'],
                'Count': [normal_count, fraud_count]
            })

            fig1 = px.pie(
                health_data,
                values='Count',
                names='Status',
                hole=0.6,
                color='Status',
                color_discrete_map={'Normal': '#10b981', 'Fraud': '#ef4444'}
            )

            # Enhanced visual styling
            fig1.update_traces(
                textposition='outside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>',
                textfont=dict(size=14, color='#1f2937'),
                marker=dict(line=dict(color='#ffffff', width=2))
            )

            fig1.update_layout(
                showlegend=False,
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                annotations=[
                    dict(text=f'Total<br>{len(df):,}', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
            # PIE CHART 2: Fraud Type Breakdown
            st.markdown("##### Fraud Type Breakdown")

            fraud_composition = fraud_df['Primary_Cause'].value_counts(
            ).reset_index()
            fraud_composition.columns = ['Violation', 'Count']

            fig2 = px.pie(
                fraud_composition,
                values='Count',
                names='Violation',
                hole=0.6,
                color_discrete_sequence=px.colors.sequential.Reds_r
            )

            # Enhanced visual styling
            fig2.update_traces(
                textposition='outside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Cases: %{value:,}<br>Share: %{percent}<extra></extra>',
                textfont=dict(size=14, color='#1f2937'),
                marker=dict(line=dict(color='#ffffff', width=2))
            )

            fig2.update_layout(
                showlegend=False,
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                annotations=[dict(
                    text=f'Fraud<br>{len(fraud_df):,}', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div style='margin-top: 1rem;'></div>",
                    unsafe_allow_html=True)

        # Interactive Drill-Down Section (moved below charts)
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("#### 🔍 Filter by Violation")
            unique_violations = [
                'All'] + sorted(fraud_df['Primary_Cause'].unique().tolist())
            selected_violation = st.selectbox(
                "Select Category:",
                unique_violations,
                key="violation_filter"
            )

        with col2:
            # Metrics for selected violation
            if selected_violation == 'All':
                filtered_df = fraud_df
            else:
                filtered_df = fraud_df[fraud_df['Primary_Cause']
                                       == selected_violation]

            shops_involved = filtered_df['ShopID'].nunique()
            total_leakage = filtered_df['Amount'].sum(
            ) if 'Amount' in filtered_df.columns else 0

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Cases", f"{len(filtered_df):,}")
            with m2:
                st.metric("Shops", f"{shops_involved}")
            with m3:
                st.metric("Leakage", f"₹{total_leakage:,.0f}")

        # Filtered Table for selected violation
        st.markdown(f"**{selected_violation} Cases:**")
        display_cols = ['ShopID', 'TransactionID',
                        'Amount', 'Risk_Score', 'Flag_Reasons']
        available_cols = [c for c in display_cols if c in filtered_df.columns]

        st.dataframe(
            filtered_df[available_cols].head(15),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
    else:
        # No fraud detected - show info message
        st.info("✅ No Fraud Detected - All transactions appear normal!")

    # --- Main Area ---
    st.markdown("### 🚨 High Priority Alerts")

    if not fraud_df.empty:
        # Create "Violation Type" column by joining Flag_Reasons
        # Handle cases where Flag_Reasons might be empty or missing
        if 'Flag_Reasons' in fraud_df.columns:
            fraud_df['Violation_Type'] = fraud_df['Flag_Reasons'].apply(
                lambda x: ', '.join(x) if isinstance(
                    x, list) and x else 'Unknown'
            )
        else:
            fraud_df['Violation_Type'] = 'Unknown'

        # Display columns
        display_cols = ['ShopID', 'TransactionID',
                        'Risk_Score', 'Violation_Type', 'Amount', 'Status']
        available_cols = [c for c in display_cols if c in fraud_df.columns]

        st.dataframe(
            fraud_df[available_cols],
            use_container_width=True,
            column_config={
                "Risk_Score": st.column_config.ProgressColumn(
                    "Risk Score",
                    help="Anomaly Score",
                    format="%d",
                    min_value=0,
                    max_value=100,
                ),
                "Amount": st.column_config.NumberColumn(
                    "Amount (₹)",
                    format="₹ %.2f"
                ),
                "Violation_Type": st.column_config.TextColumn(
                    "Detected Violations",
                    help="Specific fraud patterns detected"
                )
            },
            hide_index=True
        )

        st.markdown("<div class='h-4'></div>", unsafe_allow_html=True)

        # Call to action
        st.info("💡 **Tip:** For detailed shop-level analysis, visit the Shop Inspector page from the navigation menu.")

    else:
        st.success("✅ No high-risk transactions detected.")
