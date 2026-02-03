"""
Portfolio Analytics
Risk analysis, trends, and portfolio metrics
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Portfolio Analytics", page_icon="📈", layout="wide")

st.title("📈 Portfolio Analytics")
st.markdown("---")

# Get Snowflake session
try:
    session = get_active_session()
except Exception as e:
    st.error("❌ Not connected to Snowflake. Please run this in Snowflake's Streamlit environment.")
    st.stop()

# ============================================
# Portfolio Summary
# ============================================
st.header("📊 Portfolio Summary")

col1, col2, col3, col4 = st.columns(4)

try:
    portfolio_summary = session.sql("""
        SELECT 
            COUNT(DISTINCT CUSTOMER_ID) AS total_customers,
            SUM(CASE WHEN DECISION = 'APPROVE' THEN MAX_CREDIT_LIMIT ELSE 0 END) AS total_approved_limit,
            SUM(MAX_CREDIT_LIMIT) AS total_potential_limit,
            AVG(DEFAULT_PROBABILITY) AS avg_default_prob
        FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
    """).collect()[0]
    
    with col1:
        st.metric("Total Customers", f"{portfolio_summary[0]:,}")
    
    with col2:
        st.metric("Total Approved Limit", f"${portfolio_summary[1]:,.0f}")
    
    with col3:
        st.metric("Total Potential Limit", f"${portfolio_summary[2]:,.0f}")
    
    with col4:
        st.metric("Avg Default Probability", f"{portfolio_summary[3]:.1%}")
        
except Exception as e:
    st.warning(f"⚠️ Could not load portfolio summary: {str(e)}")

st.markdown("---")

# ============================================
# Score Band Analysis
# ============================================
st.subheader("📊 Score Band Analysis")

col1, col2 = st.columns(2)

with col1:
    try:
        score_analysis = session.sql("""
            SELECT 
                SCORE_BAND,
                COUNT(*) AS CUSTOMER_COUNT,
                AVG(DEFAULT_PROBABILITY) AS AVG_DEFAULT_PROB,
                AVG(MAX_CREDIT_LIMIT) AS AVG_CREDIT_LIMIT,
                SUM(CASE WHEN DECISION = 'APPROVE' THEN 1 ELSE 0 END) AS APPROVED_COUNT
            FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
            GROUP BY SCORE_BAND
            ORDER BY SCORE_BAND
        """).to_pandas()
        
        if not score_analysis.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=score_analysis['SCORE_BAND'],
                y=score_analysis['CUSTOMER_COUNT'],
                name='Customers',
                marker_color='#29B5E8',
                text=score_analysis['CUSTOMER_COUNT'],
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Customer Distribution by Score Band",
                xaxis_title="Score Band",
                yaxis_title="Number of Customers",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    except Exception as e:
        st.error(f"Error: {str(e)}")

with col2:
    try:
        if not score_analysis.empty:
            # Approval rate by score band
            score_analysis['APPROVAL_RATE'] = (score_analysis['APPROVED_COUNT'] / score_analysis['CUSTOMER_COUNT'] * 100)
            
            fig = px.line(
                score_analysis,
                x='SCORE_BAND',
                y='APPROVAL_RATE',
                markers=True,
                title="Approval Rate by Score Band",
                labels={'APPROVAL_RATE': 'Approval Rate (%)', 'SCORE_BAND': 'Score Band'}
            )
            fig.update_layout(height=400)
            fig.update_traces(line_color='#38ef7d', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Show detailed table
if not score_analysis.empty:
    st.dataframe(
        score_analysis.style.format({
            'CUSTOMER_COUNT': '{:,.0f}',
            'AVG_DEFAULT_PROB': '{:.3f}',
            'AVG_CREDIT_LIMIT': '${:,.0f}',
            'APPROVED_COUNT': '{:,.0f}',
            'APPROVAL_RATE': '{:.1f}%'
        }),
        use_container_width=True
    )

st.markdown("---")

# ============================================
# Risk Distribution
# ============================================
st.subheader("⚠️ Risk Distribution")

col1, col2 = st.columns(2)

with col1:
    try:
        risk_dist = session.sql("""
            SELECT 
                CONFIDENCE,
                COUNT(*) AS COUNT,
                AVG(DEFAULT_PROBABILITY) AS AVG_DEFAULT_PROB,
                AVG(SCORE_BAND) AS AVG_SCORE_BAND
            FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
            GROUP BY CONFIDENCE
            ORDER BY AVG_DEFAULT_PROB DESC
        """).to_pandas()
        
        if not risk_dist.empty:
            fig = px.pie(
                risk_dist,
                values='COUNT',
                names='CONFIDENCE',
                title="Distribution by Confidence Level",
                color='CONFIDENCE',
                color_discrete_map={'HIGH': '#f45c43', 'MEDIUM': '#ffa726', 'LOW': '#38ef7d'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    except Exception as e:
        st.error(f"Error: {str(e)}")

with col2:
    try:
        # Default probability histogram
        default_prob = session.sql("""
            SELECT DEFAULT_PROBABILITY
            FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
            ORDER BY DEFAULT_PROBABILITY
        """).to_pandas()
        
        if not default_prob.empty:
            fig = px.histogram(
                default_prob,
                x='DEFAULT_PROBABILITY',
                nbins=20,
                title="Default Probability Distribution",
                labels={'DEFAULT_PROBABILITY': 'Default Probability', 'count': 'Number of Customers'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("---")

# ============================================
# Credit Limit Analysis
# ============================================
st.subheader("💰 Credit Limit Analysis")

try:
    credit_analysis = session.sql("""
        SELECT 
            CREDIT_RATING,
            COUNT(*) AS CUSTOMER_COUNT,
            AVG(MAX_CREDIT_LIMIT) AS AVG_LIMIT,
            MIN(MAX_CREDIT_LIMIT) AS MIN_LIMIT,
            MAX(MAX_CREDIT_LIMIT) AS MAX_LIMIT,
            SUM(MAX_CREDIT_LIMIT) AS TOTAL_LIMIT
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
    
    if not credit_analysis.empty:
        fig = px.bar(
            credit_analysis,
            x='CREDIT_RATING',
            y='AVG_LIMIT',
            color='CREDIT_RATING',
            color_discrete_sequence=px.colors.sequential.Viridis_r,
            title="Average Credit Limit by Rating",
            labels={'AVG_LIMIT': 'Average Credit Limit ($)', 'CREDIT_RATING': 'Credit Rating'}
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(
            credit_analysis.style.format({
                'CUSTOMER_COUNT': '{:,.0f}',
                'AVG_LIMIT': '${:,.0f}',
                'MIN_LIMIT': '${:,.0f}',
                'MAX_LIMIT': '${:,.0f}',
                'TOTAL_LIMIT': '${:,.0f}'
            }),
            use_container_width=True
        )
    else:
        st.info("No data available")
except Exception as e:
    st.error(f"Error: {str(e)}")

st.markdown("---")

# ============================================
# Portfolio Risk Metrics
# ============================================
st.subheader("🎯 Portfolio Risk Metrics")

try:
    risk_metrics = session.sql("""
        SELECT 
            CASE 
                WHEN DEFAULT_PROBABILITY < 0.2 THEN 'Low Risk (<20%)'
                WHEN DEFAULT_PROBABILITY < 0.4 THEN 'Medium Risk (20-40%)'
                WHEN DEFAULT_PROBABILITY < 0.6 THEN 'High Risk (40-60%)'
                ELSE 'Very High Risk (>60%)'
            END AS RISK_CATEGORY,
            COUNT(*) AS CUSTOMER_COUNT,
            SUM(MAX_CREDIT_LIMIT) AS TOTAL_EXPOSURE,
            AVG(DEFAULT_PROBABILITY) AS AVG_DEFAULT_PROB
        FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
        GROUP BY RISK_CATEGORY
        ORDER BY 
            CASE RISK_CATEGORY
                WHEN 'Low Risk (<20%)' THEN 1
                WHEN 'Medium Risk (20-40%)' THEN 2
                WHEN 'High Risk (40-60%)' THEN 3
                WHEN 'Very High Risk (>60%)' THEN 4
            END
    """).to_pandas()
    
    if not risk_metrics.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                risk_metrics,
                x='RISK_CATEGORY',
                y='CUSTOMER_COUNT',
                color='RISK_CATEGORY',
                color_discrete_sequence=['#38ef7d', '#ffa726', '#ff9800', '#f45c43'],
                title="Customers by Risk Category",
                labels={'CUSTOMER_COUNT': 'Number of Customers', 'RISK_CATEGORY': 'Risk Category'}
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                risk_metrics,
                x='RISK_CATEGORY',
                y='TOTAL_EXPOSURE',
                color='RISK_CATEGORY',
                color_discrete_sequence=['#38ef7d', '#ffa726', '#ff9800', '#f45c43'],
                title="Total Exposure by Risk Category",
                labels={'TOTAL_EXPOSURE': 'Total Exposure ($)', 'RISK_CATEGORY': 'Risk Category'}
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(
            risk_metrics.style.format({
                'CUSTOMER_COUNT': '{:,.0f}',
                'TOTAL_EXPOSURE': '${:,.0f}',
                'AVG_DEFAULT_PROB': '{:.3f}'
            }),
            use_container_width=True
        )
    else:
        st.info("No data available")
except Exception as e:
    st.error(f"Error: {str(e)}")
