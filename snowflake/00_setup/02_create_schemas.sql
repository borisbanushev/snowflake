-- ============================================
-- Snowflake Credit Decisioning Platform
-- Step 2: Create Schemas (Medallion Architecture)
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;

-- ============================================
-- BRONZE LAYER - Raw data ingestion
-- ============================================

CREATE SCHEMA IF NOT EXISTS RAW_ZONE 
  COMMENT = 'Bronze layer - raw ingested data from external sources';

CREATE SCHEMA IF NOT EXISTS RAW_ZONE.DATABRICKS_SRC 
  COMMENT = 'Databricks Polaris Iceberg tables - credit bureau and external data';

CREATE SCHEMA IF NOT EXISTS RAW_ZONE.MYSQL_SRC 
  COMMENT = 'MySQL Openflow CDC streams - digital banking data';

CREATE SCHEMA IF NOT EXISTS RAW_ZONE.ORACLE_T24_SRC 
  COMMENT = 'Oracle T24 Openflow CDC streams - core banking data';

-- ============================================
-- SILVER LAYER - Cleaned and validated data
-- ============================================

CREATE SCHEMA IF NOT EXISTS CURATED_ZONE 
  COMMENT = 'Silver layer - cleaned, validated, standardized data';

CREATE SCHEMA IF NOT EXISTS CURATED_ZONE.CUSTOMER 
  COMMENT = 'Customer entities';

CREATE SCHEMA IF NOT EXISTS CURATED_ZONE.ACCOUNTS 
  COMMENT = 'Account entities';

CREATE SCHEMA IF NOT EXISTS CURATED_ZONE.LOANS 
  COMMENT = 'Loan entities';

CREATE SCHEMA IF NOT EXISTS CURATED_ZONE.TRANSACTIONS 
  COMMENT = 'Transaction entities';

CREATE SCHEMA IF NOT EXISTS CURATED_ZONE.DIGITAL 
  COMMENT = 'Digital banking entities';

CREATE SCHEMA IF NOT EXISTS CURATED_ZONE.T24_MIGRATED 
  COMMENT = 'SnowConverted T24 procedures and functions';

-- ============================================
-- GOLD LAYER - Analytics and aggregations
-- ============================================

CREATE SCHEMA IF NOT EXISTS ANALYTICS_ZONE 
  COMMENT = 'Gold layer - unified analytics-ready data';

CREATE SCHEMA IF NOT EXISTS ANALYTICS_ZONE.CUSTOMER_360 
  COMMENT = 'Unified customer 360-degree views';

CREATE SCHEMA IF NOT EXISTS ANALYTICS_ZONE.FEATURE_STORE 
  COMMENT = 'ML feature engineering and feature store';

CREATE SCHEMA IF NOT EXISTS ANALYTICS_ZONE.METRICS 
  COMMENT = 'Business KPIs and metrics';

-- ============================================
-- ML ZONE - Machine learning assets
-- ============================================

CREATE SCHEMA IF NOT EXISTS ML_ZONE 
  COMMENT = 'Machine learning zone - models, training, inference';

CREATE SCHEMA IF NOT EXISTS ML_ZONE.TRAINING 
  COMMENT = 'Training datasets';

CREATE SCHEMA IF NOT EXISTS ML_ZONE.MODELS 
  COMMENT = 'Model registry';

CREATE SCHEMA IF NOT EXISTS ML_ZONE.INFERENCE 
  COMMENT = 'Prediction outputs and inference logs';

-- ============================================
-- APPLICATION ZONE - App layer
-- ============================================

CREATE SCHEMA IF NOT EXISTS APP_ZONE 
  COMMENT = 'Application layer - Streamlit, Cortex, Intelligence';

CREATE SCHEMA IF NOT EXISTS APP_ZONE.STREAMLIT 
  COMMENT = 'Streamlit application-specific objects';

CREATE SCHEMA IF NOT EXISTS APP_ZONE.CORTEX 
  COMMENT = 'Cortex AI objects - Search, Agent, Analyst';

CREATE SCHEMA IF NOT EXISTS APP_ZONE.TRANSACTIONAL 
  COMMENT = 'Hybrid Tables for OLTP workloads (Unistore)';

CREATE SCHEMA IF NOT EXISTS APP_ZONE.INTELLIGENCE 
  COMMENT = 'Snowflake Intelligence configurations';

-- ============================================
-- GOVERNANCE ZONE
-- ============================================

CREATE SCHEMA IF NOT EXISTS GOVERNANCE 
  COMMENT = 'Governance, security, and compliance';

CREATE SCHEMA IF NOT EXISTS GOVERNANCE.TAGS 
  COMMENT = 'Data classification tags';

CREATE SCHEMA IF NOT EXISTS GOVERNANCE.POLICIES 
  COMMENT = 'Security policies - masking, row access';

CREATE SCHEMA IF NOT EXISTS GOVERNANCE.AUDIT 
  COMMENT = 'Audit logging and access history';

CREATE SCHEMA IF NOT EXISTS GOVERNANCE.MIGRATION 
  COMMENT = 'SnowConvert migration tracking';

-- Grant usage
GRANT USAGE ON ALL SCHEMAS IN DATABASE CREDIT_DECISIONING_DB TO ROLE SYSADMIN;

SELECT 'All schemas created successfully' AS STATUS;
