import streamlit as st
import streamlit.components.v1 as components_html
from src import components
import json
import os

def render():
    """
    Renders the "Vigilant-AI" Landing Page.
    """
    components.inject_tailwind()
    
    # Custom CSS for Gradient Text & Animations
    st.markdown("""
        <style>
        .hero-title {
            background: -webkit-linear-gradient(45deg, #0052cc, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.8rem;
            font-weight: 800;
            line-height: 1.2;
        }
        .hero-container {
            padding: 3rem 1rem;
            background: linear-gradient(180deg, #f7f9fc 0%, #ffffff 100%);
            border-bottom: 1px solid #e2e8f0;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- HERO SECTION ---
    # Split into 2 columns: Text (Left) + Lottie (Right)
    hero_col1, hero_col2 = st.columns([1.2, 0.8])
    
    with hero_col1:
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown('<h1 class="hero-title">Vigilant-AI</h1>', unsafe_allow_html=True)
        st.markdown("""
            <h2 style='font-size: 1.8rem; color: #172b4d; font-weight: 600; margin-top: 0.5rem;'>
                Secure. Intelligent. Real-time.
            </h2>
            <p style='font-size: 1.1rem; color: #5e6c84; margin-top: 1rem; line-height: 1.6; max_width: 90%;'>
                Next-generation fraud detection for the Public Distribution System. 
                Using hybrid AI models to detect leakage, hoarding, and anomalies instantly.
            </p>
        """, unsafe_allow_html=True)
        
    with hero_col2:
        # Load Local Lottie Animation
        try:
            with open("src/hero_anim.json", "r") as f:
                lottie_json = json.dumps(json.load(f))
                
            lottie_html = f"""
                <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
                <lottie-player 
                    id="hero-lottie"
                    background="transparent"  
                    speed="1"  
                    style="width: 100%; height: 350px;"  
                    loop  
                    autoplay>
                </lottie-player>
                <script>
                    const player = document.getElementById("hero-lottie");
                    player.load({lottie_json});
                </script>
            """
            components_html.html(lottie_html, height=400)
        except Exception as e:
            st.warning(f"Animation could not be loaded: {e}")

    # --- INTERACTIVE CARDS (Launch Control) ---
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.divider()
    
    c1, c2 = st.columns(2, gap="medium")
    
    # Left Card: Upload
    with c1:
        with st.container(border=True):
            st.markdown("### 📂 Upload Transaction Log")
            st.markdown("<p style='color:#666; font-size:0.9rem;'>Analyze custom PDS datasets.</p>", unsafe_allow_html=True)
            
            uploaded = st.file_uploader("Drop CSV", type=['csv'], label_visibility="collapsed")
            
            if uploaded:
                st.success("File Loaded!")
                if st.session_state.get('uploaded_file') != uploaded:
                    st.session_state['uploaded_file'] = uploaded
                    st.session_state['final_df'] = None
                    st.session_state['current_page'] = 'Dashboard'
                    st.rerun()

    # Right Card: Demo Mode
    with c2:
        with st.container(border=True):
            st.markdown("### 🚀 Launch Demo Mode")
            st.markdown("<p style='color:#666; font-size:0.9rem;'>No data? Load synthetic records to test the system.</p>", unsafe_allow_html=True)
            
            st.markdown("<div style='height: 29px'></div>", unsafe_allow_html=True) # Spacer to align buttons
            if st.button("Load Demo Data", use_container_width=True, type="primary"):
                 st.session_state['uploaded_file'] = None
                 st.session_state['final_df'] = None
                 st.session_state['current_page'] = 'Dashboard'
                 st.rerun()

    # --- FEATURE CARDS (Moved Below) ---
    st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)
    st.markdown("### System Capabilities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); height: 100%; border-top: 5px solid #0052cc; transition: transform 0.2s;'>
                <div style='font-size: 2rem; margin-bottom: 1rem;'>⚡</div>
                <h3 style='color: #172b4d; font-weight: 700; margin-bottom: 0.5rem;'>Real-time Core</h3>
                <p style='color: #6b778c; font-size: 0.95rem;'>Processing transactions with sub-second latency using session-state caching architecture.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); height: 100%; border-top: 5px solid #ef4444; transition: transform 0.2s;'>
                <div style='font-size: 2rem; margin-bottom: 1rem;'>🛡️</div>
                <h3 style='color: #172b4d; font-weight: 700; margin-bottom: 0.5rem;'>Fraud Shield</h3>
                <p style='color: #6b778c; font-size: 0.95rem;'>Detects 5+ vector attacks: Velocity, Hoarding, Price Inflation, and ID Misuse.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); height: 100%; border-top: 5px solid #10b981; transition: transform 0.2s;'>
                <div style='font-size: 2rem; margin-bottom: 1rem;'>🔎</div>
                <h3 style='color: #172b4d; font-weight: 700; margin-bottom: 0.5rem;'>Deep Inspector</h3>
                <p style='color: #6b778c; font-size: 0.95rem;'>Dedicated portal for granular shop analysis with visual evidence timelines.</p>
            </div>
        """, unsafe_allow_html=True)

    # --- TECHNOLOGY STACK ---
    st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<h3 style='text-align: center; color: #172b4d; margin-bottom: 2rem;'>OUR TECHNOLOGY</h3>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.columns(3)
    
    with t1:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; margin:0;'>🐍 Python Streamlit</h4>", unsafe_allow_html=True)
            
    with t2:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; margin:0;'>⚙️ Scikit-Learn</h4>", unsafe_allow_html=True)
            
    with t3:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; margin:0;'>🐼 Pandas</h4>", unsafe_allow_html=True)

    # --- DETECTABLE ANOMALIES ---
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    st.subheader("Detectable Anomalies")
    
    with st.container(border=True):
        st.markdown("""
            <ul style='list-style-type: none; padding-left: 0; font-size: 1.05rem; line-height: 1.8;'>
                <li>👻 <b>Ghost Beneficiaries:</b> IDs that have been inactive for 6+ months suddenly claiming maximum quota.</li>
                <li>⚡ <b>Velocity Fraud:</b> A single shop processing transactions faster than humanly possible (<10 seconds per user).</li>
                <li>📦 <b>Stock Diversion:</b> Discrepancies between 'Stock Received' vs. 'Stock Distributed' exceeding the 5% variance threshold.</li>
                <li>📍 <b>Geofencing Violations:</b> Users claiming rations >200km from their registered home district.</li>
            </ul>
        """, unsafe_allow_html=True)
