-- ============================================
-- Snowflake Credit Decisioning Platform
-- ML: Create Real-Time Inference UDF
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;
USE SCHEMA ML_INFERENCE;

-- ============================================
-- REAL-TIME CREDIT SCORE PREDICTION UDF
-- ============================================
-- This UDF loads the trained model and makes predictions
-- Usage: SELECT ML_INFERENCE.PREDICT_CREDIT_SCORE(...)

CREATE OR REPLACE FUNCTION PREDICT_CREDIT_SCORE(
    age INTEGER,
    annual_income FLOAT,
    debt_to_income FLOAT,
    credit_score INTEGER,
    credit_utilization FLOAT,
    relationship_months INTEGER,
    total_accounts INTEGER,
    total_balance FLOAT,
    avg_balance FLOAT,
    total_loans INTEGER,
    total_outstanding FLOAT,
    total_monthly_payment FLOAT,
    txn_count_3m INTEGER,
    txn_amount_3m FLOAT,
    avg_txn_amount_3m FLOAT,
    txn_velocity_3m FLOAT,
    total_tradelines INTEGER,
    open_tradelines INTEGER,
    delinquent_tradelines INTEGER,
    public_records INTEGER,
    inquiries_6m INTEGER,
    inquiries_12m INTEGER,
    login_count INTEGER,
    session_count_30d INTEGER,
    avg_session_duration FLOAT,
    event_count_30d INTEGER,
    days_since_last_login INTEGER,
    gender_encoded INTEGER,
    marital_status_encoded INTEGER,
    employment_status_encoded INTEGER,
    property_owner INTEGER,
    is_active INTEGER,
    mfa_enabled INTEGER,
    biometric_enabled INTEGER,
    high_risk INTEGER,
    kyc_verified INTEGER
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('snowflake-ml-python', 'xgboost')
HANDLER = 'predict'
AS
$$
from snowflake.ml.registry import Registry
from snowflake.snowpark.context import get_active_session
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
        _model = registry.get_model("CREDIT_SCORING_XGBOOST").version("v1").load()
    return _model

def predict(age, annual_income, debt_to_income, credit_score, credit_utilization,
            relationship_months, total_accounts, total_balance, avg_balance,
            total_loans, total_outstanding, total_monthly_payment,
            txn_count_3m, txn_amount_3m, avg_txn_amount_3m, txn_velocity_3m,
            total_tradelines, open_tradelines, delinquent_tradelines,
            public_records, inquiries_6m, inquiries_12m,
            login_count, session_count_30d, avg_session_duration,
            event_count_30d, days_since_last_login,
            gender_encoded, marital_status_encoded, employment_status_encoded,
            property_owner, is_active, mfa_enabled, biometric_enabled,
            high_risk, kyc_verified):
    
    session = get_active_session()
    model = get_model(session)
    
    # Create input dataframe
    input_data = session.create_dataframe([[
        age, annual_income, debt_to_income, credit_score, credit_utilization,
        relationship_months, total_accounts, total_balance, avg_balance,
        total_loans, total_outstanding, total_monthly_payment,
        txn_count_3m, txn_amount_3m, avg_txn_amount_3m, txn_velocity_3m,
        total_tradelines, open_tradelines, delinquent_tradelines,
        public_records, inquiries_6m, inquiries_12m,
        login_count, session_count_30d, avg_session_duration,
        event_count_30d, days_since_last_login,
        gender_encoded, marital_status_encoded, employment_status_encoded,
        property_owner, is_active, mfa_enabled, biometric_enabled,
        high_risk, kyc_verified
    ]], schema=[
        'F_AGE', 'F_ANNUAL_INCOME', 'F_DEBT_TO_INCOME',
        'F_CREDIT_SCORE', 'F_CREDIT_UTILIZATION', 'F_RELATIONSHIP_MONTHS',
        'F_TOTAL_ACCOUNTS', 'F_TOTAL_BALANCE', 'F_AVG_BALANCE',
        'F_TOTAL_LOANS', 'F_TOTAL_OUTSTANDING', 'F_TOTAL_MONTHLY_PAYMENT',
        'F_TXN_COUNT_3M', 'F_TXN_AMOUNT_3M', 'F_AVG_TXN_AMOUNT_3M',
        'F_TXN_VELOCITY_3M', 'F_TOTAL_TRADELINES', 'F_OPEN_TRADELINES',
        'F_DELINQUENT_TRADELINES', 'F_PUBLIC_RECORDS', 'F_INQUIRIES_6M',
        'F_INQUIRIES_12M', 'F_LOGIN_COUNT', 'F_SESSION_COUNT_30D',
        'F_AVG_SESSION_DURATION', 'F_EVENT_COUNT_30D', 'F_DAYS_SINCE_LAST_LOGIN',
        'F_GENDER_ENCODED', 'F_MARITAL_STATUS_ENCODED', 'F_EMPLOYMENT_STATUS_ENCODED',
        'F_PROPERTY_OWNER', 'F_IS_ACTIVE', 'F_MFA_ENABLED', 'F_BIOMETRIC_ENABLED',
        'F_HIGH_RISK', 'F_KYC_VERIFIED'
    ])
    
    # Get prediction
    result = model.predict(input_data).collect()[0]
    score_band = int(result['PREDICTED_SCORE_BAND'])
    
    # Map score band to credit rating and decision
    credit_ratings = ['F', 'E', 'D', 'C-', 'C', 'C+', 'B', 'B+', 'A', 'A+']
    credit_rating = credit_ratings[score_band] if score_band < len(credit_ratings) else 'F'
    
    # Credit limit multipliers by score band
    credit_limit_multipliers = [0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    multiplier = credit_limit_multipliers[score_band] if score_band < len(credit_limit_multipliers) else 0
    
    decision = 'APPROVE' if score_band >= 5 else 'DECLINE'
    max_credit_limit = int(annual_income * multiplier) if annual_income > 0 else 0
    
    # Estimate default probability (simplified - would use probability from model)
    default_probability = max(0.0, min(1.0, (10 - score_band) / 10.0))
    
    return {
        'score_band': score_band,
        'credit_rating': credit_rating,
        'decision': decision,
        'max_credit_limit': max_credit_limit,
        'default_probability': round(default_probability, 3),
        'confidence': 'HIGH' if score_band >= 7 or score_band <= 2 else 'MEDIUM'
    }
$$;

-- Grant permissions
GRANT USAGE ON FUNCTION ML_INFERENCE.PREDICT_CREDIT_SCORE TO ROLE SYSADMIN;

-- Test the function
SELECT 'Inference UDF created successfully!' AS STATUS;

-- Example usage (commented out - uncomment to test after model is trained)
/*
SELECT ML_INFERENCE.PREDICT_CREDIT_SCORE(
    35,      -- age
    75000,   -- annual_income
    0.25,    -- debt_to_income
    720,     -- credit_score
    0.3,     -- credit_utilization
    24,      -- relationship_months
    2,       -- total_accounts
    5000,    -- total_balance
    2500,    -- avg_balance
    1,       -- total_loans
    15000,   -- total_outstanding
    500,     -- total_monthly_payment
    45,      -- txn_count_3m
    5000,    -- txn_amount_3m
    111,     -- avg_txn_amount_3m
    0.5,     -- txn_velocity_3m
    5,       -- total_tradelines
    3,       -- open_tradelines
    0,       -- delinquent_tradelines
    0,       -- public_records
    2,       -- inquiries_6m
    3,       -- inquiries_12m
    50,      -- login_count
    20,      -- session_count_30d
    300,     -- avg_session_duration
    150,     -- event_count_30d
    5,       -- days_since_last_login
    1,       -- gender_encoded
    2,       -- marital_status_encoded
    1,       -- employment_status_encoded
    1,       -- property_owner
    1,       -- is_active
    1,       -- mfa_enabled
    1,       -- biometric_enabled
    0,       -- high_risk
    1        -- kyc_verified
) AS prediction;
*/
