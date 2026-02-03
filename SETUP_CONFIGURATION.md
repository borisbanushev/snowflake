# 🔧 Setup Configuration Guide

This guide lists all the information needed to automate data loading to Oracle Cloud and Databricks.

---

## 📋 Prerequisites Checklist

### ✅ What You Need to Provide

I'll create automated scripts once you provide these details. You can store them in a `.env` file (which is gitignored for security).

---

## 🔴 Oracle Cloud Database (Autonomous Database or DB System)

### Connection Information Needed:

```bash
# Oracle Cloud Database Details
ORACLE_CLOUD_HOST="your-db.adb.region.oraclecloud.com"
ORACLE_CLOUD_PORT="1522"  # Usually 1522 for Autonomous DB, 1521 for DB System
ORACLE_CLOUD_SERVICE_NAME="your_service_high"  # e.g., mydb_high, mydb_medium, mydb_low
ORACLE_CLOUD_USERNAME="t24user"  # Or your admin user
ORACLE_CLOUD_PASSWORD="YourSecurePassword123!"

# For Autonomous Database with Wallet (mTLS)
ORACLE_CLOUD_WALLET_LOCATION="/path/to/Wallet_YourDB.zip"
ORACLE_CLOUD_WALLET_PASSWORD="WalletPassword123"

# Or for TLS without wallet
ORACLE_CLOUD_USE_WALLET="false"  # Set to true if using wallet
```

### How to Get These:

1. **Login to Oracle Cloud Console**: https://cloud.oracle.com
2. **Navigate to**: Autonomous Database or Bare Metal/VM/Exadata DB Systems
3. **Select your database**
4. **Connection Strings**:
   - Click "DB Connection"
   - Copy the connection string (TNS format or Easy Connect)
   - Example: `(description=(address=(protocol=tcps)(port=1522)(host=abc.oraclecloud.com))(connect_data=(service_name=mydb_high)))`
5. **Wallet** (for Autonomous DB):
   - Click "DB Connection" → "Download Wallet"
   - Set a wallet password
   - Save the ZIP file

### What Database Service Do You Have?

- [ ] **Autonomous Database** (ATP/ADW) - Requires wallet or TLS
- [ ] **DB System** (Bare Metal/VM/Exadata) - Standard connection
- [ ] **Oracle Base Database Service** - Standard connection
- [ ] **Still need to create one** - I can provide Terraform/scripts

---

## 🟠 Databricks

### Connection Information Needed:

```bash
# Databricks Workspace Details
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
DATABRICKS_TOKEN="dapi1234567890abcdef..."  # Personal Access Token
DATABRICKS_WORKSPACE_ID="1234567890123456"

# Databricks Cluster (for data loading)
DATABRICKS_CLUSTER_ID="0123-456789-abc123"  # Existing cluster
# OR - I can create a job cluster automatically
DATABRICKS_CLUSTER_NAME="snowflake-data-loader"

# Unity Catalog (for Polaris integration)
DATABRICKS_CATALOG="credit_bureau"
DATABRICKS_SCHEMA="default"
DATABRICKS_METASTORE_ID="12345678-1234-1234-1234-123456789012"

# Storage Account (AWS S3, Azure ADLS, or GCS)
DATABRICKS_STORAGE_TYPE="s3"  # or "azure", "gcs"

# If AWS S3:
DATABRICKS_S3_BUCKET="s3://your-datalake-bucket/credit-bureau/"
DATABRICKS_AWS_REGION="ap-southeast-1"  # Singapore
DATABRICKS_AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
DATABRICKS_AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# If Azure ADLS:
DATABRICKS_AZURE_STORAGE_ACCOUNT="yourstorageaccount"
DATABRICKS_AZURE_CONTAINER="credit-bureau"
DATABRICKS_AZURE_SAS_TOKEN="?sv=2021-06-08&ss=bfqt&srt=sco&sp=rwdlacup..."

# If GCS:
DATABRICKS_GCS_BUCKET="gs://your-datalake-bucket/credit-bureau/"
DATABRICKS_GCS_SERVICE_ACCOUNT_KEY="/path/to/service-account-key.json"
```

### How to Get These:

#### 1. **Databricks Workspace URL**:
   - Login to your Databricks workspace
   - Copy URL from browser: `https://your-workspace.cloud.databricks.com`

#### 2. **Personal Access Token**:
   - In Databricks: User Settings → Developer → Access tokens
   - Click "Generate new token"
   - Lifetime: 90 days (or longer)
   - Copy the token (starts with `dapi...`)

#### 3. **Cluster ID** (if using existing):
   - Compute → Select cluster → URL has cluster ID
   - Or: Compute → Cluster → JSON tab → Copy cluster_id

#### 4. **Unity Catalog & Metastore**:
   - Data → Click on catalog name
   - Settings will show metastore ID
   - Or: SQL Editor → `SELECT current_metastore()`

#### 5. **Storage Details**:
   - This is where your Iceberg tables will be stored
   - AWS: S3 bucket name and region
   - Azure: Storage account and container
   - GCS: Bucket name

### What Databricks Environment Do You Have?

- [ ] **AWS Databricks** - Need S3 details
- [ ] **Azure Databricks** - Need ADLS details  
- [ ] **GCP Databricks** - Need GCS details
- [ ] **Unity Catalog enabled** - Yes/No
- [ ] **Still need to create workspace** - I can provide Terraform

---

## 🔵 Snowflake

### Connection Information Needed:

```bash
# Snowflake Account Details
SNOWFLAKE_ACCOUNT="xy12345.ap-southeast-1.aws"  # Your account identifier
SNOWFLAKE_USER="ACCOUNTADMIN"  # Or service account
SNOWFLAKE_PASSWORD="YourSecurePassword!"
SNOWFLAKE_ROLE="ACCOUNTADMIN"
SNOWFLAKE_WAREHOUSE="ETL_WH"
SNOWFLAKE_DATABASE="CREDIT_DECISIONING_DB"

# For Key-Pair Authentication (Recommended for automation)
SNOWFLAKE_PRIVATE_KEY_PATH="/path/to/rsa_key.p8"
SNOWFLAKE_PRIVATE_KEY_PASSPHRASE="KeyPassword123"

# AWS IAM Role (for Openflow/External Access)
SNOWFLAKE_AWS_IAM_ROLE="arn:aws:iam::123456789012:role/snowflake-access-role"
SNOWFLAKE_AWS_EXTERNAL_ID="ABC12345_SFCRole=1234567890"
```

### How to Get These:

1. **Account Identifier**:
   - Login to Snowflake
   - Look at URL: `https://app.snowflake.com/xy12345/`
   - Or: `SELECT CURRENT_ACCOUNT()`

2. **Generate Key-Pair** (recommended):
   ```bash
   # I can generate this for you
   openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8
   openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
   ```

3. **IAM Role** (for Openflow):
   - Created when you set up External Access
   - Snowflake provides the trust policy

---

## 🟢 What I'll Create for You

Once you provide the above, I'll generate:

### 1. **Environment Configuration File** (`.env`)
```bash
# Secure .env file with all your credentials
# This file will be .gitignored
```

### 2. **Oracle Cloud Data Loader** (`load_to_oracle_cloud.py`)
- Connects to Oracle Cloud (with or without wallet)
- Generates 100K customers
- Loads all T24 tables
- Supports both Autonomous DB and DB System

### 3. **Databricks Data Loader** (`load_to_databricks.py`)
- Creates Iceberg tables in Unity Catalog
- Generates credit bureau data
- Writes to S3/ADLS/GCS
- Registers tables with Polaris catalog

### 4. **Snowflake Connector Configuration** (Updated SQL)
- `oracle_openflow_cloud.sql` - Openflow to Oracle Cloud
- `databricks_polaris_config.sql` - Polaris with your credentials
- Connection monitoring queries

### 5. **Automated Setup Script** (`setup_cloud.sh`)
```bash
#!/bin/bash
# One command to:
# - Validate all credentials
# - Load data to Oracle Cloud
# - Load data to Databricks
# - Configure Snowflake connectors
# - Verify data flow
```

### 6. **Validation & Monitoring**
- Connection test scripts
- Data quality checks
- Row count verification
- CDC lag monitoring

---

## 📝 Quick Start Template

Save this as `.env` in your project root and fill in your details:

```bash
# ============================================
# ORACLE CLOUD
# ============================================
ORACLE_CLOUD_HOST=""
ORACLE_CLOUD_PORT="1522"
ORACLE_CLOUD_SERVICE_NAME=""
ORACLE_CLOUD_USERNAME="t24user"
ORACLE_CLOUD_PASSWORD=""
ORACLE_CLOUD_USE_WALLET="false"
ORACLE_CLOUD_WALLET_LOCATION=""
ORACLE_CLOUD_WALLET_PASSWORD=""

# ============================================
# DATABRICKS
# ============================================
DATABRICKS_HOST=""
DATABRICKS_TOKEN=""
DATABRICKS_CLUSTER_ID=""
DATABRICKS_CATALOG="credit_bureau"
DATABRICKS_SCHEMA="default"

# Storage
DATABRICKS_STORAGE_TYPE="s3"
DATABRICKS_S3_BUCKET=""
DATABRICKS_AWS_REGION="ap-southeast-1"
DATABRICKS_AWS_ACCESS_KEY_ID=""
DATABRICKS_AWS_SECRET_ACCESS_KEY=""

# ============================================
# SNOWFLAKE
# ============================================
SNOWFLAKE_ACCOUNT=""
SNOWFLAKE_USER=""
SNOWFLAKE_PASSWORD=""
SNOWFLAKE_ROLE="ACCOUNTADMIN"
SNOWFLAKE_WAREHOUSE="ETL_WH"
SNOWFLAKE_DATABASE="CREDIT_DECISIONING_DB"
```

---

## 🚀 Next Steps

### Option 1: You Provide Everything
1. Fill in the `.env` template above
2. Send me the details (or save as `.env` file)
3. I'll generate all automation scripts
4. You run one command: `./setup_cloud.sh`

### Option 2: Step-by-Step
1. Start with **Oracle Cloud** only
2. Then add **Databricks**
3. Finally connect **Snowflake**

### Option 3: I Help You Create Infrastructure
If you don't have Oracle Cloud or Databricks yet, I can create:
- Terraform scripts to provision everything
- ARM/CloudFormation templates
- Setup guides with screenshots

---

## ⚠️ Security Best Practices

1. **Never commit `.env` to git** - Already in .gitignore
2. **Use key-pair auth for Snowflake** - More secure than passwords
3. **Rotate credentials regularly** - Especially access tokens
4. **Use IAM roles where possible** - Instead of access keys
5. **Enable MFA** - On all cloud accounts
6. **Audit access** - Monitor connection logs

---

## 📞 What I Need From You Now

Please provide:

1. **Which services do you already have?**
   - [ ] Oracle Cloud Database (Type: __________)
   - [ ] Databricks Workspace (Cloud: __________)
   - [ ] Snowflake Account (Region: __________)

2. **What's your priority?**
   - [ ] Get Oracle Cloud working first
   - [ ] Get Databricks working first
   - [ ] Both at the same time
   - [ ] Help me set up the infrastructure

3. **Credentials sharing method:**
   - [ ] I'll create a `.env` file and paste contents here
   - [ ] I'll provide one service at a time
   - [ ] I need help creating accounts first

Just let me know what you have and what you need, and I'll create the exact automation scripts for your setup! 🚀
