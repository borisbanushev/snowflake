-- ============================================
-- Snowflake Credit Decisioning Platform
-- ML: Create Simplified Real-Time Inference UDF
-- This version takes CUSTOMER_ID and looks up features automatically
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;
USE SCHEMA ML_INFERENCE;

-- ============================================
-- SIMPLIFIED CREDIT SCORE PREDICTION STORED PROCEDURE
-- ============================================
-- This version takes CUSTOMER_ID and automatically gets features from feature store
-- Note: Using Stored Procedure instead of UDF because UDFs don't support get_active_session()
-- Usage: CALL ML_INFERENCE.PREDICT_CREDIT_SCORE_BY_ID_V4('CUST001');

CREATE OR REPLACE PROCEDURE PREDICT_CREDIT_SCORE_BY_ID_V4(customer_id VARCHAR(16777216))
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('snowflake-ml-python', 'xgboost', 'snowflake-snowpark-python')
HANDLER = 'predict'
AS
$$
from snowflake.ml.registry import Registry
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import functions as F
import json

# Cache model loading
_model = None

def get_model(session):
    global _model
    if _model is None:
        registry = Registry(
            session=session,
            database_name="CREDIT_DECISIONING_DB",
            schema_name="ML_MODELS"
        )
        # Use force=True to bypass version check (model was trained with different package versions)
        _model = registry.get_model("CREDIT_SCORING_XGBOOST").version("v1").load(force=True)
    return _model

def predict(session, customer_id):
    model = get_model(session)
    
    # Get features from feature store
    feature_df = session.table("ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES").filter(
        F.col("CUSTOMER_ID") == customer_id
    )
    
    if feature_df.count() == 0:
        return {
            'error': f'Customer {customer_id} not found in feature store',
            'customer_id': customer_id
        }
    
    # Get prediction (model returns remapped 0-based, need to add min_target back)
    result = model.predict(feature_df).collect()[0]
    score_band_remapped = int(result['PREDICTED_SCORE_BAND'])
    
    # Remap back to original scale (add minimum target value)
    # Assuming original scale is 2-9, so add 2. In production, store this in model metadata.
    min_target = 2  # This should match what was used in training
    score_band = score_band_remapped + min_target
    
    # Map score band to credit rating and decision
    credit_ratings = ['F', 'E', 'D', 'C-', 'C', 'C+', 'B', 'B+', 'A', 'A+']
    credit_rating = credit_ratings[score_band] if score_band < len(credit_ratings) else 'F'
    
    # Get annual income estimate from feature store (using total balance as proxy)
    feature_row = feature_df.collect()[0]
    estimated_annual_income = float(feature_row['F_TOTAL_BALANCE']) * 12 if feature_row['F_TOTAL_BALANCE'] else 50000
    
    # Credit limit multipliers by score band
    credit_limit_multipliers = [0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    multiplier = credit_limit_multipliers[score_band] if score_band < len(credit_limit_multipliers) else 0
    
    decision = 'APPROVE' if score_band >= 5 else 'DECLINE'
    max_credit_limit = int(estimated_annual_income * multiplier) if estimated_annual_income > 0 else 0
    
    # Estimate default probability
    default_probability = max(0.0, min(1.0, (10 - score_band) / 10.0))
    
    return {
        'customer_id': customer_id,
        'score_band': score_band,
        'credit_rating': credit_rating,
        'decision': decision,
        'max_credit_limit': max_credit_limit,
        'default_probability': round(default_probability, 3),
        'confidence': 'HIGH' if score_band >= 7 or score_band <= 2 else 'MEDIUM'
    }
$$;

-- Grant permissions
GRANT USAGE ON PROCEDURE ML_INFERENCE.PREDICT_CREDIT_SCORE_BY_ID_V4(VARCHAR) TO ROLE SYSADMIN;

SELECT 'Simplified inference Stored Procedure created successfully!' AS STATUS;

-- Test the procedure (uncomment after model is trained)
-- Note: Stored Procedures use CALL syntax, not SELECT
/*
CALL ML_INFERENCE.PREDICT_CREDIT_SCORE_BY_ID_V4('CUS-000001');

-- Or try with a customer ID from your actual data:
CALL ML_INFERENCE.PREDICT_CREDIT_SCORE_BY_ID_V4(
    (SELECT CUSTOMER_ID FROM ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES LIMIT 1)
);
*/
