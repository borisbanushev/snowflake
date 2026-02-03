-- ============================================
-- Snowflake Credit Decisioning Platform
-- Direct Load: Create Internal Stage for CSVs
-- ============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;

-- Create internal named stage for CSV uploads
CREATE OR REPLACE STAGE CSV_DATA_STAGE
  FILE_FORMAT = (
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE
    DATE_FORMAT = 'AUTO'
    TIMESTAMP_FORMAT = 'AUTO'
    ENCODING = 'UTF8'
  )
  COMMENT = 'Internal stage for CSV data uploads';

-- Grant privileges
GRANT USAGE ON STAGE CSV_DATA_STAGE TO ROLE SYSADMIN;

-- Verify stage is created
SHOW STAGES LIKE 'CSV_DATA_STAGE';

SELECT 'CSV stage created successfully' AS STATUS;
