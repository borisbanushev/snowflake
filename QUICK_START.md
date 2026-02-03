# 🚀 Quick Start Guide

## For Users with Oracle Cloud + Databricks Already Provisioned

### Prerequisites
- ✅ Oracle Cloud Database (Autonomous or DB System) 
- ✅ Databricks Workspace with Unity Catalog
- ✅ Snowflake Account (Enterprise on AWS Singapore)

---

## Step 1: Configure Credentials (5 minutes)

Create `.env` file from template:

```bash
cd /Users/boris/Desktop/snowflake
cp .env.example .env
nano .env  # or use VS Code, vim, etc.
```

### Fill in these values:

```bash
# ============================================
# ORACLE CLOUD
# ============================================
ORACLE_CLOUD_HOST="abc123.adb.ap-southeast-1.oraclecloud.com"
ORACLE_CLOUD_PORT="1522"
ORACLE_CLOUD_SERVICE="mydb_high"  # or mydb_medium, mydb_low
ORACLE_CLOUD_USERNAME="ADMIN"
ORACLE_CLOUD_PASSWORD="YourPassword123!"

# If using wallet (Autonomous DB):
ORACLE_USE_WALLET="false"  # Set to "true" if using wallet
ORACLE_WALLET_LOCATION="/path/to/Wallet_YourDB"
ORACLE_WALLET_PASSWORD="WalletPass123"

# ============================================
# DATABRICKS (Managed/Serverless Tables)
# ============================================
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
DATABRICKS_TOKEN="dapi1234567890abcdef"  # From User Settings → Developer → Access tokens
DATABRICKS_CATALOG="credit_bureau_data"
DATABRICKS_SCHEMA="credit_bureau"

# ============================================
# SNOWFLAKE
# ============================================
SNOWFLAKE_ACCOUNT="xy12345.ap-southeast-1.aws"
SNOWFLAKE_USER="ACCOUNTADMIN"
SNOWFLAKE_PASSWORD="YourPassword!"
```

---

## Step 2: Load Data to Cloud (10-15 minutes)

Run the automated loader:

```bash
cd /Users/boris/Desktop/snowflake
./scripts/load_cloud_data.sh
```

This will:
1. Install Python dependencies
2. Connect to Oracle Cloud
3. Create T24 tables and load 100K customers
4. Connect to Databricks
5. Create Unity Catalog + managed tables
6. Load credit bureau data

**Expected Output:**
```
✅ Connected to Oracle Cloud
✅ Created T24_CUSTOMER
✅ Created T24_ACCOUNT
✅ Created T24_LOAN
📥 Inserted 100,000 customers
📥 Inserted 180,000 accounts
📥 Inserted 35,000 loans

✅ Connected to Databricks
✅ Catalog: credit_bureau_data
✅ Schema: credit_bureau
✅ Created CREDIT_BUREAU_REPORT (managed table)
✅ Created INCOME_VERIFICATION (managed table)
📥 Loaded 100,000 credit reports
📥 Loaded 100,000 income verifications

🎉 All data loaded successfully!
```

---

## Step 3: Configure Snowflake Connectors (5 minutes)

### A. Update Connection Strings

Edit these files with your actual values:

**1. Oracle Openflow Connector:**
```bash
nano snowflake/01_connectors/oracle_openflow.sql
```

Update lines:
```sql
CONNECTION_STRING = 'jdbc:oracle:thin:@abc123.adb.region.oraclecloud.com:1522/mydb_high'
USERNAME = 'ADMIN'
PASSWORD = SECRET 'GOVERNANCE.POLICIES.oracle_cloud_password'
```

**2. Databricks Polaris Connector:**
```bash
nano snowflake/01_connectors/databricks_polaris.sql
```

Update lines:
```sql
CATALOG_URI = 'https://your-workspace.cloud.databricks.com/api/2.1/unity-catalog'
CATALOG_NAME = 'credit_bureau_data'
OAUTH_CLIENT_ID = 'your-databricks-token'
```

### B. Run Connectors in Snowflake

```sql
-- In Snowflake web UI or SnowSQL:

-- 1. Setup
USE ROLE ACCOUNTADMIN;
!source snowflake/00_setup/01_create_database.sql
!source snowflake/00_setup/02_create_schemas.sql
!source snowflake/00_setup/03_create_warehouses.sql
!source snowflake/00_setup/04_create_roles.sql

-- 2. Connectors
!source snowflake/01_connectors/oracle_openflow.sql
!source snowflake/01_connectors/databricks_polaris.sql

-- 3. Other components
!source snowflake/05_unistore/hybrid_tables.sql
!source snowflake/08_governance/01_tags.sql
!source snowflake/08_governance/02_masking_policies.sql
```

---

## Step 4: Verify Data Flow (2 minutes)

Run these queries in Snowflake:

```sql
-- Check Oracle CDC data
SELECT COUNT(*) FROM RAW_ZONE.ORACLE_T24_SRC.T24_CUSTOMER;
-- Expected: 100,000

SELECT COUNT(*) FROM RAW_ZONE.ORACLE_T24_SRC.T24_ACCOUNT;
-- Expected: 180,000

SELECT COUNT(*) FROM RAW_ZONE.ORACLE_T24_SRC.T24_LOAN;
-- Expected: 35,000

-- Check Databricks data via Polaris
SELECT COUNT(*) FROM RAW_ZONE.DATABRICKS_SRC.CREDIT_BUREAU_REPORT;
-- Expected: 100,000

SELECT COUNT(*) FROM RAW_ZONE.DATABRICKS_SRC.INCOME_VERIFICATION;
-- Expected: 100,000

-- Monitor connector health
SELECT * FROM GOVERNANCE.AUDIT.OPENFLOW_CONNECTOR_STATUS;
SELECT * FROM GOVERNANCE.AUDIT.POLARIS_SYNC_STATUS;
```

---

## Step 5: Launch Streamlit App (2 minutes)

```bash
cd streamlit
pip install -r requirements.txt
streamlit run main.py
```

Open browser to: http://localhost:8501

---

## 🎯 Quick Reference

### Where to Get Credentials:

**Oracle Cloud:**
- Console → Database → Your DB → Connection Strings
- Download wallet: DB Connection → Download Wallet

**Databricks:**
- Workspace URL: Your browser address bar
- Token: User Settings → Developer → Access tokens → Generate new token
- Catalog: Data → Browse → Click catalog name

**Snowflake:**
- Account: From URL (https://app.snowflake.com/ACCOUNT/)
- Or run: `SELECT CURRENT_ACCOUNT()`

---

## 🆘 Troubleshooting

### Oracle Cloud Connection Failed
- Check IP is whitelisted in Access Control List
- For Autonomous DB: Verify wallet location and password
- Test: `tnsping mydb_high` (if Oracle Client installed)

### Databricks Connection Failed
- Verify token hasn't expired
- Check workspace URL (no trailing slash)
- Ensure Unity Catalog is enabled

### Snowflake Connector Issues
- Verify external access is configured
- Check network rules allow Oracle/Databricks IPs
- Review connector logs: `TABLE(INFORMATION_SCHEMA.CONNECTOR_HISTORY())`

---

## 📚 What's Next?

1. **View Data Flow**: Check `TECHNICAL_PRESENTATION.md` for architecture
2. **Customize**: Edit table schemas in loader scripts
3. **Scale**: Increase `NUM_CUSTOMERS` in `.env`
4. **Monitor**: Set up alerts for connector lag
5. **Present**: Use `PRESENTATION_SLIDES.md` for demos

---

## ⏱️ Total Time: ~25-30 minutes

- Configure: 5 min
- Load data: 10-15 min
- Setup Snowflake: 5 min
- Verify: 2 min
- Launch app: 2 min

**Result:** Fully functional Credit Decisioning Platform with real-time data from Oracle Cloud and Databricks! 🎉
