-- ============================================
-- Snowflake Credit Decisioning Platform
-- GenAI Phase 1: Create ML Decision Explanation Function
-- ============================================
-- Role: ACCOUNTADMIN

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;
USE SCHEMA AGENT_TOOLS;

-- ============================================
-- FUNCTION: EXPLAIN DECISION
-- ============================================
-- Uses Cortex LLM to generate human-readable explanations
-- for ML model decisions

CREATE OR REPLACE FUNCTION EXPLAIN_DECISION(
    customer_id VARCHAR,
    ml_score_band INTEGER,
    ml_credit_rating VARCHAR,
    ml_decision VARCHAR,
    ml_default_prob FLOAT,
    customer_data VARIANT
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',  -- Using Llama 3 70B model
        CONCAT(
            'You are a credit analyst explaining a credit decision to a credit officer. ',
            'Generate a clear, professional explanation in 3-4 paragraphs. ',
            'Be specific about risk factors and cite numbers. ',
            'Use a professional but accessible tone.\n\n',
            'Customer ID: ', customer_id, '\n',
            'ML Score Band: ', ml_score_band, '/9\n',
            'Credit Rating: ', ml_credit_rating, '\n',
            'ML Recommendation: ', ml_decision, '\n',
            'Default Probability: ', ROUND(ml_default_prob * 100, 1), '%\n',
            'Customer Data: ', customer_data::VARCHAR, '\n\n',
            'Explain why the ML model made this recommendation, highlighting ',
            'the key factors that influenced the decision. Be specific about ',
            'what risk factors were considered and why this decision was made. ',
            'If approved, explain what makes this customer a good candidate. ',
            'If declined, explain the primary risk factors. ',
            'If referred, explain why manual review is needed.'
        )
    ) AS EXPLANATION
$$;

-- ============================================
-- ALTERNATIVE: Using Snowflake Arctic Model
-- ============================================
-- If Llama 3 is not available, use Snowflake Arctic

CREATE OR REPLACE FUNCTION EXPLAIN_DECISION_ARCTIC(
    customer_id VARCHAR,
    ml_score_band INTEGER,
    ml_credit_rating VARCHAR,
    ml_decision VARCHAR,
    ml_default_prob FLOAT,
    customer_data VARIANT
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic',  -- Using Snowflake Arctic model
        CONCAT(
            'You are a credit analyst explaining a credit decision. ',
            'Generate a clear explanation in 3-4 paragraphs.\n\n',
            'Customer ID: ', customer_id, '\n',
            'ML Score Band: ', ml_score_band, '/9\n',
            'Credit Rating: ', ml_credit_rating, '\n',
            'ML Recommendation: ', ml_decision, '\n',
            'Default Probability: ', ROUND(ml_default_prob * 100, 1), '%\n',
            'Customer Data: ', customer_data::VARCHAR, '\n\n',
            'Explain the ML model recommendation, highlighting key factors.'
        )
    ) AS EXPLANATION
$$;

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

GRANT USAGE ON FUNCTION CREDIT_DECISIONING_DB.AGENT_TOOLS.EXPLAIN_DECISION(
    VARCHAR, INTEGER, VARCHAR, VARCHAR, FLOAT, VARIANT
) TO ROLE SYSADMIN;

GRANT USAGE ON FUNCTION CREDIT_DECISIONING_DB.AGENT_TOOLS.EXPLAIN_DECISION_ARCTIC(
    VARCHAR, INTEGER, VARCHAR, VARCHAR, FLOAT, VARIANT
) TO ROLE SYSADMIN;

-- ============================================
-- TEST FUNCTION
-- ============================================
-- Test with sample data
-- Note: This requires actual customer data and ML predictions

/*
-- Example test (uncomment and modify with real data)
SELECT 
    'Test: Explanation Generation' AS TEST_NAME,
    EXPLAIN_DECISION(
        'CUS-000001',
        8,
        'B+',
        'APPROVE',
        0.15,
        PARSE_JSON('{"CUSTOMER_ID": "CUS-000001", "CREDIT_SCORE": 720, "DEBT_TO_INCOME_RATIO": 0.32}')
    ) AS EXPLANATION;
*/

-- ============================================
-- VERIFICATION
-- ============================================

SELECT 
    'Explanation functions created successfully' AS STATUS,
    FUNCTION_NAME,
    FUNCTION_TYPE
FROM INFORMATION_SCHEMA.FUNCTIONS
WHERE FUNCTION_SCHEMA = 'AGENT_TOOLS'
AND FUNCTION_NAME LIKE 'EXPLAIN_DECISION%'
ORDER BY FUNCTION_NAME;
