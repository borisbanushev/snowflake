-- ============================================
-- Snowflake Credit Decisioning Platform
-- Direct Load: Create Schemas for CSV Data
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;

-- ============================================
-- Create Schemas for Different Data Sources
-- ============================================

-- Digital Banking Data (from simulated PostgreSQL)
CREATE SCHEMA IF NOT EXISTS DIGITAL_BANKING
  COMMENT = 'Digital banking customer data - profiles, sessions, events, KYC';

-- Core Banking Data (from simulated T24)
CREATE SCHEMA IF NOT EXISTS CORE_BANKING
  COMMENT = 'T24 core banking data - customers, accounts, loans, transactions';

-- Credit Bureau Data (from simulated external bureaus)
CREATE SCHEMA IF NOT EXISTS CREDIT_BUREAU
  COMMENT = 'Credit bureau data - scores, inquiries, tradelines, public records';

-- Reference Data (lookup tables)
CREATE SCHEMA IF NOT EXISTS REFERENCE_DATA
  COMMENT = 'Reference and lookup data - countries, currencies, products, branches';

-- Grant usage
GRANT USAGE ON SCHEMA DIGITAL_BANKING TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA CORE_BANKING TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA CREDIT_BUREAU TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA REFERENCE_DATA TO ROLE SYSADMIN;

SELECT 'All schemas created successfully' AS STATUS;
