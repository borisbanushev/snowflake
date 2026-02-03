# 📚 Snowflake Catalog View - External Data Sources

## Overview

Your Snowflake implementation will show all 3 external data sources clearly organized in the catalog, making data lineage and source tracking transparent.

---

## 🗂️ Catalog Structure

### Database: `CREDIT_DECISIONING_DB`

```
CREDIT_DECISIONING_DB
│
├── RAW_ZONE (Bronze Layer - External Sources)
│   │
│   ├── ORACLE_T24_SRC ⭐ (Source 1: Oracle T24 Core Banking)
│   │   ├── T24_CUSTOMER          [Openflow CDC]
│   │   ├── T24_ACCOUNT            [Openflow CDC]
│   │   ├── T24_LOAN               [Openflow CDC]
│   │   ├── T24_TRANSACTION        [Openflow CDC]
│   │   ├── T24_PAYMENT_SCHEDULE   [Openflow CDC]
│   │   └── T24_COLLATERAL         [Openflow CDC]
│   │
│   ├── MYSQL_SRC ⭐ (Source 2: MySQL Digital Banking)
│   │   ├── DIGITAL_CUSTOMER_PROFILE [Openflow CDC]
│   │   ├── DIGITAL_SESSION          [Openflow CDC]
│   │   ├── DIGITAL_EVENT            [Openflow CDC]
│   │   └── DIGITAL_KYC_DOCUMENT     [Openflow CDC]
│   │
│   └── DATABRICKS_SRC ⭐ (Source 3: Databricks via Polaris)
│       ├── CREDIT_BUREAU_REPORT     [Polaris/Iceberg]
│       ├── INCOME_VERIFICATION      [Polaris/Iceberg]
│       ├── ALTERNATIVE_DATA         [Polaris/Iceberg]
│       └── FRAUD_INDICATORS         [Polaris/Iceberg]
│
├── CURATED_ZONE (Silver Layer - Cleaned & Enriched)
│   ├── CUSTOMERS
│   ├── ACCOUNTS
│   ├── LOANS
│   ├── TRANSACTIONS
│   └── CREDIT_BUREAU
│
└── ANALYTICS_ZONE (Gold Layer - Business Ready)
    └── CUSTOMER_360
        └── CUSTOMER_360_UNIFIED (joins all 3 sources)
```

---

## 📊 Viewing External Sources in Snowflake

### Option 1: Snowflake Web UI

**Path:** Data → Databases → CREDIT_DECISIONING_DB → RAW_ZONE

You'll see 3 schemas:
```
📁 RAW_ZONE
  ├── 📁 ORACLE_T24_SRC     ← Oracle Cloud
  ├── 📁 MYSQL_SRC          ← MySQL Digital Banking  
  └── 📁 DATABRICKS_SRC     ← Databricks via Polaris
```

Click each schema to see the tables from that source.

---

### Option 2: SQL Queries

#### **List All External Source Schemas:**

```sql
USE DATABASE CREDIT_DECISIONING_DB;

-- Show all RAW_ZONE schemas (external sources)
SHOW SCHEMAS IN RAW_ZONE;
```

**Result:**
```
SCHEMA_NAME          | COMMENT
---------------------|----------------------------------
ORACLE_T24_SRC       | T24 Core Banking via Openflow CDC
MYSQL_SRC            | Digital Banking via Openflow CDC
DATABRICKS_SRC       | Credit Bureau via Polaris Catalog
```

#### **View Tables from Each Source:**

```sql
-- Oracle T24 tables
SHOW TABLES IN SCHEMA RAW_ZONE.ORACLE_T24_SRC;

-- MySQL Digital Banking tables  
SHOW TABLES IN SCHEMA RAW_ZONE.MYSQL_SRC;

-- Databricks Credit Bureau tables
SHOW TABLES IN SCHEMA RAW_ZONE.DATABRICKS_SRC;
```

#### **Get Table Details with Source Information:**

```sql
-- Comprehensive catalog view
SELECT 
    table_catalog,
    table_schema,
    table_name,
    table_type,
    row_count,
    bytes,
    CASE table_schema
        WHEN 'ORACLE_T24_SRC' THEN 'Oracle Cloud (Openflow CDC)'
        WHEN 'MYSQL_SRC' THEN 'MySQL Digital (Openflow CDC)'
        WHEN 'DATABRICKS_SRC' THEN 'Databricks (Polaris Catalog)'
        ELSE 'Snowflake Native'
    END as data_source_type,
    comment
FROM CREDIT_DECISIONING_DB.INFORMATION_SCHEMA.TABLES
WHERE table_schema IN ('ORACLE_T24_SRC', 'MYSQL_SRC', 'DATABRICKS_SRC')
ORDER BY table_schema, table_name;
```

**Sample Output:**
```
TABLE_SCHEMA      | TABLE_NAME              | TABLE_TYPE | ROW_COUNT | SOURCE_TYPE
------------------|-------------------------|------------|-----------|-----------------------------
DATABRICKS_SRC    | CREDIT_BUREAU_REPORT    | EXTERNAL   | 100,000   | Databricks (Polaris Catalog)
DATABRICKS_SRC    | INCOME_VERIFICATION     | EXTERNAL   | 100,000   | Databricks (Polaris Catalog)
MYSQL_SRC         | DIGITAL_CUSTOMER_PROFILE| EXTERNAL   | 100,000   | MySQL Digital (Openflow CDC)
MYSQL_SRC         | DIGITAL_EVENT           | EXTERNAL   | 500,000   | MySQL Digital (Openflow CDC)
ORACLE_T24_SRC    | T24_CUSTOMER            | EXTERNAL   | 100,000   | Oracle Cloud (Openflow CDC)
ORACLE_T24_SRC    | T24_ACCOUNT             | EXTERNAL   | 180,000   | Oracle Cloud (Openflow CDC)
ORACLE_T24_SRC    | T24_LOAN                | EXTERNAL   | 35,000    | Oracle Cloud (Openflow CDC)
```

---

### Option 3: Data Lineage View

Snowflake's Object Explorer shows the complete lineage:

```sql
-- See data lineage for unified customer table
SELECT * 
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE OBJECTS_MODIFIED_NAME = 'CUSTOMER_360_UNIFIED'
LIMIT 10;
```

This shows that `CUSTOMER_360_UNIFIED` pulls from:
- ✅ `RAW_ZONE.ORACLE_T24_SRC.T24_CUSTOMER`
- ✅ `RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE`
- ✅ `RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT`

---

## 🔍 Detailed Source Information

### Source 1: Oracle T24 (via Openflow CDC)

```sql
-- View Oracle source tables
SELECT 
    table_name,
    row_count,
    last_altered,
    comment
FROM CREDIT_DECISIONING_DB.INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'ORACLE_T24_SRC'
ORDER BY table_name;
```

**Connection Details:**
- **Technology:** Snowflake Openflow Connector
- **Method:** Log-based CDC (Change Data Capture)
- **Latency:** Near real-time (1-minute refresh)
- **Source System:** Oracle Autonomous Database / DB System
- **Tables:** 6 tables (Customer, Account, Loan, Transaction, Payment Schedule, Collateral)

**View Connector Status:**
```sql
SELECT 
    CONNECTOR_NAME,
    STATUS,
    LAST_SYNC_TIME,
    RECORDS_PROCESSED,
    ERROR_COUNT
FROM TABLE(INFORMATION_SCHEMA.CONNECTOR_HISTORY(
    CONNECTOR_NAME => 'ORACLE_T24_OPENFLOW_CONNECTOR'
))
ORDER BY LAST_SYNC_TIME DESC
LIMIT 10;
```

---

### Source 2: MySQL Digital Banking (via Openflow CDC)

```sql
-- View MySQL source tables
SELECT 
    table_name,
    row_count,
    last_altered,
    comment
FROM CREDIT_DECISIONING_DB.INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'MYSQL_SRC'
ORDER BY table_name;
```

**Connection Details:**
- **Technology:** Snowflake Openflow Connector
- **Method:** Binlog-based CDC
- **Latency:** High-frequency (30-second refresh)
- **Source System:** MySQL Cloud or On-Premises
- **Tables:** 4 tables (Customer Profile, Session, Event, KYC Documents)

**View Connector Status:**
```sql
SELECT 
    CONNECTOR_NAME,
    STATUS,
    LAST_SYNC_TIME,
    RECORDS_PROCESSED
FROM TABLE(INFORMATION_SCHEMA.CONNECTOR_HISTORY(
    CONNECTOR_NAME => 'MYSQL_DIGITAL_OPENFLOW_CONNECTOR'
))
ORDER BY LAST_SYNC_TIME DESC
LIMIT 10;
```

---

### Source 3: Databricks (via Polaris Catalog)

```sql
-- View Databricks source tables
SELECT 
    table_name,
    table_type,
    row_count,
    comment
FROM CREDIT_DECISIONING_DB.INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'DATABRICKS_SRC'
ORDER BY table_name;
```

**Connection Details:**
- **Technology:** Apache Polaris Open Catalog
- **Format:** Iceberg Tables / Delta Lake
- **Latency:** 5-minute refresh (configurable)
- **Source System:** Databricks Unity Catalog
- **Catalog:** main (or sowcatalog)
- **Schema:** credit_bureau
- **Tables:** 4 tables (Credit Bureau, Income Verification, Alternative Data, Fraud Indicators)

**View Polaris Sync Status:**
```sql
SELECT 
    TABLE_NAME,
    CATALOG_NAME,
    LAST_REFRESH_TIME,
    REFRESH_STATUS,
    CASE 
        WHEN REFRESH_STATUS = 'SUCCESS' AND 
             DATEDIFF('MINUTE', LAST_REFRESH_TIME, CURRENT_TIMESTAMP()) < 10 
        THEN 'HEALTHY'
        ELSE 'CHECK_NEEDED'
    END AS SYNC_HEALTH
FROM TABLE(INFORMATION_SCHEMA.ICEBERG_TABLE_REFRESH_HISTORY())
WHERE CATALOG_NAME = 'POLARIS_DATABRICKS_CATALOG'
ORDER BY LAST_REFRESH_TIME DESC;
```

---

## 📈 Unified Catalog View

### Query All External Sources at Once:

```sql
-- Complete external data source inventory
WITH source_summary AS (
  SELECT 
    'Oracle T24' as source_system,
    'ORACLE_T24_SRC' as schema_name,
    'Openflow CDC' as connection_type,
    '1 minute' as refresh_frequency,
    COUNT(*) as table_count,
    SUM(row_count) as total_rows
  FROM CREDIT_DECISIONING_DB.INFORMATION_SCHEMA.TABLES
  WHERE table_schema = 'ORACLE_T24_SRC'
  
  UNION ALL
  
  SELECT 
    'MySQL Digital',
    'MYSQL_SRC',
    'Openflow CDC',
    '30 seconds',
    COUNT(*),
    SUM(row_count)
  FROM CREDIT_DECISIONING_DB.INFORMATION_SCHEMA.TABLES
  WHERE table_schema = 'MYSQL_SRC'
  
  UNION ALL
  
  SELECT 
    'Databricks Credit Bureau',
    'DATABRICKS_SRC',
    'Polaris Catalog',
    '5 minutes',
    COUNT(*),
    SUM(row_count)
  FROM CREDIT_DECISIONING_DB.INFORMATION_SCHEMA.TABLES
  WHERE table_schema = 'DATABRICKS_SRC'
)
SELECT * FROM source_summary
ORDER BY source_system;
```

**Result:**
```
SOURCE_SYSTEM              | SCHEMA_NAME    | CONNECTION_TYPE  | REFRESH_FREQ | TABLE_COUNT | TOTAL_ROWS
---------------------------|----------------|------------------|--------------|-------------|------------
Databricks Credit Bureau   | DATABRICKS_SRC | Polaris Catalog  | 5 minutes    | 4           | 200,000
MySQL Digital              | MYSQL_SRC      | Openflow CDC     | 30 seconds   | 4           | 750,000
Oracle T24                 | ORACLE_T24_SRC | Openflow CDC     | 1 minute     | 6           | 315,000
```

---

## 🎯 What Users Will See

### In Streamlit Application:

**Data Sources Tab:**
```
External Data Sources
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Oracle T24 Core Banking
   Connection: Openflow CDC
   Status: ● Active (Synced 30 seconds ago)
   Tables: 6 tables, 315,000 records
   
✅ MySQL Digital Banking  
   Connection: Openflow CDC
   Status: ● Active (Synced 15 seconds ago)
   Tables: 4 tables, 750,000 records
   
✅ Databricks Credit Bureau
   Connection: Polaris Catalog
   Status: ● Active (Synced 2 minutes ago)
   Tables: 4 tables, 200,000 records
```

### In Governance Dashboard:

```sql
-- Data source governance view
SELECT 
    table_schema as data_source,
    table_name,
    row_count,
    bytes / (1024*1024*1024) as size_gb,
    last_altered,
    retention_time,
    ARRAY_AGG(DISTINCT tag_value) as data_classifications
FROM CREDIT_DECISIONING_DB.INFORMATION_SCHEMA.TABLES t
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES tr
    ON t.table_name = tr.object_name
WHERE table_schema IN ('ORACLE_T24_SRC', 'MYSQL_SRC', 'DATABRICKS_SRC')
GROUP BY 1,2,3,4,5,6
ORDER BY data_source, table_name;
```

---

## 🔗 Cross-Source Queries

You can query across all 3 sources seamlessly:

```sql
-- Customer 360 view joining all 3 sources
SELECT 
    -- From Oracle T24
    o.CUSTOMER_ID,
    o.NAME_1 as FULL_NAME,
    o.DATE_OF_BIRTH,
    o.CUSTOMER_SINCE,
    
    -- From MySQL Digital Banking
    m.EMAIL,
    m.LAST_LOGIN,
    m.MFA_ENABLED,
    m.EKYC_STATUS,
    
    -- From Databricks Credit Bureau
    d.CREDIT_SCORE,
    d.BUREAU_NAME,
    d.TOTAL_ACCOUNTS,
    d.CREDIT_LIMIT_UTILIZATION,
    
    -- Source indicators
    'Oracle T24' as core_banking_source,
    'MySQL' as digital_source,
    'Databricks' as bureau_source

FROM RAW_ZONE.ORACLE_T24_SRC.T24_CUSTOMER o

LEFT JOIN RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE m
    ON o.CUSTOMER_ID = m.CUSTOMER_ID
    
LEFT JOIN RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT d
    ON o.CUSTOMER_ID = d.CUSTOMER_ID

WHERE o.CUSTOMER_STATUS = 'ACTIVE'
LIMIT 10;
```

---

## 📊 Monitoring Dashboard

### Real-time Source Health:

```sql
-- Create monitoring view
CREATE OR REPLACE VIEW GOVERNANCE.AUDIT.EXTERNAL_SOURCE_HEALTH AS
SELECT 
    CURRENT_TIMESTAMP() as check_time,
    
    -- Oracle T24 Health
    (SELECT COUNT(*) FROM RAW_ZONE.ORACLE_T24_SRC.T24_CUSTOMER) as oracle_customer_count,
    (SELECT MAX(MODIFIED_DATE) FROM RAW_ZONE.ORACLE_T24_SRC.T24_CUSTOMER) as oracle_last_update,
    
    -- MySQL Health  
    (SELECT COUNT(*) FROM RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE) as mysql_customer_count,
    (SELECT MAX(MODIFIED_DATE) FROM RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE) as mysql_last_update,
    
    -- Databricks Health
    (SELECT COUNT(*) FROM RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT) as databricks_report_count,
    (SELECT MAX(MODIFIED_TIMESTAMP) FROM RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT) as databricks_last_update;

-- Query health status
SELECT * FROM GOVERNANCE.AUDIT.EXTERNAL_SOURCE_HEALTH;
```

---

## ✅ Verification Checklist

After deployment, verify all 3 sources are visible:

```sql
-- 1. Check schemas exist
SHOW SCHEMAS IN RAW_ZONE;
-- Expected: ORACLE_T24_SRC, MYSQL_SRC, DATABRICKS_SRC

-- 2. Check table counts
SELECT 
    table_schema,
    COUNT(*) as table_count
FROM CREDIT_DECISIONING_DB.INFORMATION_SCHEMA.TABLES
WHERE table_schema LIKE '%_SRC'
GROUP BY table_schema;
-- Expected: ORACLE_T24_SRC (6), MYSQL_SRC (4), DATABRICKS_SRC (4)

-- 3. Check data is flowing
SELECT 
    'Oracle' as source,
    COUNT(*) as row_count,
    MAX(MODIFIED_DATE) as latest_record
FROM RAW_ZONE.ORACLE_T24_SRC.T24_CUSTOMER

UNION ALL

SELECT 
    'MySQL',
    COUNT(*),
    MAX(MODIFIED_DATE)
FROM RAW_ZONE.MYSQL_SRC.DIGITAL_CUSTOMER_PROFILE

UNION ALL

SELECT 
    'Databricks',
    COUNT(*),
    MAX(MODIFIED_TIMESTAMP)
FROM RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT;

-- 4. Check connector status
SELECT * FROM GOVERNANCE.AUDIT.OPENFLOW_CONNECTOR_STATUS;
SELECT * FROM GOVERNANCE.AUDIT.POLARIS_SYNC_STATUS;
```

---

## 🎓 Summary

**Yes, all 3 external data sources will be clearly visible in Snowflake!**

✅ **Organized by Source:** Each source has its own schema (ORACLE_T24_SRC, MYSQL_SRC, DATABRICKS_SRC)

✅ **Clear Naming:** Schema and table names indicate the source system

✅ **Metadata Tracked:** Connection type, sync status, last update time all visible

✅ **Lineage Visible:** Snowflake tracks which downstream tables use which source

✅ **Monitoring Built-in:** Views show real-time health of all connections

✅ **User-Friendly:** Both technical (SQL) and business users (Streamlit) can see sources

The catalog structure makes it **crystal clear** where data comes from, supports **governance and compliance**, and enables **cross-source analytics**! 🎯
