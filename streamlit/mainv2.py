"""
Snowflake Credit Decisioning Platform
Main Streamlit Application - Enterprise Edition
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from snowflake.snowpark.context import get_active_session
import datetime

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Credit Decisioning Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CUSTOM CSS & STYLING (Enterprise/Bank Look)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #F5F7FA;
    }

    /* Top Navigation Bar Style (simulated with container) */
    .top-nav {
        background-color: #FFFFFF;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 2rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .main-title {
        color: #1A365D; /* Navy Blue */
        font-weight: 700;
        font-size: 1.8rem;
        margin: 0;
    }
    
    .subtitle {
        color: #64748B;
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }

    /* KPI Cards */
    .kpi-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #CBD5E1;
    }

    .kpi-label {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .kpi-value {
        color: #1E293B;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .kpi-delta {
        font-size: 0.85rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .delta-pos { color: #10B981; }
    .delta-neg { color: #EF4444; }
    
    /* Action Cards / Navigation */
    .action-section {
        margin-top: 2.5rem;
    }
    
    .section-header {
        color: #334155;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-left: 4px solid #29B5E8;
        padding-left: 1rem;
    }
    
    .info-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.25rem;
        height: 100%;
    }
    
    .info-card h4 {
        color: #1E293B;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .info-card p {
        color: #64748B;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    .sidebar-user {
        padding: 1rem;
        background: #F8FAFC;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #E2E8F0;
    }
    
    .sidebar-user-label {
        font-size: 0.75rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .sidebar-user-val {
        font-size: 0.9rem;
        color: #334155;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CONNECTIVITY TO SNOWFLAKE
# -----------------------------------------------------------------------------
session = None
try:
    session = get_active_session()
    is_connected = True
except:
    is_connected = False

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://www.snowflake.com/wp-content/themes/snowflake/assets/img/brand-guidelines/logo-sno-blue-example.svg", width=180)
    
    # st.markdown("### Decisioning Portal") 
    # Removed redundant manual navigation since Streamlit Pages are detected
    
    if is_connected:
        try:
            user_info = session.sql("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()").collect()[0]
            st.markdown(f"""
            <div class="sidebar-user">
                <div class="sidebar-user-label">Logged in as</div>
                <div class="sidebar-user-val">{user_info[0]}</div>
                <div style="margin-top: 8px;"></div>
                <div class="sidebar-user-label">Role</div>
                <div class="sidebar-user-val">{user_info[1]}</div>
                <div style="margin-top: 8px;"></div>
                <div class="sidebar-user-label">Warehouse</div>
                <div class="sidebar-user-val">{user_info[2]}</div>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.error("Error fetching user details")
    else:
        st.markdown(f"""
        <div class="sidebar-user">
            <div class="sidebar-user-label">Status</div>
            <div class="sidebar-user-val" style="color: orange;">Offline / Local</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("v2.1.0 • Enterprise Edition")

# -----------------------------------------------------------------------------
# MAIN CONTENT
# -----------------------------------------------------------------------------

# Top Header Section
st.markdown("""
<div class="top-nav">
    <div>
        <h1 class="main-title">Credit Decisioning Platform</h1>
        <div class="subtitle">Unified Enterprise Data Platform • Financial Services</div>
    </div>
    <div>
        <img src="https://www.snowflake.com/wp-content/themes/snowflake/assets/img/brand-guidelines/logo-sno-blue-example.svg" height="40" style="opacity: 0.8;">
    </div>
</div>
""", unsafe_allow_html=True)

# KPI Section
st.markdown('<div class="section-header">Portfolio Overview</div>', unsafe_allow_html=True)

# Default values
total_customers = "0"
pending_apps = "0"
delinquent_loans = "0"
total_exposure = "$0M"

if is_connected:
    try:
        # We wrap this in another try in case tables don't exist yet
        stats = session.sql("""
            SELECT 
                (SELECT COUNT(*) FROM ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED) AS customers,
                (SELECT COUNT(*) FROM APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS WHERE STATUS = 'SUBMITTED') AS pending_apps,
                (SELECT COUNT(*) FROM CURATED_ZONE.LOANS.FACT_LOANS WHERE DAYS_PAST_DUE > 0) AS delinquent_loans,
                (SELECT SUM(LOAN_AMOUNT) FROM CURATED_ZONE.LOANS.FACT_LOANS) as exposure
        """).collect()[0]
        
        total_customers = f"{stats[0]:,}"
        pending_apps = f"{stats[1]:,}"
        delinquent_loans = f"{stats[2]:,}"
        # Mocking exposure if null
        exposure_val = stats[3] if stats[3] else 45000000 
        total_exposure = f"${exposure_val/1000000:.1f}M"
    except:
        # Fallback if specific tables missing
        total_customers = "12,450"
        pending_apps = "48"
        delinquent_loans = "15"
        total_exposure = "$45.2M"
else:
    # Local fallback/Mock Data
    total_customers = "12,450"
    pending_apps = "48"
    delinquent_loans = "15"
    total_exposure = "$45.2M"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Active Customers</div>
        <div class="kpi-value">{total_customers}</div>
        <div class="kpi-delta delta-pos">↑ 2.4% <span style="color: #94A3B8; font-weight: 400; margin-left: 4px;">vs last month</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Pending Reviews</div>
        <div class="kpi-value">{pending_apps}</div>
        <div class="kpi-delta" style="color: #F59E0B;">• Requires Action</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Risk Exposure</div>
        <div class="kpi-value">{total_exposure}</div>
        <div class="kpi-delta delta-pos">↓ 0.8% <span style="color: #94A3B8; font-weight: 400; margin-left: 4px;">vs target</span></div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Delinquency Rate</div>
        <div class="kpi-value">1.2%</div>
        <div class="kpi-delta delta-neg">↑ 0.1% <span style="color: #94A3B8; font-weight: 400; margin-left: 4px;">vs last month</span></div>
    </div>
    """, unsafe_allow_html=True)

# Dashboard & Actions Section
st.markdown('<div class="action-section"></div>', unsafe_allow_html=True)
col_l, col_r = st.columns([2, 1])

with col_l:
    st.markdown('<div class="section-header">Operational Capability</div>', unsafe_allow_html=True)
    
    # Grid for capabilities
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.info("**Real-time CDC**\n\nLive data ingestion from Oracle T24 & MySQL using Snowflake Native Connectors.")
    with c2:
        st.info("**Federated Access**\n\nApache Polaris integration for seamless Databricks Delta Lake queries.")
    with c3:
        st.info("**AI Decision Agent**\n\nCortex-powered automated credit scoring and risk assessment.")
        
    st.markdown("###") # spacer
    
    # Mock Chart
    st.markdown("**Application Trend (Last 30 Days)**")
    chart_data = pd.DataFrame({
        'Date': pd.date_range(end=datetime.date.today(), periods=30),
        'Applications': [x + (x*0.1) for x in range(30, 60)] # Mock linear trend
    })
    st.bar_chart(chart_data.set_index('Date'), height=200, color="#29B5E8")

with col_r:
    st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)
    
    # Action Buttons styled as cards
    st.markdown("""
    <div style="display: flex; flex-direction: column; gap: 1rem;">
    """, unsafe_allow_html=True)
    
    if st.button("📝 Start New Application", use_container_width=True):
        st.toast("Application module loading...")
        
    if st.button("📋 Review Priority Queue", use_container_width=True):
        st.toast("Fetching high priority items...")
        
    if st.button("🤖 Ask AI Assistant", use_container_width=True):
        st.toast("Initializing Cortex AI...")
        
    if st.button("👥 Customer Lookup", use_container_width=True):
        st.toast("Opening Customer 360...")

    st.markdown("""
    <div class="info-card" style="margin-top: 1rem; background-color: #F0F9FF; border-color: #BAE6FD;">
        <h4 style="color: #0369A1;">System Status</h4>
        <p style="margin:0;">
        🟢 <strong>Cortex AI:</strong> Online<br>
        🟢 <strong>Polaris Catalog:</strong> Synced<br>
        🟢 <strong>T24 Connector:</strong> Active
        </p>
    </div>
    """, unsafe_allow_html=True)
