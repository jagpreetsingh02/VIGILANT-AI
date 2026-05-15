import streamlit as st


def inject_tailwind():
    """Injects Tailwind CSS via CDN."""
    st.markdown("""
        <script src="https://cdn.tailwindcss.com"></script>
    """, unsafe_allow_html=True)


def navbar():
    """
    Professional top header navigation bar with sticky positioning.
    Returns the selected page name if a navigation button is clicked.
    """

    st.markdown("""
        <style>
        .navbar-container {
            position: sticky;
            top: 0;
            z-index: 999;
            background: #0052cc;
            padding: 0.8rem 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin: -1rem -1rem 2rem -1rem;
            display: flex;
            align-items: center;
        }
        .navbar-button {
            background: rgba(255, 255, 255, 0.1);
            border: none !important;
            color: white !important;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.95rem;
            font-weight: 500;
            text-decoration: none;
            margin-right: 0.5rem;
            display: inline-block;
            text-align: center;
            width: 100%;
        }
        .navbar-button:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }
        .navbar-button-active {
            background: white !important; 
            color: #0052cc !important;
            font-weight: 700;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        /* Target buttons inside columns to apply class */
        div[data-testid="stHorizontalBlock"] button {
             border: none;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'Home'

    current_page = st.session_state.get('current_page', 'Home')

    st.markdown('<div class="navbar-container">', unsafe_allow_html=True)

    cols = st.columns([2.5, 1, 1.2, 1.2, 1.5, 2.6])

    with cols[0]:

        st.markdown("""
            <h3 style='margin: 0; padding: 0.3rem 0; 
                       color: #0052cc;
                       font-weight: 800; font-size: 1.6rem; letter-spacing: -0.5px;'>
                VigilantAI
            </h3>
        """, unsafe_allow_html=True)

    with cols[1]:

        label = "Home"
        if st.button(label, key="nav_home", use_container_width=True):
            st.session_state['current_page'] = 'Home'
            st.rerun()

    with cols[2]:

        label = "Dashboard"
        if st.button(label, key="nav_dashboard", use_container_width=True):
            st.session_state['current_page'] = 'Dashboard'
            st.rerun()

    with cols[3]:

        label = "Geo Map"
        if st.button(label, key="nav_map", use_container_width=True):
            st.session_state['current_page'] = 'Live Map'
            st.rerun()

    with cols[4]:

        label = "Shop Inspector"
        if st.button(label, key="nav_inspector", use_container_width=True):
            st.session_state['current_page'] = 'Shop Inspector'
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    return current_page


def metric_card(title, value, prefix="", color="blue"):
    """Creates a styled metric card."""
    color_map = {
        "blue": "#0052cc",
        "red": "#ef4444",
        "green": "#10b981"
    }

    st.markdown(f"""
        <div style='background-color: white; padding: 1.5rem; border-radius: 8px; 
                    border-left: 4px solid {color_map.get(color, "#0052cc")}; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
            <h4 style='margin: 0; font-size: 0.85rem; color: #666; text-transform: uppercase;'>{title}</h4>
            <h2 style='margin: 0.5rem 0 0 0; font-size: 2rem; color: #172b4d;'>{prefix}{value}</h2>
        </div>
    """, unsafe_allow_html=True)
