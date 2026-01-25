"""
AI Credit Agent Page
Interactive interface for the Cortex AI Credit Decisioning Agent
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
import json
import time

st.set_page_config(page_title="AI Credit Agent", page_icon="🤖", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .agent-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    .message-user {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1976d2;
        margin: 1rem 0;
    }
    .message-agent {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #43a047;
        margin: 1rem 0;
    }
    .decision-approve {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .decision-decline {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .decision-refer {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session
try:
    session = get_active_session()
except Exception as e:
    st.error("❌ Unable to connect to Snowflake. Please configure Streamlit in Snowflake.")
    st.stop()

# Header
st.markdown("""
<div class="agent-header">
    <h1>🤖 AI Credit Decisioning Agent</h1>
    <p>Powered by Snowflake Cortex AI</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
This AI agent acts as a **Senior Credit Analyst**, evaluating applications using:
- **ML Credit Score** (XGBoost model)
- **Bank Policy Documents** (via Cortex Search)
- **Customer 360 Data** (unified from all sources)
- **Real-time Risk Assessment**
""")

# Sidebar - Application Selection
st.sidebar.header("📋 Select Application")

try:
    # Get pending applications
    pending_apps = session.sql("""
        SELECT 
            APPLICATION_ID, 
            CUSTOMER_ID, 
            REQUESTED_AMOUNT, 
            PRODUCT_CODE, 
            SUBMITTED_AT,
            PRIORITY
        FROM APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS
        WHERE STATUS = 'SUBMITTED'
        ORDER BY 
            CASE PRIORITY 
                WHEN 'URGENT' THEN 1 
                WHEN 'HIGH' THEN 2 
                ELSE 3 
            END,
            SUBMITTED_AT
        LIMIT 20
    """).to_pandas()
    
    if pending_apps.empty:
        st.sidebar.info("No pending applications in queue.")
        
        # Add sample application button
        if st.sidebar.button("➕ Create Sample Application"):
            # Create a sample application for testing
            result = session.sql("""
                CALL APP_ZONE.TRANSACTIONAL.SUBMIT_APPLICATION(
                    'CUS-000001',
                    'NEW_LOAN',
                    'PERSONAL',
                    50000,
                    36,
                    'Home renovation'
                )
            """).collect()
            st.sidebar.success("✓ Sample application created!")
            st.rerun()
    else:
        # Show pending applications
        selected_app_id = st.sidebar.selectbox(
            "Pending Applications",
            pending_apps['APPLICATION_ID'].tolist(),
            format_func=lambda x: f"{x[:12]}... - ${pending_apps[pending_apps['APPLICATION_ID']==x]['REQUESTED_AMOUNT'].values[0]:,.0f}"
        )
        
        if selected_app_id:
            app_details = pending_apps[pending_apps['APPLICATION_ID'] == selected_app_id].iloc[0]
            
            st.sidebar.markdown("---")
            st.sidebar.markdown(f"**Customer:** {app_details['CUSTOMER_ID']}")
            st.sidebar.markdown(f"**Amount:** ${app_details['REQUESTED_AMOUNT']:,.2f}")
            st.sidebar.markdown(f"**Product:** {app_details['PRODUCT_CODE']}")
            st.sidebar.markdown(f"**Priority:** {app_details['PRIORITY']}")
            
            # Get customer profile
            try:
                customer_profile = session.sql(f"""
                    SELECT 
                        FULL_NAME,
                        CREDIT_SCORE,
                        RISK_CATEGORY,
                        VERIFIED_ANNUAL_INCOME,
                        DEBT_TO_INCOME_RATIO,
                        RELATIONSHIP_TENURE_MONTHS,
                        TOTAL_DEPOSITS,
                        TOTAL_LOANS_OUTSTANDING
                    FROM ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED
                    WHERE CUSTOMER_ID = '{app_details['CUSTOMER_ID']}'
                """).to_pandas()
                
                if not customer_profile.empty:
                    cp = customer_profile.iloc[0]
                    
                    st.sidebar.markdown("### 📊 Customer Profile")
                    st.sidebar.metric("Credit Score", cp['CREDIT_SCORE'])
                    st.sidebar.metric("Risk Category", cp['RISK_CATEGORY'])
                    st.sidebar.metric("Annual Income", f"${cp['VERIFIED_ANNUAL_INCOME']:,.0f}")
                    st.sidebar.metric("DTI Ratio", f"{cp['DEBT_TO_INCOME_RATIO']:.1%}")
            except Exception as e:
                st.sidebar.warning(f"Unable to load customer profile: {e}")
            
            # Main content
            st.markdown("---")
            st.subheader("🎯 Application Details")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Application ID", app_details['APPLICATION_ID'][:12] + "...")
            with col2:
                st.metric("Customer ID", app_details['CUSTOMER_ID'])
            with col3:
                st.metric("Requested Amount", f"${app_details['REQUESTED_AMOUNT']:,.0f}")
            with col4:
                st.metric("Product", app_details['PRODUCT_CODE'])
            
            # Action buttons
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🤖 Run AI Agent Analysis", type="primary", use_container_width=True):
                    st.session_state.run_agent = True
            
            with col2:
                if st.button("📜 View Relevant Policies", use_container_width=True):
                    st.session_state.show_policies = True
            
            # Agent Analysis
            if st.session_state.get('run_agent'):
                st.markdown("---")
                st.subheader("🤖 AI Agent Analysis")
                
                with st.status("Agent is analyzing the application...", expanded=True) as status:
                    st.write("📊 Gathering customer profile...")
                    time.sleep(0.5)
                    
                    st.write("🎯 Running ML credit scoring model...")
                    time.sleep(0.5)
                    
                    st.write("📚 Searching relevant bank policies...")
                    time.sleep(0.5)
                    
                    st.write("🔍 Checking delinquency history...")
                    time.sleep(0.5)
                    
                    st.write("💰 Calculating debt-to-income ratio...")
                    time.sleep(0.5)
                    
                    st.write("🧠 Agent is formulating decision...")
                    
                    try:
                        # Call the Cortex Agent (simplified version)
                        # In production, this would call the actual agent function
                        st.write("⚠️ Note: This is a demo. In production, this would call:")
                        st.code("""
SELECT APP_ZONE.CORTEX.CREDIT_AGENT_EVALUATE(
    '{app_id}',
    '{cust_id}',
    {amount},
    36,
    '{product}'
)
                        """.format(
                            app_id=app_details['APPLICATION_ID'],
                            cust_id=app_details['CUSTOMER_ID'],
                            amount=app_details['REQUESTED_AMOUNT'],
                            product=app_details['PRODUCT_CODE']
                        ))
                        
                        # Simulated agent output for demo
                        agent_output = {
                            'final_recommendation': 'APPROVE',
                            'ml_score_band': 7,
                            'ml_credit_rating': 'B',
                            'agent_analysis': """
**CUSTOMER SUMMARY:**
The customer has a good credit profile with stable employment and adequate income.

**ML SCORE INTERPRETATION:**
- Score Band: 7/10 (B Rating)
- This indicates acceptable risk with standard approval criteria

**POLICY COMPLIANCE CHECK:**
✓ DTI Ratio: 35% (Within 50% limit)
✓ Credit Score: 720 (Above 650 threshold)
✓ No current delinquencies
✓ Relationship: 24+ months (good standing)

**RISK FACTORS:**
- None significant identified

**MITIGATING FACTORS:**
- Existing customer with positive payment history
- Stable employment (5+ years at current employer)
- Adequate deposit balances

**FINAL RECOMMENDATION: APPROVE**

Rationale: The customer meets all policy requirements for approval. The ML model 
recommends approval (Band 7/10), DTI is within limits, and there are no red flags 
in the credit history. Approved amount matches requested amount.
                            """
                        }
                        
                        status.update(label="✓ Analysis Complete!", state="complete", expanded=True)
                    except Exception as e:
                        st.error(f"Error running agent: {e}")
                        agent_output = None
                
                # Display Results
                if agent_output:
                    decision = agent_output.get('final_recommendation', 'REFER')
                    
                    # Decision Banner
                    if decision == 'APPROVE':
                        st.markdown('<div class="decision-approve">🟢 RECOMMENDED FOR APPROVAL</div>', unsafe_allow_html=True)
                    elif decision == 'DECLINE':
                        st.markdown('<div class="decision-decline">🔴 RECOMMENDED FOR DECLINE</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="decision-refer">🟡 REQUIRES HUMAN REVIEW</div>', unsafe_allow_html=True)
                    
                    st.markdown("")
                    
                    # ML Score
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("ML Score Band", f"{agent_output.get('ml_score_band', 'N/A')}/10")
                    with col2:
                        st.metric("Credit Rating", agent_output.get('ml_credit_rating', 'N/A'))
                    with col3:
                        st.metric("Recommendation", decision)
                    
                    # Analysis
                    st.markdown("### 📝 Detailed Analysis")
                    st.markdown(agent_output.get('agent_analysis', 'No analysis available'))
                    
                    # Action Buttons
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("✅ Accept Recommendation", type="primary", use_container_width=True):
                            st.success("✓ Decision recorded! Application updated.")
                            st.balloons()
                    
                    with col2:
                        if st.button("✏️ Override Decision", use_container_width=True):
                            st.info("Override workflow initiated")
                    
                    with col3:
                        if st.button("📤 Escalate", use_container_width=True):
                            st.info("Escalated to Credit Manager")
                    
                    with col4:
                        if st.button("🔄 Re-analyze", use_container_width=True):
                            st.rerun()
            
            # Policy Search
            if st.session_state.get('show_policies'):
                st.markdown("---")
                st.subheader("📜 Relevant Bank Policies")
                
                with st.expander("📄 Credit Scoring Model Usage Policy", expanded=True):
                    st.markdown("""
**Version 2.1 - Effective January 2025**

**Score Bands and Decisions:**
- Bands 8-10 (A+, A, B+): Auto Approve
- Bands 6-7 (B, C+): Approve
- Bands 4-5 (C, C-): Refer for review
- Bands 1-3 (D, E, F): Decline

**Credit Limits by Band:**
- Band 10: Up to 3.0x annual income
- Band 9: Up to 2.5x annual income
- Band 8: Up to 2.0x annual income
- Band 7: Up to 1.5x annual income
                    """)
                
                with st.expander("💰 Debt-to-Income Ratio Guidelines"):
                    st.markdown("""
**Maximum DTI Thresholds:**
- Personal Loans: 50%
- Mortgage: 45%
- Auto Loans: 45%
- Credit Cards: 40%

**Overrides:**
DTI up to 55% may be approved if:
- Credit score band >= 7
- Collateral coverage > 120%
- Employment in stable sector
                    """)

except Exception as e:
    st.error(f"Error loading applications: {e}")

# Footer
st.markdown("---")
st.caption("AI Credit Agent powered by Snowflake Cortex • Uses ML models, policy RAG, and real-time data")
