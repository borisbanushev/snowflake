"""
The Snowflake Advantage
Business value, unification, and enterprise capabilities
"""

import streamlit as st
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="The Snowflake Advantage", page_icon="❄️", layout="wide")

# -----------------------------------------------------------------------------
# CUSTOM CSS (High Impact)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        padding: 4rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #38BDF8, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        letter-spacing: -0.025em;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.25rem;
        max-width: 800px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Value Cards */
    .impact-card {
        background: white;
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        height: 100%;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .impact-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border-color: #38BDF8;
    }
    
    .impact-icon {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
        background: #F0F9FF;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        color: #0284C7;
    }
    
    .impact-title {
        font-weight: 800;
        font-size: 1.5rem;
        color: #0F172A;
        margin-bottom: 1rem;
    }
    
    .impact-text {
        color: #475569;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Section Headers */
    .section-heading {
        font-size: 2rem;
        font-weight: 800;
        color: #1E293B;
        margin: 4rem 0 2rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .section-badge {
        background: #E0F2FE;
        color: #0369A1;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 700;
        text-transform: uppercase;
    }

    /* Code/Governance Box */
    .code-box {
        background: #1E293B;
        border-radius: 12px;
        padding: 2rem;
        color: #E2E8F0;
        font-family: 'Monaco', monospace;
        position: relative;
    }
    .mask-highlight {
        background: rgba(239, 68, 68, 0.2);
        color: #FCA5A5;
        padding: 0 4px;
        border-radius: 4px;
    }

    /* Sidebar match */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    [data-testid="stSidebarNav"] ul li a[aria-current="page"] {
        background-color: #F1F5F9 !important;
        border-left: 5px solid #29B5E8 !important;
        color: #1E293B !important;
        font-weight: 700 !important;
        padding-left: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://www.snowflake.com/wp-content/themes/snowflake/assets/img/brand-guidelines/logo-sno-blue-example.svg", width=180)
    

# -----------------------------------------------------------------------------
# HERO SECTION
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">The Intelligent Data Cloud</div>
    <div class="hero-subtitle">
        One platform that unifies <b>Transactional Applications</b>, <b>Enterprise Analytics</b>, and <b>Native AI Agents</b>.
        <br>No silos. No copy-paste. Just intelligence.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# VALUE PILLARS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# VALUE PILLARS
# -----------------------------------------------------------------------------

# --- SECTION 1: UNIFICATION ---
st.markdown("""
<div class="section-heading">
    <span class="section-badge" style="background: #E0F2FE; color: #0284C7;">Federation</span>
    A Total Data Landscape Unification
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="impact-card">
    <div style="display: flex; align-items: flex-start; gap: 1.5rem;">
        <div class="impact-icon" style="margin-bottom: 0; min-width: 80px;">🌐</div>
        <div>
            <div class="impact-title">A Single Data Estate</div>
            <div class="impact-text">
                Legacy systems (Oracle, MySQL) and modern lakes (Databricks) are no longer isolated silos. 
                We operate on a <b>Zero-Copy</b> principle using <b>Apache Iceberg</b> and <b>Polaris Catalog</b>. 
                This allows the AI Agent to query the <i>entire</i> customer context—account history, real-time clicks, and external credit scores—without waiting for ETL jobs.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SECTION 2: UNISTORE ---
st.markdown("""
<div class="section-heading">
    <span class="section-badge" style="background: #FEF3C7; color: #D97706;">Unistore</span>
    OLTP Meets AI
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="impact-card">
    <div style="display: flex; align-items: flex-start; gap: 1.5rem;">
        <div class="impact-icon" style="margin-bottom: 0; min-width: 80px;">⚡</div>
        <div>
            <div class="impact-title">The Hybrid Transactional/Analytical Platform</div>
            <div class="impact-text">
                Historically, you had to move data to analyze it. With <b>Unistore Hybrid Tables</b>, we perform sub-millisecond lookups 
                and write Credit Decisions to the <i>same</i> platform that trains the XGBoost models.
                <br><b>Result:</b> A closed loop where Insight ➡ Action ➡ New Insight happens in milliseconds.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SECTION 3: AI AGENTS ---
st.markdown("""
<div class="section-heading">
    <span class="section-badge" style="background: #E8FFEA; color: #16A34A;">Speed</span>
    Agentic Decision Making
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="impact-card">
    <div style="display: flex; align-items: flex-start; gap: 1.5rem;">
        <div class="impact-icon" style="margin-bottom: 0; min-width: 80px;">🤖</div>
        <div>
            <div class="impact-title">From Human Latency to AI Velocity</div>
            <div class="impact-text">
                Traditional credit reviews take days of manual document hunting. 
                Our <b>Cortex AI Agents</b> autonomously retrieve policy docs (Vector Search), check credit history (SQL), and calculate risk ratios (Python) in seconds.
                <br><b>Result:</b> 90% Faster Time-to-Decision while maintaining full auditability.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SECTION 4: GOVERNANCE ---
st.markdown("""
<div class="section-heading">
    <span class="section-badge" style="background: #FEE2E2; color: #DC2626;">Governance</span>
    Native Trust
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="impact-card">
    <div style="display: flex; align-items: flex-start; gap: 1.5rem;">
        <div class="impact-icon" style="margin-bottom: 0; min-width: 80px;">🛡️</div>
        <div>
            <div class="impact-title">Security at the Storage Layer</div>
            <div class="impact-text">
                AI Agents are powerful, but they require strict guardrails. Our <b>Role-Based Access Control (RBAC)</b> 
                and <b>Dynamic Masking Policies</b> apply universally. Whether it's a raw SQL query or an LLM prompt, 
                PII is redacted <i>before</i> the compute layer sees it, ensuring zero leakage by design.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# LINEAGE SECTION
# -----------------------------------------------------------------------------
st.markdown("""
<div class="section-heading">
    <span class="section-badge">Architecture</span>
    Enterprise Data Lineage
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Why is the lineage so complex?** Because real enterprises are complex. 
Notice explicitly how **Dynamic Tables** sit between the Raw and Silver layers. They are separate because they operate on a different *state model*—automated, incremental refreshes that "breathe" data from Source to Insight.
""")

# Complex Sankey
labels = [
    "Oracle T24 (Core)", "MySQL (Digital App)", "Databricks (Bureau)", 
    "Snowflake Raw Layer", 
    "Dynamic Table: Cleanse", 
    "Dynamic Table: Conform", 
    "Silver Layer (Curated)", 
    "Dynamic Table: Aggregation",
    "Gold Layer (Feature Store)", 
    "Hybrid Table (Unistore)",
    "Cortex AI Agent",
    "Streamlit App",
    "Compliance Audit"
]

source = [0, 1, 2, 3, 3, 4, 5, 6, 7, 8, 8, 9, 10, 10]
target = [3, 3, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11, 11, 12]
value  = [10, 8, 5, 10, 8, 15, 12, 12, 8, 10, 5, 5, 5, 2]
colors = [
    "#94A3B8", "#94A3B8", "#94A3B8", # Sources
    "#64748B", # Raw
    "#F59E0B", "#F59E0B", # Dynamic Tables (Orange)
    "#3B82F6", # Silver
    "#F59E0B", # Dynamic Tables
    "#10B981", # Gold
    "#8B5CF6", # Hybrid
    "#EC4899", # AI
    "#6366F1", # App
    "#EF4444"  # Audit
]

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = colors
    ),
    link = dict(
      source = source,
      target = target,
      value = value,
      color = "rgba(200, 200, 200, 0.3)"
  ))])

fig.update_layout(title_text="From Silo to App: The Data Journey", height=500, font_size=12)
st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------------------------
# GOVERNANCE SECTION
# -----------------------------------------------------------------------------
st.markdown("""
<div class="section-heading">
    <span class="section-badge">Security</span>
    AI With Guardrails
</div>
""", unsafe_allow_html=True)

c_gov1, c_gov2 = st.columns(2)

with c_gov1:
    st.markdown("### 🚫 What the Agent Sees")
    st.markdown("The Agent runs with the `APP_SERVICE_ROLE`. It **cannot** see PII, even if it tries to 'hack' the prompt.")
    st.markdown("""
    <div class="code-box">
    > 🤖 <b>AGENT:</b> "Show me the details for CUS-001"<br><br>
    <b>DATABASE RESPONSE:</b><br>
    ---------------------------------------------<br>
    ID: CUS-001<br>
    NAME: <span class="mask-highlight">**********</span> (MASKED_PII_POLICY)<br>
    EMAIL: <span class="mask-highlight">*****@****.com</span> (MASKED_PII_POLICY)<br>
    CREDIT_SCORE: 785 (Visible)<br>
    ---------------------------------------------<br>
    </div>
    """, unsafe_allow_html=True)

with c_gov2:
    st.markdown("### ✅ What the Auditor Sees")
    st.markdown("With `COMPLIANCE_ROLE`, full traceability is maintained. Every AI action is a logged transaction.")
    st.markdown("""
    <div class="code-box" style="background: #064E3B;">
    > 👮 <b>AUDITOR:</b> "Who accessed CUS-001?"<br><br>
    <b>AUDIT LOG:</b><br>
    ---------------------------------------------<br>
    TIMESTAMP: 2025-01-24 14:02:11<br>
    USER: APP_SERVICE_BOT<br>
    ACTION: SELECT * FROM CUSTOMER_360<br>
    OUTCOME: <span style="color:#6EE7B7">SUCCESS (Masked Delivery)</span><br>
    ---------------------------------------------<br>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DEPLOYMENT
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; margin-top: 3rem;">
    <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Ready to Deploy?</div>
    <div style="color: #64748B; max-width: 600px; margin: 0 auto;">
        This entire demo—including the <b>Dockerized Sources</b>, <b>Snowpark Models</b>, and <b>Governance Rules</b>—is built with Infrastructure as Code.
    </div>
    <br>
    <div style="font-family: monospace; background: #F1F5F9; padding: 1rem; border-radius: 8px; display: inline-block;">
        ./scripts/deploy_all.sh --environment=production
    </div>
</div>
""", unsafe_allow_html=True)
