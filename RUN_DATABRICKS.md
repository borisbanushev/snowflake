# 🚀 Load Data to Databricks

## Quick Run (1 Command)

Your Databricks credentials are already configured. Just run:

```bash
cd /Users/boris/Desktop/snowflake
./scripts/load_databricks_only.sh
```

---

## What This Does

1. **Connects to your Databricks workspace:**
   - Workspace: `https://dbc-6730e836-5587.cloud.databricks.com`
   - Catalog: `sowcatalog`
   - Schema: `credit_bureau`

2. **Creates 4 managed Delta tables:**
   - `CREDIT_BUREAU_REPORT` - Credit scores and bureau data
   - `INCOME_VERIFICATION` - Employment and income validation
   - `ALTERNATIVE_DATA` - Non-traditional credit signals
   - `FRAUD_INDICATORS` - Risk and fraud detection scores

3. **Loads realistic data:**
   - 100,000 credit bureau reports
   - 100,000 income verifications
   - Matching customer IDs (CUS-000000 to CUS-099999)
   - Realistic distributions and correlations

---

## Expected Output

```
======================================================================
Databricks Credit Bureau Data Loader
======================================================================

✅ Found .env configuration

[1/3] Installing Python dependencies...
✅ Dependencies installed

[2/3] Loading data to Databricks Unity Catalog...
Workspace: https://dbc-6730e836-5587.cloud.databricks.com
Catalog: sowcatalog
Schema: credit_bureau

======================================================================
Databricks Credit Bureau Data Loader (Managed Tables)
======================================================================
Catalog: sowcatalog
Schema: credit_bureau
Storage: Databricks-managed (serverless)
======================================================================
✅ Connected to Databricks successfully!
Using warehouse: Starter Warehouse

📦 Setting up Unity Catalog...
✅ Catalog: sowcatalog
✅ Schema: credit_bureau
📁 Storage: Databricks-managed (serverless)

📊 Creating managed Delta tables...

✅ Created CREDIT_BUREAU_REPORT (managed table)
✅ Created INCOME_VERIFICATION (managed table)
✅ Created ALTERNATIVE_DATA (managed table)
✅ Created FRAUD_INDICATORS (managed table)

🎲 Generating credit bureau data...

👥 Generating 100,000 credit bureau reports...
100%|████████████████████████████████████| 100000/100000

💰 Generating 100,000 income verification records...
100%|████████████████████████████████████| 100000/100000

📤 Loading data to Databricks managed tables...

📥 Loading 100,000 rows to CREDIT_BUREAU_REPORT...
100%|████████████████████████████████████| 100/100 batches

📥 Loading 100,000 rows to INCOME_VERIFICATION...
100%|████████████████████████████████████| 100/100 batches

======================================================================
🎉 Databricks Data Load Complete!
======================================================================
Credit Reports:      100,000
Income Verification: 100,000

📁 Storage: Databricks-managed (serverless)

✅ Databricks is ready for Snowflake Polaris integration!
   Catalog: sowcatalog
   Schema: credit_bureau
   Format: Delta Lake (managed tables)

💡 Next: Configure Snowflake to read from Unity Catalog via Polaris
```

---

## Verify in Databricks

### Option 1: Databricks SQL Editor

Go to: https://dbc-6730e836-5587.cloud.databricks.com/sql/editor

Run these queries:

```sql
-- Check catalog and schema
SHOW CATALOGS;
SHOW SCHEMAS IN sowcatalog;

-- Check tables
SHOW TABLES IN sowcatalog.credit_bureau;

-- Verify data
SELECT COUNT(*) FROM sowcatalog.credit_bureau.CREDIT_BUREAU_REPORT;
-- Expected: 100,000

SELECT COUNT(*) FROM sowcatalog.credit_bureau.INCOME_VERIFICATION;
-- Expected: 100,000

-- Sample data
SELECT * FROM sowcatalog.credit_bureau.CREDIT_BUREAU_REPORT LIMIT 10;

-- Check credit score distribution
SELECT 
    CASE 
        WHEN CREDIT_SCORE >= 800 THEN '800+'
        WHEN CREDIT_SCORE >= 740 THEN '740-799'
        WHEN CREDIT_SCORE >= 670 THEN '670-739'
        WHEN CREDIT_SCORE >= 580 THEN '580-669'
        ELSE 'Below 580'
    END AS score_range,
    COUNT(*) as customer_count,
    ROUND(AVG(CREDIT_SCORE), 0) as avg_score
FROM sowcatalog.credit_bureau.CREDIT_BUREAU_REPORT
GROUP BY score_range
ORDER BY score_range DESC;

-- Check income verification
SELECT 
    VERIFICATION_TYPE,
    COUNT(*) as count,
    ROUND(AVG(ANNUAL_INCOME), 0) as avg_income
FROM sowcatalog.credit_bureau.INCOME_VERIFICATION
GROUP BY VERIFICATION_TYPE;
```

### Option 2: Databricks Data Explorer

1. Go to: https://dbc-6730e836-5587.cloud.databricks.com/explore/data
2. Click on `sowcatalog`
3. Click on `credit_bureau` schema
4. Browse tables:
   - CREDIT_BUREAU_REPORT
   - INCOME_VERIFICATION
   - ALTERNATIVE_DATA
   - FRAUD_INDICATORS

---

## What's Generated

### CREDIT_BUREAU_REPORT (100K rows)
- Realistic credit scores (300-850) with beta distribution
- Account history and delinquencies
- Public records, bankruptcies, collections
- Credit utilization and limits
- Inquiry counts
- Partitioned by REPORT_DATE for performance

### INCOME_VERIFICATION (100K rows)
- Annual income ($30K - $500K)
- Employment status and sector
- Job titles and employer names
- Verification methods and status
- Income stability scores
- Partitioned by VERIFICATION_DATE

### ALTERNATIVE_DATA (Empty for now)
- Will be populated with gig economy income
- Digital footprint scores
- E-commerce history
- Social media indicators

### FRAUD_INDICATORS (Empty for now)
- Identity verification scores
- Watchlist and sanctions checks
- Behavioral anomalies
- Device and IP risk signals

---

## Troubleshooting

### "Catalog not found"
```bash
# The catalog 'sowcatalog' must exist in your workspace
# Create it if needed:
# In Databricks SQL: CREATE CATALOG sowcatalog;
```

### "Permission denied"
```bash
# Your token needs Unity Catalog permissions
# Generate a new token with:
# - Workspace access
# - Unity Catalog access (CREATE, USE CATALOG, USE SCHEMA)
```

### "Connection timeout"
```bash
# Check workspace URL is correct
# Verify token hasn't expired (generate new one if needed)
```

### "Warehouse not found"
```bash
# Script will auto-create a SQL warehouse if none exist
# Or specify existing one: DATABRICKS_WAREHOUSE_ID="abc123" in .env
```

---

## Re-run / Reset

To reload data:

```bash
# Drop and recreate tables
cd /Users/boris/Desktop/snowflake
./scripts/load_databricks_only.sh

# Or manually drop in Databricks SQL:
DROP TABLE IF EXISTS sowcatalog.credit_bureau.CREDIT_BUREAU_REPORT;
DROP TABLE IF EXISTS sowcatalog.credit_bureau.INCOME_VERIFICATION;
DROP TABLE IF EXISTS sowcatalog.credit_bureau.ALTERNATIVE_DATA;
DROP TABLE IF EXISTS sowcatalog.credit_bureau.FRAUD_INDICATORS;

# Then re-run the script
```

---

## Next: Connect to Snowflake

Once data is loaded, configure Snowflake to access it:

1. Update `snowflake/01_connectors/databricks_polaris.sql` with:
   - Your Databricks workspace URL
   - Unity Catalog name: `sowcatalog`
   - Schema name: `credit_bureau`

2. Run in Snowflake to create external tables

3. Query from Snowflake:
   ```sql
   SELECT COUNT(*) FROM RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT;
   ```

---

## Estimated Time: 5-10 minutes

- Install dependencies: 30 seconds
- Create tables: 10 seconds
- Generate data: 2-3 minutes
- Load data: 2-5 minutes

**Total:** Less than 10 minutes for 100K records! 🚀
