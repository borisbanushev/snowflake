"""
Technical Architecture
System design, data pipeline, and security specifications
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Technical Architecture", page_icon="📚", layout="wide")

# -----------------------------------------------------------------------------
# CUSTOM CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #F5F7FA;
    }

    .page-header {
        background-color: #FFFFFF;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 2rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .page-title {
        color: #1A365D;
        font-weight: 700;
        font-size: 1.8rem;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .page-subtitle {
        color: #64748B;
        font-size: 0.95rem;
        margin-top: 0.25rem;
        margin-left: 2.7rem; 
    }
    
    .tech-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        height: 100%;
    }
    
    .tech-header {
        color: #1E293B;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #F1F5F9;
        padding-bottom: 0.5rem;
    }
    
    .code-block {
        background-color: #0F172A;
        color: #E2E8F0;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Monaco', 'Consolas', monospace;
        font-size: 0.85rem;
        overflow-x: auto;
    }
    
    .diagram-box {
        background-color: #F8FAFC;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        color: #64748B;
        font-weight: 500;
        margin: 1rem 0;
    }

    /* Sidebar - match other pages */
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
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style="padding: 1rem; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0;">
        <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Technical Specs</div>
        <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #1E293B;">
        <b>Version:</b> 2.1.0<br>
        <b>Region:</b> AWS Singapore<br>
        <b>Edition:</b> Enterprise
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("v2.1.0 • Enterprise Edition")

# -----------------------------------------------------------------------------
# MAIN HEADER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="page-header">
    <div class="page-title">
        <span>📚</span> Technical Architecture
    </div>
    <div class="page-subtitle">Underlying infrastructure, data pipelines, and governance framework</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TABS
# -----------------------------------------------------------------------------
tabs = st.tabs(["🏗️ Architecture", "🔄 Data Integration (CDC)", "💾 Schema & Data Model", "🛡️ Governance", "🤖 ML & AI"])

# --- TAB 1: ARCHITECTURE ---
with tabs[0]:
    st.markdown("### High-Level Reference Architecture")
    
    st.info("""
    **Core Philosophy**: A Unified Data Platform combining Transactional (Unistore) and Analytical workloads, 
    federating external data via Apache Polaris, and powering decisions with Cortex AI.
    """)
    
    # Diagram simulation
    st.markdown("""
    <div class="diagram-box">
        [ Oracle T24 ] --(LogMiner CDC)--> [ Snowflake RAW_ZONE ] <br>
        [ MySQL DB ] --(Binlog CDC)--> [ Snowflake RAW_ZONE ] <br>
        [ Databricks ] --(Polaris/Iceberg)--> [ Snowflake RAW_ZONE ] <br>
        <br>
        ⬇️ (Streams & Tasks) <br>
        <br>
        [ CURATED_ZONE (Silver) ] --> [ ANALYTICS_ZONE (Gold) ] <br>
        <br>
        ⬇️ 🔄 <br>
        <br>
        [ Snowpark ML Training ] <--> [ Unistore / Hybrid Tables ] <--> [ Streamlit App ]
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="tech-card">
            <div class="tech-header">Compute Layer</div>
            <ul>
                <li><b>ETL_WH (Medium):</b> Continuous data pipeline processing (Bronze → Silver → Gold)</li>
                <li><b>ML_WH (Large):</b> Snowpark-optimized for XGBoost training</li>
                <li><b>APP_WH (Small):</b> Low-latency Streamlit queries</li>
                <li><b>TRANSACTIONAL_WH (Medium):</b> Hybrid table OLTP operations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="tech-card">
            <div class="tech-header">Storage Layer</div>
            <ul>
                <li><b>Raw Zone:</b> Landing area for CDC replication</li>
                <li><b>Curated Zone:</b> Cleaned, conformed dimensions and facts</li>
                <li><b>Analytics Zone:</b> Customer 360 & aggregated metrics</li>
                <li><b>App Zone (Unistore):</b> Transactional state for Credit Applications</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 2: DATA INTEGRATION ---
with tabs[1]:
    st.markdown("### 🔄 Real-time Data Ingestion (Openflow)")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**1. Oracle T24 Core Banking**")
        st.markdown("Replicated via **LogMiner** for sub-minute latency.")
        st.code("""
-- Oracle Openflow Configuration
CREATE CONNECTION ORACLE_T24_CONN
TYPE = ORACLE
HOST = 'oracle-t24'
PORT = 1521
CDC_MODE = 'LOG_BASED';

-- Synced Tables
1. T24_CUSTOMER (100k records)
2. T24_ACCOUNT (180k records)
3. T24_TRANSACTION (5M records)
        """, language="sql")
        
    with c2:
        st.markdown("**2. Apache Polaris (Federation)**")
        st.markdown("Zero-copy access to **Databricks Delta Lake** via Iceberg.")
        st.code("""
-- Databricks Federation
CREATE CATALOG DATABRICKS_CATALOG
USING POLARIS
CATALOG_ID = 'db-credit-bureau'
URL = 'https://polaris.databricks.net';

-- External Tables
1. CREDIT_BUREAU_SCORES
2. EXTERNAL_ENRICHMENT
        """, language="sql")

# --- TAB 3: SCHEMA ---
with tabs[2]:
    st.markdown("### 💾 Logical Data Model")
    
    st.markdown("**Database:** `CREDIT_DECISIONING_DB`")
    
    expander1 = st.expander("APP_ZONE.TRANSACTIONAL (Unistore Hybrid Tables)", expanded=True)
    with expander1:
        st.markdown("Hyper-optimized for single-row lookups and transactional inserts.")
        st.code("""
CREATE HYBRID TABLE CREDIT_APPLICATIONS (
    APPLICATION_ID VARCHAR(36) PRIMARY KEY,
    CUSTOMER_ID VARCHAR(20),
    STATUS VARCHAR(20),
    REQUESTED_AMOUNT NUMBER(12,2),
    INDEX idx_cust (CUSTOMER_ID),
    INDEX idx_status (STATUS)
);

CREATE HYBRID TABLE CREDIT_DECISIONS (
    DECISION_ID VARCHAR(36) PRIMARY KEY,
    APP_ID VARCHAR(36) FOREIGN KEY REFERENCES CREDIT_APPLICATIONS,
    FINAL_DECISION VARCHAR(10),
    DECISION_TIMESTAMP TIMESTAMP_NTZ
);
        """, language="sql")
        
    expander2 = st.expander("ANALYTICS_ZONE.CUSTOMER_360 (Gold Layer)")
    with expander2:
        st.markdown("Unified view merging Oracle, MySQL, and Databricks sources.")
        st.code("""
CREATE VIEW CUSTOMER_360_UNIFIED AS
SELECT 
    c.CUSTOMER_ID,
    c.RISK_CATEGORY,             -- From Oracle
    d.TOTAL_SESSIONS,            -- From MySQL
    b.EXTERNAL_RISK_SCORE,       -- From Databricks
    l.TOTAL_LOANS_OUTSTANDING    -- Aggregated Fact
FROM CURATED_ZONE.CUSTOMER c
JOIN CURATED_ZONE.DIGITAL_PROFILE d ...
LEFT JOIN DATABRICKS_CATALOG.BUREAU b ...
        """, language="sql")

# --- TAB 4: GOVERNANCE ---
with tabs[3]:
    st.markdown("### 🛡️ Security & Governance Framework")
    
    g1, g2 = st.columns(2)
    
    with g1:
        st.markdown("#### Role-Based Access Control (RBAC)")
        st.dataframe(pd.DataFrame({
            "Role": ["DATA_ENGINEER", "DATA_SCIENTIST", "CREDIT_ANALYST", "COMPLIANCE_AUDITOR"],
            "Access": ["Pipeline CRUD", "ML/Analytics Read", "App/Hybrid CRUD", "Read-Only (Masked)"],
            "Scope": ["Bronze/Silver", "Gold/ML", "App Zone", "Global"]
        }), hide_index=True)
        
    with g2:
        st.markdown("#### Dynamic Masking Policies")
        st.markdown("Context-aware data protection for sensitive fields.")
        st.code("""
CREATE MASKING POLICY PII_MASK AS (val string) 
RETURNS string ->
    CASE 
        WHEN CURRENT_ROLE() IN ('CREDIT_ANALYST') THEN val
        WHEN CURRENT_ROLE() IN ('DATA_ENGINEER') THEN '***-**-****'
        ELSE '*********'
    END;

ALTER TABLE CUSTOMER MODIFY COLUMN SSN 
SET MASKING POLICY PII_MASK;
        """, language="sql")

# --- TAB 5: ML & AI ---
with tabs[4]:
    st.markdown("### 🤖 Artificial Intelligence Stack")
    
    st.markdown("#### 1. Predictive ML (Snowpark)")
    st.markdown("""
    - **Model:** XGBoost Classifier
    - **Training:** 100k customer records with 50+ features
    - **Deployment:** Vectorized UDF for <5ms inference
    """)
    
    st.markdown("#### 2. Generative AI (Cortex)")
    st.markdown("""
    - **Cortex Search:** RAG retriever for non-structured Policy PDFs.
    - **Cortex Analyst:** Text-to-SQL for ad-hoc business queries.
    - **Cortex Agents:** Orchestrator combining ML scores, Policy Search, and Transactional lookups.
    """)
    
    st.code("""
-- Example Cortex Agent Logic
SELECT snowflake.cortex.complete(
    'llama3-70b',
    CONCAT(
        'Analyze this customer: ', customer_json, 
        ' against these policies: ', policy_context_rag
    )
);
    """, language="sql")

st.markdown("---")
st.caption("Technical Documentation • Last Updated: Feb 2026")
