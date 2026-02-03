"""
Executive Dashboard
Portfolio overview, KPIs, and key metrics
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Executive Dashboard", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #29B5E8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .kpi-header {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #29B5E8;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Executive Dashboard")
st.markdown("---")

# Get Snowflake session
try:
    session = get_active_session()
except Exception as e:
    st.error("❌ Not connected to Snowflake. Please run this in Snowflake's Streamlit environment.")
    st.stop()

# ============================================
# Key Performance Indicators
# ============================================
st.header("🎯 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

try:
    # Get portfolio metrics
    metrics = session.sql("""
        SELECT 
            COUNT(DISTINCT CUSTOMER_ID) AS total_customers,
            SUM(CASE WHEN DECISION = 'APPROVE' THEN 1 ELSE 0 END) AS approved_count,
            SUM(CASE WHEN DECISION = 'DECLINE' THEN 1 ELSE 0 END) AS declined_count,
            ROUND(AVG(SCORE_BAND), 2) AS avg_score_band,
            ROUND(AVG(DEFAULT_PROBABILITY), 3) AS avg_default_prob,
            ROUND(AVG(MAX_CREDIT_LIMIT), 0) AS avg_credit_limit
        FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
    """).collect()[0]
    
    with col1:
        st.metric("Total Customers", f"{metrics[0]:,}")
    
    with col2:
        approval_rate = (metrics[1] / metrics[0] * 100) if metrics[0] > 0 else 0
        st.metric("Approval Rate", f"{approval_rate:.1f}%", f"{metrics[1]:,} approved")
    
    with col3:
        st.metric("Average Score Band", f"{metrics[3]:.1f}", f"Out of 10")
    
    with col4:
        st.metric("Avg Default Probability", f"{metrics[4]:.1%}", f"Risk indicator")
        
except Exception as e:
    st.warning(f"⚠️ Could not load metrics: {str(e)}")
    st.info("💡 Make sure batch scoring has been run to populate ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS")

st.markdown("---")

# ============================================
# Credit Score Distribution
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Credit Score Distribution")
    try:
        score_dist = session.sql("""
            SELECT 
                CREDIT_RATING,
                COUNT(*) AS customer_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
            FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
            GROUP BY CREDIT_RATING
            ORDER BY 
                CASE CREDIT_RATING
                    WHEN 'A+' THEN 1
                    WHEN 'A' THEN 2
                    WHEN 'B+' THEN 3
                    WHEN 'B' THEN 4
                    WHEN 'C+' THEN 5
                    WHEN 'C' THEN 6
                    WHEN 'C-' THEN 7
                    WHEN 'D' THEN 8
                    WHEN 'E' THEN 9
                    WHEN 'F' THEN 10
                END
        """).to_pandas()
        
        if not score_dist.empty:
            fig = px.bar(
                score_dist,
                x='CREDIT_RATING',
                y='customer_count',
                color='CREDIT_RATING',
                color_discrete_sequence=px.colors.sequential.Viridis_r,
                labels={'customer_count': 'Number of Customers', 'CREDIT_RATING': 'Credit Rating'},
                title="Customers by Credit Rating"
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    except Exception as e:
        st.error(f"Error loading score distribution: {str(e)}")

with col2:
    st.subheader("✅ Decision Breakdown")
    try:
        decision_dist = session.sql("""
            SELECT 
                DECISION,
                COUNT(*) AS count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
            FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
            GROUP BY DECISION
        """).to_pandas()
        
        if not decision_dist.empty:
            fig = px.pie(
                decision_dist,
                values='count',
                names='DECISION',
                color='DECISION',
                color_discrete_map={'APPROVE': '#38ef7d', 'DECLINE': '#f45c43'},
                title="Approval vs Decline Distribution"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show percentages
            for _, row in decision_dist.iterrows():
                st.write(f"**{row['DECISION']}**: {row['count']:,} customers ({row['percentage']}%)")
        else:
            st.info("No data available")
    except Exception as e:
        st.error(f"Error loading decision breakdown: {str(e)}")

st.markdown("---")

# ============================================
# Score Band Distribution
# ============================================
st.subheader("📊 Score Band Distribution")
try:
    score_bands = session.sql("""
        SELECT 
            SCORE_BAND,
            COUNT(*) AS customer_count,
            AVG(DEFAULT_PROBABILITY) AS avg_default_prob,
            AVG(MAX_CREDIT_LIMIT) AS avg_credit_limit
        FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
        GROUP BY SCORE_BAND
        ORDER BY SCORE_BAND
    """).to_pandas()
    
    if not score_bands.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=score_bands['SCORE_BAND'],
            y=score_bands['customer_count'],
            name='Customer Count',
            marker_color='#29B5E8',
            text=score_bands['customer_count'],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Distribution of Credit Score Bands",
            xaxis_title="Score Band (2-9)",
            yaxis_title="Number of Customers",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show detailed stats
        st.dataframe(
            score_bands.style.format({
                'customer_count': '{:,.0f}',
                'avg_default_prob': '{:.3f}',
                'avg_credit_limit': '${:,.0f}'
            }),
            use_container_width=True
        )
    else:
        st.info("No data available")
except Exception as e:
    st.error(f"Error loading score bands: {str(e)}")

st.markdown("---")

# ============================================
# Risk Analysis
# ============================================
st.subheader("⚠️ Risk Analysis")
col1, col2 = st.columns(2)

with col1:
    try:
        risk_by_confidence = session.sql("""
            SELECT 
                CONFIDENCE,
                COUNT(*) AS count,
                AVG(DEFAULT_PROBABILITY) AS avg_default_prob,
                AVG(SCORE_BAND) AS avg_score
            FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
            GROUP BY CONFIDENCE
            ORDER BY avg_default_prob DESC
        """).to_pandas()
        
        if not risk_by_confidence.empty:
            fig = px.bar(
                risk_by_confidence,
                x='CONFIDENCE',
                y='avg_default_prob',
                color='CONFIDENCE',
                color_discrete_map={'HIGH': '#f45c43', 'MEDIUM': '#ffa726', 'LOW': '#38ef7d'},
                labels={'avg_default_prob': 'Average Default Probability', 'CONFIDENCE': 'Confidence Level'},
                title="Average Default Probability by Confidence Level"
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    except Exception as e:
        st.error(f"Error loading risk analysis: {str(e)}")

with col2:
    try:
        # Default probability distribution
        default_prob = session.sql("""
            SELECT 
                CASE 
                    WHEN DEFAULT_PROBABILITY < 0.2 THEN 'Low Risk (<20%)'
                    WHEN DEFAULT_PROBABILITY < 0.4 THEN 'Medium Risk (20-40%)'
                    WHEN DEFAULT_PROBABILITY < 0.6 THEN 'High Risk (40-60%)'
                    ELSE 'Very High Risk (>60%)'
                END AS risk_category,
                COUNT(*) AS customer_count
            FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
            GROUP BY risk_category
            ORDER BY 
                CASE risk_category
                    WHEN 'Low Risk (<20%)' THEN 1
                    WHEN 'Medium Risk (20-40%)' THEN 2
                    WHEN 'High Risk (40-60%)' THEN 3
                    WHEN 'Very High Risk (>60%)' THEN 4
                END
        """).to_pandas()
        
        if not default_prob.empty:
            fig = px.bar(
                default_prob,
                x='risk_category',
                y='customer_count',
                color='risk_category',
                color_discrete_sequence=['#38ef7d', '#ffa726', '#ff9800', '#f45c43'],
                labels={'customer_count': 'Number of Customers', 'risk_category': 'Risk Category'},
                title="Customers by Risk Category"
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    except Exception as e:
        st.error(f"Error loading risk categories: {str(e)}")

st.markdown("---")

# ============================================
# Recent Predictions Table
# ============================================
st.subheader("📋 Recent Predictions")
try:
    recent = session.sql("""
        SELECT 
            CUSTOMER_ID,
            CREDIT_RATING,
            SCORE_BAND,
            DECISION,
            MAX_CREDIT_LIMIT,
            ROUND(DEFAULT_PROBABILITY, 3) AS DEFAULT_PROBABILITY,
            CONFIDENCE,
            PREDICTION_DATE
        FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
        ORDER BY PREDICTION_DATE DESC
        LIMIT 100
    """).to_pandas()
    
    if not recent.empty:
        st.dataframe(
            recent.style.format({
                'MAX_CREDIT_LIMIT': '${:,.0f}',
                'DEFAULT_PROBABILITY': '{:.3f}'
            }),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No predictions available")
except Exception as e:
    st.error(f"Error loading recent predictions: {str(e)}")
