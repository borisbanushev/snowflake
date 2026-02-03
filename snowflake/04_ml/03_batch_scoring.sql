-- ============================================
-- Snowflake Credit Decisioning Platform
-- ML: Batch Scoring - Score All Customers
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;
USE SCHEMA ML_PREDICTIONS;

-- ============================================
-- CREATE PREDICTIONS TABLE
-- ============================================

CREATE OR REPLACE TABLE CREDIT_SCORE_PREDICTIONS (
    CUSTOMER_ID VARCHAR(20),
    PREDICTION_DATE TIMESTAMP,
    SCORE_BAND INTEGER,
    CREDIT_RATING VARCHAR(10),
    DECISION VARCHAR(20),
    MAX_CREDIT_LIMIT INTEGER,
    DEFAULT_PROBABILITY DECIMAL(5,3),
    CONFIDENCE VARCHAR(10),
    PREDICTION_DETAILS VARIANT,
    CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================
-- BATCH SCORE ALL CUSTOMERS
-- ============================================
-- NOTE: Batch scoring should be done using the Python Notebook script:
--       03_batch_scoring.py (run in Snowflake Notebooks)
--
-- This SQL file creates the predictions table structure.
-- The actual batch scoring is performed by the Python script which has
-- access to Snowpark sessions needed for ML model inference.
--
-- To run batch scoring:
-- 1. Open Snowflake Notebooks
-- 2. Create new notebook
-- 3. Copy contents of 03_batch_scoring.py
-- 4. Run all cells
--
-- Alternatively, you can score individual customers using:
-- CALL ML_INFERENCE.PREDICT_CREDIT_SCORE_BY_ID('CUSTOMER_ID');

-- ============================================
-- VALIDATION QUERIES (run after batch scoring)
-- ============================================

-- Summary statistics
SELECT 
    'Batch Scoring Complete' AS STATUS,
    COUNT(*) AS TOTAL_PREDICTIONS,
    COUNT(DISTINCT CUSTOMER_ID) AS CUSTOMERS_SCORED,
    SUM(CASE WHEN DECISION = 'APPROVE' THEN 1 ELSE 0 END) AS APPROVED_COUNT,
    SUM(CASE WHEN DECISION = 'DECLINE' THEN 1 ELSE 0 END) AS DECLINED_COUNT,
    AVG(SCORE_BAND) AS AVG_SCORE_BAND,
    AVG(DEFAULT_PROBABILITY) AS AVG_DEFAULT_PROBABILITY
FROM CREDIT_SCORE_PREDICTIONS;

-- Distribution by credit rating
SELECT 
    CREDIT_RATING,
    COUNT(*) AS CUSTOMER_COUNT,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS PERCENTAGE
FROM CREDIT_SCORE_PREDICTIONS
GROUP BY CREDIT_RATING
ORDER BY CREDIT_RATING DESC;

-- Distribution by decision
SELECT 
    DECISION,
    COUNT(*) AS CUSTOMER_COUNT,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS PERCENTAGE
FROM CREDIT_SCORE_PREDICTIONS
GROUP BY DECISION
ORDER BY DECISION;

-- Grant permissions
GRANT SELECT ON TABLE ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS TO ROLE SYSADMIN;

SELECT 'Predictions table created! Run 03_batch_scoring.py in Snowflake Notebooks to score all customers.' AS STATUS;
