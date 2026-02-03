-- ============================================
-- Snowflake Openflow: PostgreSQL RDS Connector
-- ============================================
-- Purpose: Configure Snowflake to ingest data from PostgreSQL RDS via Openflow
-- Database: CREDIT_DECISIONING_DB
-- Source: AWS RDS PostgreSQL (Singapore)
-- Tables: digital_customer_profile, digital_session, digital_event
-- ============================================

-- Switch to appropriate role
USE ROLE ACCOUNTADMIN;

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS CREDIT_DECISIONING_DB;

-- Create schemas for PostgreSQL data
CREATE SCHEMA IF NOT EXISTS CREDIT_DECISIONING_DB.GOVERNANCE;
CREATE SCHEMA IF NOT EXISTS CREDIT_DECISIONING_DB.RAW_ZONE;
CREATE SCHEMA IF NOT EXISTS CREDIT_DECISIONING_DB.POSTGRESQL_SRC;

-- Create secret for PostgreSQL credentials
CREATE OR REPLACE SECRET CREDIT_DECISIONING_DB.GOVERNANCE.postgres_rds_password
TYPE = password
USERNAME = 'digitaluser'
PASSWORD = 'DigitalPass123!';

-- Grant privileges to Openflow role (replace with your actual Openflow role)
-- Find your role in Openflow UI -> View Details -> Runtime Role
GRANT USAGE ON DATABASE CREDIT_DECISIONING_DB TO ROLE BORIS8B_OPENFLOW_ROLE;
GRANT USAGE ON SCHEMA CREDIT_DECISIONING_DB.GOVERNANCE TO ROLE BORIS8B_OPENFLOW_ROLE;
GRANT USAGE ON SCHEMA CREDIT_DECISIONING_DB.RAW_ZONE TO ROLE BORIS8B_OPENFLOW_ROLE;
GRANT USAGE ON SCHEMA CREDIT_DECISIONING_DB.POSTGRESQL_SRC TO ROLE BORIS8B_OPENFLOW_ROLE;
GRANT ALL ON SCHEMA CREDIT_DECISIONING_DB.POSTGRESQL_SRC TO ROLE BORIS8B_OPENFLOW_ROLE;
GRANT READ ON SECRET CREDIT_DECISIONING_DB.GOVERNANCE.postgres_rds_password TO ROLE BORIS8B_OPENFLOW_ROLE;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE BORIS8B_OPENFLOW_ROLE;

-- Create monitoring view for PostgreSQL Openflow status
CREATE OR REPLACE VIEW CREDIT_DECISIONING_DB.GOVERNANCE.OPENFLOW_POSTGRES_STATUS AS
SELECT 
    CURRENT_TIMESTAMP() AS check_time,
    'READY' AS status,
    'PostgreSQL Openflow connector configured' AS message;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- 1. Verify schemas exist
SHOW SCHEMAS IN DATABASE CREDIT_DECISIONING_DB;

-- 2. Verify secret exists
SHOW SECRETS IN SCHEMA CREDIT_DECISIONING_DB.GOVERNANCE;

-- 3. Verify grants to Openflow role
SHOW GRANTS TO ROLE BORIS8B_OPENFLOW_ROLE;

-- 4. After Openflow ingestion, verify data
USE DATABASE CREDIT_DECISIONING_DB;
USE SCHEMA POSTGRESQL_SRC;

-- Check row counts (run after Openflow sync)
SELECT 'digital_customer_profile' AS table_name, COUNT(*) AS row_count 
FROM digital_customer_profile
UNION ALL
SELECT 'digital_session', COUNT(*) 
FROM digital_session
UNION ALL
SELECT 'digital_event', COUNT(*) 
FROM digital_event;

-- Sample data from each table
SELECT * FROM digital_customer_profile LIMIT 10;
SELECT * FROM digital_session LIMIT 10;
SELECT * FROM digital_event LIMIT 10;

-- ============================================
-- PostgreSQL RDS CONNECTION DETAILS
-- ============================================
-- These will be filled after deploying PostgreSQL RDS
-- Run: ./scripts/deploy_postgres_rds.sh

-- PostgreSQL Endpoint: [Will be shown after deployment]
-- Format: snowflake-credit-demo-postgres.[random-id].ap-southeast-1.rds.amazonaws.com
-- Port: 5432
-- Database: digital_banking
-- Username: digitaluser
-- Password: DigitalPass123!

-- JDBC Connection String Format:
-- jdbc:postgresql://[ENDPOINT]:5432/digital_banking
