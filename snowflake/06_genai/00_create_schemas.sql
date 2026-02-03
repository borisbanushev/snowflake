-- ============================================
-- Snowflake Credit Decisioning Platform
-- GenAI Phase 1: Create Schemas
-- ============================================
-- Role: ACCOUNTADMIN (required for schema creation and grants)

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;

-- ============================================
-- CREATE CORTEX SCHEMA
-- ============================================
-- Note: Snowflake has Database > Schema (no nested schemas).
-- APP_ZONE is a schema in CREDIT_DECISIONING_DB, not a database.
-- So we create CORTEX and AGENT_TOOLS as schemas in the current database.

CREATE SCHEMA IF NOT EXISTS CORTEX
  COMMENT = 'Cortex AI services - Search, Agents, LLM functions';

-- ============================================
-- CREATE AGENT TOOLS SCHEMA
-- ============================================

CREATE SCHEMA IF NOT EXISTS AGENT_TOOLS
  COMMENT = 'Functions and tools for Cortex Agents';

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

GRANT USAGE ON SCHEMA CORTEX TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA AGENT_TOOLS TO ROLE SYSADMIN;

-- ============================================
-- VERIFICATION
-- ============================================

SELECT 
    'Schemas created successfully' AS STATUS,
    SCHEMA_NAME,
    SCHEMA_OWNER
FROM INFORMATION_SCHEMA.SCHEMATA
WHERE SCHEMA_NAME IN ('CORTEX', 'AGENT_TOOLS')
AND CATALOG_NAME = 'CREDIT_DECISIONING_DB'
ORDER BY SCHEMA_NAME;
