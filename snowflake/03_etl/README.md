# ETL Pipelines - Dynamic Tables

This directory contains SQL scripts to create Dynamic Tables for data transformation and feature engineering.

## Execution Order

Run these scripts in order:

1. **`00_create_schemas.sql`** - Creates Analytics Zone schemas
2. **`01_feature_engineering.sql`** - Creates ML feature store (50+ features)
3. **`02_customer_360.sql`** - Creates unified Customer 360 views
4. **`03_portfolio_analytics.sql`** - Creates portfolio risk analytics

## What Are Dynamic Tables?

Dynamic Tables are Snowflake's declarative data transformation feature. They:
- Automatically refresh based on `TARGET_LAG` (e.g., every 5-15 minutes)
- Track dependencies and refresh in correct order
- Provide incremental updates for efficiency
- Eliminate the need for manual ETL orchestration

## Feature Engineering

**File:** `01_feature_engineering.sql`

Creates **50+ ML features** including:
- Demographic features (age, gender, marital status)
- Financial features (balances, loans, DTI ratio)
- Transaction features (3M, 6M, 12M windows)
- Credit bureau features (scores, tradelines, inquiries)
- Digital behavior features (logins, sessions, engagement)
- Risk indicators

**Output Table:** `ANALYTICS_ZONE.FEATURE_STORE.CREDIT_SCORING_FEATURES`

**Refresh:** Every 15 minutes

## Customer 360

**File:** `02_customer_360.sql`

Creates unified customer views combining:
- Core banking data (T24)
- Digital banking data
- Credit bureau data
- Financial summaries

**Output Tables:**
- `ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED`
- `ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_FINANCIAL_SUMMARY`

**Refresh:** Every 5 minutes

## Portfolio Analytics

**File:** `03_portfolio_analytics.sql`

Creates portfolio-level metrics:
- Portfolio summary (totals, averages, rates)
- Delinquency cohorts (by days past due)
- Risk segments (low/medium/high risk)
- Early warning alerts (at-risk customers)

**Output Tables:**
- `ANALYTICS_ZONE.RISK_ANALYTICS.PORTFOLIO_SUMMARY`
- `ANALYTICS_ZONE.RISK_ANALYTICS.DELINQUENCY_COHORTS`
- `ANALYTICS_ZONE.RISK_ANALYTICS.RISK_SEGMENTS`
- `ANALYTICS_ZONE.RISK_ANALYTICS.EARLY_WARNING_ALERTS`

**Refresh:** Every 15 minutes

## How to Run

### Option 1: Snowflake UI (Recommended)

1. Open Snowflake Web UI
2. Open SQL Worksheet
3. Copy and paste each script
4. Run each script in order
5. Monitor refresh status in Snowsight

### Option 2: SnowSQL CLI

```bash
snowsql -a <account> -u <user> -d CREDIT_DECISIONING_DB -w COMPUTE_WH \
  -f 00_create_schemas.sql

snowsql -a <account> -u <user> -d CREDIT_DECISIONING_DB -w COMPUTE_WH \
  -f 01_feature_engineering.sql

# ... repeat for each file
```

## Verification

After running all scripts, verify with:

```sql
-- Check feature store
SELECT COUNT(*) FROM ANALYTICS_ZONE.FEATURE_STORE.CREDIT_SCORING_FEATURES;
-- Should match customer count (~3,000)

-- Check Customer 360
SELECT COUNT(*) FROM ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED;
-- Should match customer count

-- Check portfolio summary
SELECT * FROM ANALYTICS_ZONE.RISK_ANALYTICS.PORTFOLIO_SUMMARY;
-- Should have 1 row with portfolio totals
```

## Monitoring

Monitor Dynamic Table refresh status:

```sql
-- View all Dynamic Tables
SHOW DYNAMIC TABLES IN SCHEMA ANALYTICS_ZONE.FEATURE_STORE;
SHOW DYNAMIC TABLES IN SCHEMA ANALYTICS_ZONE.CUSTOMER_360;
SHOW DYNAMIC TABLES IN SCHEMA ANALYTICS_ZONE.RISK_ANALYTICS;

-- Check refresh history
SELECT * FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY())
WHERE TABLE_SCHEMA LIKE 'ANALYTICS_ZONE%'
ORDER BY REFRESH_START_TIME DESC;
```

## Troubleshooting

### Dynamic Table Not Refreshing

1. Check warehouse is running: `ALTER WAREHOUSE COMPUTE_WH RESUME;`
2. Check TARGET_LAG is reasonable (not too aggressive)
3. Check for errors: `SELECT * FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY()) WHERE STATE = 'FAILED';`

### Missing Data

1. Verify source tables have data
2. Check joins are correct (LEFT JOIN vs INNER JOIN)
3. Verify date filters are correct

### Performance Issues

1. Increase warehouse size if needed
2. Adjust TARGET_LAG to refresh less frequently
3. Check query performance with EXPLAIN

## Next Steps

After ETL pipelines are running:

1. **Phase 2:** Train ML model using feature store
2. **Phase 3:** Build Streamlit dashboards using Customer 360 and Portfolio Analytics
3. **Phase 4:** Set up GenAI features

See `NEXT_STEPS_ROADMAP.md` for full implementation plan.
