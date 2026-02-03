"""
Customer 360 Viewer
Unified customer profile with credit score and financial data
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

st.set_page_config(page_title="Customer 360", page_icon="👥", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .customer-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    .score-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #29B5E8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .approve-badge {
        background: #38ef7d;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        display: inline-block;
        font-weight: bold;
    }
    .decline-badge {
        background: #f45c43;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        display: inline-block;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("👥 Customer 360")
st.markdown("---")

# Get Snowflake session
try:
    session = get_active_session()
except Exception as e:
    st.error("❌ Not connected to Snowflake. Please run this in Snowflake's Streamlit environment.")
    st.stop()

# ============================================
# Customer Search
# ============================================
col1, col2 = st.columns([3, 1])

with col1:
    customer_id = st.text_input(
        "🔍 Search Customer ID",
        placeholder="Enter customer ID (e.g., CUS-000001)",
        key="customer_search"
    )

with col2:
    st.write("")
    st.write("")
    if st.button("🔎 Search", type="primary"):
        st.session_state['search_customer'] = customer_id

# If customer ID provided, show details
if 'search_customer' in st.session_state and st.session_state['search_customer']:
    customer_id = st.session_state['search_customer']
    
    # ============================================
    # Credit Score Prediction
    # ============================================
    st.header(f"📊 Credit Score for {customer_id}")
    
    try:
        # Get prediction from batch scoring table
        prediction = session.sql(f"""
            SELECT 
                CUSTOMER_ID,
                CREDIT_RATING,
                SCORE_BAND,
                DECISION,
                MAX_CREDIT_LIMIT,
                DEFAULT_PROBABILITY,
                CONFIDENCE,
                PREDICTION_DETAILS,
                PREDICTION_DATE
            FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
            WHERE CUSTOMER_ID = '{customer_id}'
            ORDER BY PREDICTION_DATE DESC
            LIMIT 1
        """).collect()
        
        if prediction:
            pred = prediction[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Credit Rating", pred['CREDIT_RATING'])
            
            with col2:
                st.metric("Score Band", f"{pred['SCORE_BAND']}/9")
            
            with col3:
                decision_color = "🟢" if pred['DECISION'] == 'APPROVE' else "🔴"
                st.metric("Decision", f"{decision_color} {pred['DECISION']}")
            
            with col4:
                st.metric("Max Credit Limit", f"${pred['MAX_CREDIT_LIMIT']:,}")
            
            # Show prediction details
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Risk Metrics")
                st.metric("Default Probability", f"{pred['DEFAULT_PROBABILITY']:.1%}")
                st.metric("Confidence", pred['CONFIDENCE'])
                
                # Visualize default probability
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = float(pred['DEFAULT_PROBABILITY']) * 100,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Default Risk (%)"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 20], 'color': "lightgreen"},
                            {'range': [20, 40], 'color': "yellow"},
                            {'range': [40, 60], 'color': "orange"},
                            {'range': [60, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 50
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("💰 Credit Details")
                st.write(f"**Max Credit Limit:** ${pred['MAX_CREDIT_LIMIT']:,}")
                st.write(f"**Prediction Date:** {pred['PREDICTION_DATE']}")
                
                # Show prediction details JSON if available
                if pred['PREDICTION_DETAILS']:
                    st.subheader("📋 Full Prediction Details")
                    st.json(pred['PREDICTION_DETAILS'])
        else:
            st.warning(f"⚠️ No prediction found for customer {customer_id}")
            st.info("💡 Try using the stored procedure for real-time scoring:")
            st.code(f"CALL ML_INFERENCE.PREDICT_CREDIT_SCORE_BY_ID_V4('{customer_id}');", language="sql")
            
    except Exception as e:
        st.error(f"Error loading prediction: {str(e)}")
    
    st.markdown("---")
    
    # ============================================
    # Customer Features
    # ============================================
    st.header("🔧 Customer Features")
    
    try:
        features = session.sql(f"""
            SELECT *
            FROM ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES
            WHERE CUSTOMER_ID = '{customer_id}'
            LIMIT 1
        """).to_pandas()
        
        if not features.empty:
            # Display key features
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("👤 Demographics")
                if 'F_AGE' in features.columns:
                    st.write(f"**Age:** {features['F_AGE'].iloc[0]}")
                if 'F_RELATIONSHIP_MONTHS' in features.columns:
                    st.write(f"**Relationship:** {features['F_RELATIONSHIP_MONTHS'].iloc[0]} months")
            
            with col2:
                st.subheader("💳 Financial")
                if 'F_TOTAL_BALANCE' in features.columns:
                    st.write(f"**Total Balance:** ${features['F_TOTAL_BALANCE'].iloc[0]:,.2f}")
                if 'F_CREDIT_SCORE' in features.columns:
                    st.write(f"**Credit Score:** {features['F_CREDIT_SCORE'].iloc[0]}")
                if 'F_DEBT_TO_INCOME' in features.columns:
                    st.write(f"**Debt-to-Income:** {features['F_DEBT_TO_INCOME'].iloc[0]:.2%}")
            
            with col3:
                st.subheader("📊 Accounts & Loans")
                if 'F_TOTAL_ACCOUNTS' in features.columns:
                    st.write(f"**Total Accounts:** {features['F_TOTAL_ACCOUNTS'].iloc[0]}")
                if 'F_TOTAL_LOANS' in features.columns:
                    st.write(f"**Total Loans:** {features['F_TOTAL_LOANS'].iloc[0]}")
            
            # Show all features in expandable section
            with st.expander("📋 View All Features"):
                st.dataframe(features.T, use_container_width=True)
        else:
            st.warning(f"⚠️ No features found for customer {customer_id}")
            
    except Exception as e:
        st.error(f"Error loading features: {str(e)}")
    
    st.markdown("---")
    
    # ============================================
    # Customer 360 Unified View
    # ============================================
    st.header("🌐 Customer 360 Unified View")
    
    try:
        customer_360 = session.sql(f"""
            SELECT *
            FROM ANALYTICS_CUSTOMER_360.CUSTOMER_360_UNIFIED
            WHERE CUSTOMER_ID = '{customer_id}'
            LIMIT 1
        """).to_pandas()
        
        if not customer_360.empty:
            st.dataframe(customer_360, use_container_width=True)
        else:
            st.info("Customer 360 data not available")
    except Exception as e:
        st.info(f"Customer 360 view not available: {str(e)}")

else:
    # ============================================
    # Customer List
    # ============================================
    st.header("📋 All Customers")
    
    try:
        customers = session.sql("""
            SELECT 
                CUSTOMER_ID,
                CREDIT_RATING,
                SCORE_BAND,
                DECISION,
                MAX_CREDIT_LIMIT,
                DEFAULT_PROBABILITY,
                CONFIDENCE
            FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
            ORDER BY SCORE_BAND DESC, CUSTOMER_ID
            LIMIT 100
        """).to_pandas()
        
        if not customers.empty:
            st.dataframe(
                customers.style.format({
                    'MAX_CREDIT_LIMIT': '${:,.0f}',
                    'DEFAULT_PROBABILITY': '{:.3f}'
                }),
                use_container_width=True,
                height=600
            )
        else:
            st.info("No customers found")
    except Exception as e:
        st.error(f"Error loading customers: {str(e)}")
