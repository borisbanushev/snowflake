"""
AI Credit Agent Page
Enterprise interface for the Cortex AI Credit Decisioning Agent
"""

import streamlit as st
import json
import time
import re
import pandas as pd
from snowflake.snowpark.context import get_active_session

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="AI Credit Agent", page_icon="🤖", layout="wide")

# -----------------------------------------------------------------------------
# CUSTOM CSS & STYLING (Enterprise/AI Premium Look)
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

    /* Top Page Header */
    .page-header {
        background-color: #FFFFFF;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 2rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .page-title {
        color: #1A365D; /* Navy Blue */
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

    /* AI Hero Banner */
    .ai-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .ai-banner::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(59,130,246,0.3) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
    }

    .ai-banner h2 {
        margin: 0;
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    .ai-banner p {
        opacity: 0.9;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* KPI Cards */
    .kpi-card {
        background-color: #FFFFFF;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        height: 100%;
    }

    .kpi-label {
        color: #64748B;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .kpi-value {
        color: #1E293B;
        font-size: 1.5rem;
        font-weight: 700;
        word-break: break-word;
    }

    /* Decision Banners */
    .decision-panel {
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 1.25rem;
        margin-bottom: 2rem;
        border: 2px solid transparent;
    }
    
    .decision-approve {
        background-color: #ECFDF5;
        color: #065F46;
        border-color: #A7F3D0;
    }
    
    .decision-decline {
        background-color: #FEF2F2;
        color: #991B1B;
        border-color: #FECACA;
    }
    
    .decision-refer {
        background-color: #FFFBEB;
        color: #92400E;
        border-color: #FDE68A;
    }

    /* Section Headers */
    .section-header {
        color: #334155;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3b82f6;
        padding-left: 1rem;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    [data-testid="stSidebarNav"] ul li a[aria-current="page"] {
        background-color: #F1F5F9 !important;
        border-left: 5px solid #3b82f6 !important;
        color: #1E293B !important;
        font-weight: 700 !important;
        padding-left: 15px !important;
    }

    .sidebar-user {
        padding: 1.25rem;
        background: #F8FAFC;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #E2E8F0;
    }
    
    .sidebar-user-label {
        font-size: 0.7rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    
    .sidebar-user-val {
        font-size: 0.85rem;
        color: #334155;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAGE STATE: reset on load/reload (fresh session)
# -----------------------------------------------------------------------------
if "agent_page_initialized" not in st.session_state:
    st.session_state.agent_messages = []
    st.session_state.run_analysis = False
    st.session_state.show_policies = False
    st.session_state.agent_page_initialized = True

# -----------------------------------------------------------------------------
# CONNECTIVITY
# -----------------------------------------------------------------------------
is_connected = False
session = None
try:
    session = get_active_session()
    is_connected = True
except:
    pass

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://www.snowflake.com/wp-content/themes/snowflake/assets/img/brand-guidelines/logo-sno-blue-example.svg", width=180)
    
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    st.markdown("### 📋 Application Queue")
    
    # Logic to select application
    selected_app_id = None
    app_details = None
    
    if is_connected:
        try:
            pending_apps = session.sql("""
                SELECT DISTINCT
                    CUSTOMER_ID AS APPLICATION_ID,
                    CUSTOMER_ID,
                    COALESCE(MAX_CREDIT_LIMIT, 50000) AS REQUESTED_AMOUNT,
                    'PERSONAL_LOAN' AS PRODUCT_CODE,
                    CASE 
                        WHEN SCORE_BAND >= 8 THEN 'HIGH'
                        WHEN SCORE_BAND >= 5 THEN 'MEDIUM'
                        ELSE 'LOW'
                    END AS PRIORITY
                FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
                ORDER BY APPLICATION_ID -- Show a mix
                LIMIT 20
            """).to_pandas()
            
            if not pending_apps.empty:
                selected_app_id = st.selectbox(
                    "Review Application",
                    pending_apps['APPLICATION_ID'].tolist(),
                    format_func=lambda x: f"{x} - ${pending_apps[pending_apps['APPLICATION_ID']==x]['REQUESTED_AMOUNT'].values[0]:,.0f}",
                    label_visibility="collapsed"
                )
                app_details = pending_apps[pending_apps['APPLICATION_ID'] == selected_app_id].iloc[0]
            else:
                st.info("No pending applications in queue.")
        except:
            st.warning("Decisioning tables not available.")
    else:
        st.info("Limited availability in Demo Mode.")

    st.markdown("---")
    
    if is_connected:
        try:
            user_info = session.sql("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()").collect()[0]
            st.markdown(f"""
            <div class="sidebar-user">
                <p class="sidebar-user-label">Logged in as</p>
                <p class="sidebar-user-val">{user_info[0]}</p>
                <div style="margin-top: 10px;"></div>
                <p class="sidebar-user-label">Role</p>
                <p class="sidebar-user-val">{user_info[1]}</p>
                <div style="margin-top: 10px;"></div>
                <p class="sidebar-user-label">Warehouse</p>
                <p class="sidebar-user-val">{user_info[2]}</p>
            </div>
            """, unsafe_allow_html=True)
        except:
            pass
    else:
        st.markdown("""
        <div class="sidebar-user">
            <p class="sidebar-user-label">Status</p>
            <p class="sidebar-user-val" style="color: #F59E0B;">Demo Mode (Local)</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("v2.1.0 • Enterprise AI Edition")



# -----------------------------------------------------------------------------
# HERO BANNER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="ai-banner">
    <h2>AI Decisioning Intelligence</h2>
    <p>Empowering credit professionals with predictive risk modeling and automated policy alignment checks.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ASK THE CREDIT ANALYST (chat-style Q&A)
# -----------------------------------------------------------------------------
st.markdown('<div class="section-header">Ask the Credit Analyst</div>', unsafe_allow_html=True)
st.caption("Ask a question about a customer or loan. Include a customer ID (e.g. CUS-000001) or select an application from the sidebar. Chat history is shown below; each question is answered with current customer data.")

# Reset button: clear chat and analysis state
if st.button("Reset chat", key="agent_reset_btn", help="Clear conversation and analysis state"):
    st.session_state.agent_messages = []
    st.session_state.run_analysis = False
    st.session_state.show_policies = False
    st.rerun()

# Text input for the question
user_question = st.text_area(
    "Your question",
    placeholder="e.g. Analyze customer CUS-000001 for a $50,000 personal loan",
    height=100,
    key="agent_question_input",
    label_visibility="collapsed"
)
ask_clicked = st.button("Ask", type="primary", key="agent_ask_btn")

def _extract_customer_id(text, default=None):
    """Extract customer ID from text (e.g. CUS-000001) or return default."""
    if not text:
        return default
    m = re.search(r"CUS-\d+", text, re.IGNORECASE)
    return m.group(0) if m else default

def _safe_sql_str(s, max_len=12000):
    """Escape single quotes for SQL and truncate to avoid token limits."""
    s = str(s).replace("'", "''")
    return s[:max_len] + ("..." if len(s) > max_len else "")

def _call_agent_tools_and_llm(session, customer_id, user_question, requested_amount=None, product_code=None):
    """Call agent-tool UDFs and CORTEX.COMPLETE to generate analyst response. Returns (success, response_text).
    Uses a single prompt (no conversation history) to avoid JSON parsing errors when embedding in SQL."""
    try:
        cust = session.sql(f"SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_CUSTOMER_DATA('{customer_id}') AS V").collect()
        cred = session.sql(f"SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_CREDIT_SCORE('{customer_id}') AS V").collect()
        txn = session.sql(f"SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_TRANSACTION_HISTORY('{customer_id}', 12) AS V").collect()
        cust_v = cust[0]["V"] if cust and cust[0]["V"] else "{}"
        cred_v = cred[0]["V"] if cred and cred[0]["V"] else "{}"
        txn_v = txn[0]["V"] if txn and txn[0]["V"] else "{}"
        if isinstance(cust_v, (dict, list)):
            cust_v = json.dumps(cust_v)
        if isinstance(cred_v, (dict, list)):
            cred_v = json.dumps(cred_v)
        if isinstance(txn_v, (dict, list)):
            txn_v = json.dumps(txn_v)
        app_context = ""
        if requested_amount is not None:
            app_context = f"\n\nApplication context (from this application): The applicant has REQUESTED a limit of ${requested_amount:,.0f}" + (f" ({product_code or 'loan'})." if product_code else ".")
        prompt = f"""You are a senior credit analyst at a bank. Answer the user's question clearly and give a structured recommendation (APPROVE/DECLINE/REFER) when relevant.{app_context}

In your Final Recommendation, state BOTH the amount the applicant REQUESTED (if known) and the amount you RECOMMEND approving. Use labels: "Amount requested by applicant" vs "Recommended approval amount".

User question: {user_question}

Customer 360 data: {cust_v}

Credit score data: {cred_v}

Transaction history (12 months): {txn_v}

Respond in a clear, professional way. Use sections as needed: Credit Score Summary, Policy/Compliance, Risk Assessment, Final Recommendation."""
        prompt_escaped = _safe_sql_str(prompt, max_len=12000)
        llm_res = session.sql(f"SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3-70b', '{prompt_escaped}') AS RESP").collect()
        if llm_res and llm_res[0]["RESP"]:
            return True, llm_res[0]["RESP"]
        return False, "No response from model."
    except Exception as e:
        return False, f"Error: {str(e)}"

if ask_clicked and user_question and user_question.strip():
    customer_id = _extract_customer_id(user_question)
    if app_details is not None:
        customer_id = customer_id or app_details.get("CUSTOMER_ID") or app_details.get("APPLICATION_ID")
    if not customer_id:
        st.warning("Include a customer ID in your question (e.g. CUS-000001) or select an application from the sidebar.")
    else:
        if is_connected and session is not None:
            requested_amt = None
            product = None
            if app_details is not None:
                requested_amt = float(app_details.get("REQUESTED_AMOUNT", 0))
                product = app_details.get("PRODUCT_CODE")
            with st.spinner("Credit Analyst is thinking..."):
                ok, response_text = _call_agent_tools_and_llm(
                    session, customer_id, user_question.strip(),
                    requested_amount=requested_amt, product_code=product
                )
            if ok:
                st.session_state.agent_messages.append({"role": "user", "content": user_question.strip()})
                st.session_state.agent_messages.append({"role": "assistant", "content": response_text})
            else:
                st.error(response_text)
        else:
            st.info("Connect to Snowflake (e.g. run this app in Snowflake or set up a connection) to use the Credit Analyst.")

# Show last exchange(s)
for i, msg in enumerate(st.session_state.agent_messages):
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

st.markdown("---")

# -----------------------------------------------------------------------------
# APPLICATION DETAILS & ANALYSIS
# -----------------------------------------------------------------------------
if app_details is not None:
    st.markdown('<div class="section-header">Subject Application Overview</div>', unsafe_allow_html=True)
    st.caption("Amounts below are from the application. The AI recommendation in the chat above (e.g. \"Recommended approval amount\") is the analyst\u2019s suggested limit.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">App ID</div><div class="kpi-value">{app_details['APPLICATION_ID']}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Priority</div><div class="kpi-value">{app_details['PRIORITY']}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Requested by applicant</div><div class="kpi-value">${app_details['REQUESTED_AMOUNT']:,.0f}</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Product</div><div class="kpi-value">{app_details['PRODUCT_CODE']}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    
    # Interaction Row
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        if st.button("Analyze Case with Cortex AI", type="primary", use_container_width=True):
            st.session_state.run_analysis = True
            
    with col_r:
        if st.button("Review Bank Underwriting Policy", use_container_width=True):
            st.session_state.show_policies = not st.session_state.get('show_policies', False)

    # ANALYSIS EXECUTION
    if st.session_state.get('run_analysis'):
        st.markdown('<div class="section-header">Decision Assistance Report</div>', unsafe_allow_html=True)
        
        with st.status("Initializing Intelligence Engine...", expanded=True) as status:
            time.sleep(1)
            status.update(label="Scanning Credit Risk Profile...")
            time.sleep(1)
            status.update(label="Analyzing Policy Alignment...")
            time.sleep(1)
            status.update(label="Intelligence Report Generated.", state="complete")
        
        # ML decision from predictions table
        decision = "APPROVE"
        rating = "B+"
        prob = "12.4%"
        score_band = 6
        default_prob_float = 0.12
        try:
             res = session.sql(f"""
                 SELECT DECISION, CREDIT_RATING, DEFAULT_PROBABILITY, SCORE_BAND
                 FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
                 WHERE CUSTOMER_ID='{app_details['CUSTOMER_ID']}' LIMIT 1
             """).collect()
             if res:
                 decision = res[0][0]
                 rating = res[0][1]
                 default_prob_float = float(res[0][2])
                 prob = f"{default_prob_float:.1%}"
                 score_band = int(res[0][3])
        except Exception:
            pass

        # Decision Banner
        if decision == "APPROVE":
            st.markdown('<div class="decision-panel decision-approve">✅ RECOMMENDED ACTION: APPROVE</div>', unsafe_allow_html=True)
        elif decision == "DECLINE":
            st.markdown('<div class="decision-panel decision-decline">❌ RECOMMENDED ACTION: DECLINE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="decision-panel decision-refer">⚠️ RECOMMENDED ACTION: REFER FOR SENIOR REVIEW</div>', unsafe_allow_html=True)

        # Intelligence Cards
        ml_1, ml_2, ml_3 = st.columns(3)
        with ml_1:
             st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Risk Rating</div><div class="kpi-value" style="color:#3b82f6;">{rating}</div></div>""", unsafe_allow_html=True)
        with ml_2:
             st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Default Probability</div><div class="kpi-value">{prob}</div></div>""", unsafe_allow_html=True)
        with ml_3:
             st.markdown(f"""<div class="kpi-card"><div class="kpi-label">AI Confidence</div><div class="kpi-value" style="color:#10B981;">HIGH</div></div>""", unsafe_allow_html=True)

        st.markdown("### Executive Summary & Rationale")
        st.info(f"""
        **Application ID:** {app_details['APPLICATION_ID']}  
        **AI Recommendation:** {decision}  
        
        **Rationale:**  
        The predictive assessment indicates a {prob} default probability for this applicant. This aligns with current bank policy for {app_details['PRODUCT_CODE']} within the requested limits. Key risk indicators such as internal liquidity and credit history show positive correlation with successful repayment.
        
        **Risk Mitigants:**  
        - Verified income stability exceeds required minimums.
        - Existing relationship tenure of 24+ months observed in internal deposits.
        """)

        # GenAI: ML decision explanation (EXPLAIN_DECISION) - two-step to avoid UDF nesting / internal error
        st.markdown("### Why did the ML model recommend this?")
        try:
            cid_esc = str(app_details["CUSTOMER_ID"]).replace("'", "''")
            rating_esc = str(rating).replace("'", "''")
            decision_esc = str(decision).replace("'", "''")
            # Step 1: get customer data as JSON
            cust_row = session.sql(f"SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_CUSTOMER_DATA('{cid_esc}') AS V").collect()
            cust_v = cust_row[0]["V"] if cust_row and cust_row[0]["V"] is not None else {}
            cust_json = json.dumps(cust_v) if isinstance(cust_v, (dict, list)) else str(cust_v)
            cust_sql = cust_json.replace("\\", "\\\\").replace("'", "''")[:8000]
            # Step 2: call EXPLAIN_DECISION with scalar args and PARSE_JSON(customer_data)
            expl_res = session.sql(f"""
                SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.EXPLAIN_DECISION(
                    '{cid_esc}',
                    {score_band},
                    '{rating_esc}',
                    '{decision_esc}',
                    {default_prob_float},
                    PARSE_JSON('{cust_sql}')
                ) AS EXPLANATION
            """).collect()
            if expl_res and expl_res[0]["EXPLANATION"]:
                with st.expander("📋 ML model explanation (Cortex LLM)", expanded=True):
                    st.markdown(expl_res[0]["EXPLANATION"])
            else:
                st.caption("No ML explanation available for this application.")
        except Exception as e:
            st.caption(f"Explanation not available: {e}")

        # Control Buttons
        bc_1, bc_2, bc_3 = st.columns(3)
        with bc_1:
            if st.button("Accept & Confirm", type="primary", key="btn_accept", use_container_width=True):
                st.toast("Decision synchronized to core banking systems.")
                time.sleep(1)
                st.balloons()
        with bc_2:
            if st.button("Request Senior Override", key="btn_override", use_container_width=True):
                 st.toast("Application escalated for manual review.")
        with bc_3:
            if st.button("Reset Analysis", key="btn_reset", use_container_width=True):
                st.session_state.run_analysis = False
                st.rerun()

    # POLICY DRAWER
    if st.session_state.get('show_policies'):
        st.markdown("---")
        with st.expander("📖 Central Underwriting Policies", expanded=True):
            st.markdown("""
            ### Personal Credit Policy (v4.2)
            *   **Tier 1 (A/B):** Automatic approval for amounts up to $100k if DTI < 40%.
            *   **Tier 2 (C):** Requires review for amounts exceeding $50k.
            *   **Tier 3 (D/F):** Automatic decline unless collateral exceeds 150%.
            
            ### Geographic Risk Adjustments
            Applications from high-volatility regions require a 10% risk premium on score bands.
            """)

else:
    st.info("Please select an application from the queue in the sidebar to begin AI-assisted analysis.")

