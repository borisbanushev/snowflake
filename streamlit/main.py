"""
Snowflake Credit Decisioning Platform
Main Streamlit Application
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session

# Page configuration
st.set_page_config(
    page_title="Credit Decisioning Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #29B5E8;
        text-align: center;
        padding: 2rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #29B5E8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏦 Credit Decisioning Platform</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Powered by Snowflake Enterprise Data Platform</div>',
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.image("https://www.snowflake.com/wp-content/themes/snowflake/assets/img/brand-guidelines/logo-sno-blue-example.svg", width=200)
    st.markdown("---")
    st.markdown("### 👤 User Information")
    
    # Get current user and role
    try:
        session = get_active_session()
        user_info = session.sql("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()").collect()[0]
        st.write(f"**User:** {user_info[0]}")
        st.write(f"**Role:** {user_info[1]}")
        st.write(f"**Warehouse:** {user_info[2]}")
    except Exception as e:
        st.warning("⚠️ Not connected to Snowflake")
        st.caption("Please configure Streamlit in Snowflake or set up connection")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    
    try:
        # Get quick stats
        stats = session.sql("""
            SELECT 
                (SELECT COUNT(*) FROM ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED) AS customers,
                (SELECT COUNT(*) FROM APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS WHERE STATUS = 'SUBMITTED') AS pending_apps,
                (SELECT COUNT(*) FROM CURATED_ZONE.LOANS.FACT_LOANS WHERE DAYS_PAST_DUE > 0) AS delinquent_loans
        """).collect()[0]
        
        st.metric("Total Customers", f"{stats[0]:,}")
        st.metric("Pending Applications", f"{stats[1]:,}")
        st.metric("Delinquent Loans", f"{stats[2]:,}")
    except:
        pass

# Main content
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h2>🚀 Featured Capabilities</h2>
        <ul>
            <li><strong>Real-time CDC:</strong> Live data from Oracle T24 & MySQL</li>
            <li><strong>Apache Polaris:</strong> Federated Databricks access</li>
            <li><strong>AI Credit Agent:</strong> Automated decision making</li>
            <li><strong>Cortex Search:</strong> Policy document RAG</li>
            <li><strong>ML Scoring:</strong> XGBoost real-time inference</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h2>🎯 Quick Actions</h2>
        <ul>
            <li>📝 Submit new credit application</li>
            <li>📋 Review pending applications</li>
            <li>🤖 Consult AI credit agent</li>
            <li>👥 View customer 360 profiles</li>
            <li>📊 Analyze portfolio metrics</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Welcome message
st.markdown("""
## Welcome to the Credit Decisioning Platform

This platform demonstrates Snowflake's capabilities as a unified enterprise data platform for financial services.

### 🔍 Navigation

Use the sidebar to navigate between different sections:

1. **📊 Executive Dashboard** - Portfolio overview and KPIs
2. **📝 Application Portal** - Submit new credit applications
3. **📋 Application Queue** - Review and process applications
4. **🤖 AI Credit Agent** - Interactive AI-powered credit analyst
5. **💬 Intelligence Chat** - Natural language data queries
6. **👥 Customer 360** - Unified customer profiles
7. **📈 Portfolio Analytics** - Risk analysis and reporting
8. **📚 Policy Manager** - Bank policy documents
9. **🔒 Governance Center** - Data lineage and compliance
10. **⚙️ Admin Console** - System configuration

### 🎓 Getting Started

1. Start by exploring the **Executive Dashboard** for an overview
2. Try the **AI Credit Agent** to see automated decision making
3. Use **Intelligence Chat** for natural language queries
4. Review **Customer 360** to see unified data from all sources

### 📚 Documentation

- [Implementation Plan](../implementationplan.md)
- [Architecture Overview](../docs/architecture.md)
- [Data Model](../docs/data-model.md)
""")

# Footer
st.markdown("---")
st.caption("Built with ❤️ on Snowflake • Powered by Cortex AI, Openflow, Polaris, Unistore, and Snowpark ML")
