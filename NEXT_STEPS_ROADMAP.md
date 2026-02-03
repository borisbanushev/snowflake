# 🚀 Next Steps Roadmap - Credit Decisioning Platform

**Status:** ✅ Data Loaded | 🚧 Next: ETL → ML → Dashboards → GenAI  
**Last Updated:** February 3, 2026

---

## 📊 Current Status

### ✅ Completed
- [x] **Data Generation**: 19 CSV files with 170,341 records
- [x] **Schema Creation**: 4 schemas (DIGITAL_BANKING, CORE_BANKING, CREDIT_BUREAU, REFERENCE_DATA)
- [x] **Table Creation**: 19 tables across all schemas
- [x] **Data Load**: All CSV files uploaded and loaded into Snowflake
- [x] **Streamlit App**: Basic structure with AI Credit Agent page

### 🚧 To Build Next
1. **ETL Pipelines** (Dynamic Tables)
2. **Machine Learning Models** (Snowpark ML)
3. **Dashboards** (Streamlit pages)
4. **GenAI Features** (Cortex Search, Agents, Analyst)

---

## 🎯 Phase 1: ETL Pipelines (Dynamic Tables)

### Purpose
Create declarative data pipelines to transform raw data into analytics-ready formats.

### Files to Create

#### 1.1 Feature Engineering Pipeline
**File:** `snowflake/03_etl/01_feature_engineering.sql`

**What it does:**
- Creates feature store with 50+ engineered features
- Aggregates transaction data (3M, 6M, 12M windows)
- Calculates financial ratios (DTI, utilization, etc.)
- Creates behavioral features (transaction velocity, payment patterns)

**Tables to create:**
- `ANALYTICS_ZONE.FEATURE_STORE.CREDIT_SCORING_FEATURES`
- `ANALYTICS_ZONE.FEATURE_STORE.CUSTOMER_BEHAVIOR_FEATURES`
- `ANALYTICS_ZONE.FEATURE_STORE.FINANCIAL_AGGREGATES`

**Key Features:**
```sql
-- Example features to engineer:
- F_AGE, F_ANNUAL_INCOME, F_DEBT_TO_INCOME
- F_CREDIT_SCORE, F_CREDIT_UTILIZATION
- F_AVG_BALANCE_3M, F_TXN_COUNT_3M, F_TXN_VELOCITY_6M
- F_PAYMENT_HISTORY_SCORE, F_DELINQUENCY_COUNT_12M
- F_DIGITAL_ENGAGEMENT_SCORE, F_LOGIN_FREQUENCY_30D
- F_RELATIONSHIP_MONTHS, F_ACCOUNT_AGE
```

#### 1.2 Customer 360 View
**File:** `snowflake/03_etl/02_customer_360.sql`

**What it does:**
- Unifies customer data from all sources (T24, Digital, Credit Bureau)
- Creates single source of truth for customer profiles
- Includes financial summary, digital behavior, risk profile

**Tables to create:**
- `ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_360_UNIFIED`
- `ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_FINANCIAL_SUMMARY`
- `ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_DIGITAL_BEHAVIOR`
- `ANALYTICS_ZONE.CUSTOMER_360.CUSTOMER_RISK_PROFILE`

#### 1.3 Portfolio Analytics
**File:** `snowflake/03_etl/03_portfolio_analytics.sql`

**What it does:**
- Creates portfolio-level aggregations
- Delinquency cohorts and risk segments
- Early warning indicators

**Tables to create:**
- `ANALYTICS_ZONE.RISK_ANALYTICS.PORTFOLIO_SUMMARY`
- `ANALYTICS_ZONE.RISK_ANALYTICS.DELINQUENCY_COHORTS`
- `ANALYTICS_ZONE.RISK_ANALYTICS.RISK_SEGMENTS`
- `ANALYTICS_ZONE.RISK_ANALYTICS.EARLY_WARNING_ALERTS`

### Implementation Steps

1. **Create ETL schemas:**
   ```sql
   CREATE SCHEMA IF NOT EXISTS ANALYTICS_ZONE.FEATURE_STORE;
   CREATE SCHEMA IF NOT EXISTS ANALYTICS_ZONE.CUSTOMER_360;
   CREATE SCHEMA IF NOT EXISTS ANALYTICS_ZONE.RISK_ANALYTICS;
   ```

2. **Create Dynamic Tables** (auto-refresh every 5-15 minutes)
   ```sql
   CREATE OR REPLACE DYNAMIC TABLE ANALYTICS_ZONE.FEATURE_STORE.CREDIT_SCORING_FEATURES
     TARGET_LAG = '15 minutes'
     WAREHOUSE = ETL_WH
   AS
   SELECT 
       c.CUSTOMER_ID,
       -- Feature engineering SQL here
   FROM CORE_BANKING.T24_CUSTOMER c
   -- Joins and aggregations
   ```

3. **Validate data quality:**
   ```sql
   SELECT COUNT(*) FROM ANALYTICS_ZONE.FEATURE_STORE.CREDIT_SCORING_FEATURES;
   -- Should match customer count
   ```

**Estimated Time:** 4-6 hours  
**Priority:** 🔴 High (needed for ML training)

---

## 🤖 Phase 2: Machine Learning Models

### Purpose
Train XGBoost credit scoring model and deploy for real-time inference.

### Files to Create

#### 2.1 Model Training Notebook
**File:** `snowflake/04_ml/01_train_credit_model.ipynb` (Snowflake Notebook)

**What it does:**
- Loads feature store data
- Trains XGBoost classifier (10-band classification)
- Evaluates model performance
- Registers model in ML Registry

**Key Steps:**
```python
from snowflake.ml.modeling.xgboost import XGBClassifier
from snowflake.ml.registry import Registry

# Load training data
training_df = session.table("ANALYTICS_ZONE.FEATURE_STORE.CREDIT_SCORING_FEATURES")

# Train model
model = XGBClassifier(
    input_cols=ALL_FEATURES,
    label_cols=['TARGET_CREDIT_SCORE_BAND'],
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1
)
model.fit(training_df)

# Register model
registry = Registry(session, database_name="CREDIT_DECISIONING_DB", schema_name="ML_ZONE.MODELS")
model_version = registry.log_model(
    model_name="CREDIT_SCORING_XGBOOST",
    version_name="v1",
    model=model
)
```

#### 2.2 Inference UDF
**File:** `snowflake/04_ml/02_create_inference_udf.sql`

**What it does:**
- Creates SQL UDF for real-time credit scoring
- Loads model from registry
- Returns credit score, rating, decision

**Function signature:**
```sql
CREATE OR REPLACE FUNCTION ML_ZONE.INFERENCE.PREDICT_CREDIT_SCORE(
    age INTEGER,
    annual_income FLOAT,
    debt_to_income FLOAT,
    credit_score INTEGER,
    -- ... other features
)
RETURNS VARIANT
```

**Returns:**
```json
{
  "score_band": 7,
  "credit_rating": "B+",
  "decision": "APPROVE",
  "max_credit_limit": 50000,
  "default_probability": 0.15
}
```

#### 2.3 Batch Scoring
**File:** `snowflake/04_ml/03_batch_scoring.sql`

**What it does:**
- Scores all customers in batch
- Stores predictions in table
- Updates credit applications with scores

**Table:**
- `ML_ZONE.PREDICTIONS.CREDIT_SCORE_PREDICTIONS`

### Implementation Steps

1. **Create ML schemas:**
   ```sql
   CREATE SCHEMA IF NOT EXISTS ML_ZONE.MODELS;
   CREATE SCHEMA IF NOT EXISTS ML_ZONE.INFERENCE;
   CREATE SCHEMA IF NOT EXISTS ML_ZONE.PREDICTIONS;
   ```

2. **Train model in Snowflake Notebook:**
   - Open Snowflake Notebooks
   - Create new notebook
   - Copy code from `01_train_credit_model.ipynb`
   - Run training
   - Verify model registered

3. **Create inference UDF:**
   ```sql
   -- Run 02_create_inference_udf.sql
   ```

4. **Test inference:**
   ```sql
   SELECT ML_ZONE.INFERENCE.PREDICT_CREDIT_SCORE(
       35, 75000, 0.25, 720, 0.3, 24, 1, 1, 1
   ) AS prediction;
   ```

5. **Batch score customers:**
   ```sql
   -- Run 03_batch_scoring.sql
   ```

**Estimated Time:** 3-4 hours  
**Priority:** 🔴 High (core functionality)

---

## 📊 Phase 3: Dashboards & Streamlit Pages

### Purpose
Create comprehensive UI for credit officers, risk managers, and executives.

### Files to Create

#### 3.1 Executive Dashboard
**File:** `streamlit/pages/1_📊_Executive_Dashboard.py`

**What it shows:**
- Portfolio KPIs (total loans, outstanding balance, default rate)
- Application metrics (pending, approved, declined)
- Risk metrics (delinquency rate, early warning alerts)
- Revenue metrics (interest income, fees)

**Key Metrics:**
```python
- Total Customers: 3,000
- Active Loans: 1,200
- Portfolio Value: $XXM
- Default Rate: X.X%
- Pending Applications: XX
- Average Decision Time: X hours
```

#### 3.2 Application Portal
**File:** `streamlit/pages/2_📝_Application_Portal.py`

**What it does:**
- Form to submit new credit applications
- Customer lookup and pre-fill
- Real-time credit score display
- ML model prediction integration

#### 3.3 Application Queue
**File:** `streamlit/pages/3_📋_Application_Queue.py`

**What it shows:**
- List of pending applications
- Filter by status, date, amount
- Quick actions (approve, decline, refer)
- Bulk operations

#### 3.4 Customer 360 Viewer
**File:** `streamlit/pages/5_👥_Customer_360.py`

**What it shows:**
- Unified customer profile
- Financial summary (accounts, loans, balances)
- Digital behavior (sessions, events)
- Credit bureau data
- Transaction history
- Risk profile

#### 3.5 Portfolio Analytics
**File:** `streamlit/pages/6_📈_Portfolio_Analytics.py`

**What it shows:**
- Portfolio performance charts
- Risk segment analysis
- Delinquency trends
- Geographic distribution
- Product performance

#### 3.6 Intelligence Chat (Cortex Analyst)
**File:** `streamlit/pages/7_💬_Intelligence_Chat.py`

**What it does:**
- Natural language to SQL queries
- Ask questions in plain English
- Visualize results automatically
- Export insights

**Example queries:**
- "Show me customers with credit score above 750"
- "What's the average loan amount by product?"
- "Which branch has the highest default rate?"

#### 3.7 Policy Manager
**File:** `streamlit/pages/8_📚_Policy_Manager.py`

**What it shows:**
- List of policy documents
- Search policies
- View policy content
- Upload new policies

#### 3.8 Governance Center
**File:** `streamlit/pages/9_🔒_Governance_Center.py`

**What it shows:**
- Data lineage visualization
- PII detection and masking status
- Access audit logs
- Compliance reports

### Implementation Steps

1. **Create dashboard pages:**
   ```bash
   cd streamlit/pages
   # Create each page file
   ```

2. **Update main.py navigation:**
   - Ensure all pages are listed
   - Add icons and descriptions

3. **Test each page:**
   ```bash
   streamlit run main.py
   ```

**Estimated Time:** 8-12 hours  
**Priority:** 🟡 Medium (enhances UX)

---

## 🧠 Phase 4: GenAI Features

### Purpose
Implement Cortex AI capabilities for intelligent credit decisioning.

### Files to Create

#### 4.1 Cortex Search Setup
**File:** `snowflake/06_genai/01_cortex_search_setup.sql`

**What it does:**
- Creates Cortex Search service
- Indexes policy documents
- Creates search endpoints

**Steps:**
```sql
-- Create service
CREATE SERVICE CORTEX_SEARCH_POLICIES
  IN COMPUTE POOL CORTEX_COMPUTE_POOL
  SPECIFICATION_FILE = 'policy_search_spec.yaml';

-- Index documents
CREATE CORTEX SEARCH INDEX POLICY_DOCUMENTS
  ON TABLE REFERENCE_DATA.POLICIES.POLICY_DOCUMENTS
  COLUMNS (CONTENT);
```

#### 4.2 Policy Documents Table
**File:** `snowflake/06_genai/02_create_policy_documents.sql`

**What it does:**
- Creates table for policy documents
- Loads existing policies
- Sets up for Cortex Search

**Table:**
- `REFERENCE_DATA.POLICIES.POLICY_DOCUMENTS`

**Columns:**
- POLICY_ID, POLICY_NAME, POLICY_TYPE, CONTENT, EFFECTIVE_DATE

#### 4.3 Cortex Agent Functions
**File:** `snowflake/06_genai/03_cortex_agent_functions.sql`

**What it does:**
- Creates SQL functions for agent tools
- Customer lookup function
- Credit score calculation
- Policy retrieval function

**Functions:**
```sql
CREATE FUNCTION AGENT_TOOLS.GET_CUSTOMER_DATA(customer_id VARCHAR)
CREATE FUNCTION AGENT_TOOLS.GET_CREDIT_SCORE(customer_id VARCHAR)
CREATE FUNCTION AGENT_TOOLS.SEARCH_POLICIES(query VARCHAR)
```

#### 4.4 Cortex Agent Definition
**File:** `snowflake/06_genai/04_create_credit_agent.sql`

**What it does:**
- Creates Cortex Agent for credit decisioning
- Configures system prompt
- Links to tools and search

**Agent configuration:**
```sql
CREATE CORTEX AGENT CREDIT_ANALYST_AGENT
  INSTRUCTIONS = 'You are a senior credit analyst...'
  TOOLS = (
    AGENT_TOOLS.GET_CUSTOMER_DATA,
    AGENT_TOOLS.GET_CREDIT_SCORE,
    AGENT_TOOLS.SEARCH_POLICIES
  )
  SEARCH_SERVICE = CORTEX_SEARCH_POLICIES;
```

#### 4.5 Update Streamlit AI Agent Page
**File:** `streamlit/pages/4_🤖_AI_Credit_Agent.py` (update existing)

**What to add:**
- Connect to Cortex Agent
- Call agent with application context
- Display agent reasoning
- Show policy references

### Implementation Steps

1. **Create GenAI schemas:**
   ```sql
   CREATE SCHEMA IF NOT EXISTS REFERENCE_DATA.POLICIES;
   CREATE SCHEMA IF NOT EXISTS AGENT_TOOLS;
   ```

2. **Load policy documents:**
   - Upload policy PDFs/text files
   - Insert into POLICY_DOCUMENTS table

3. **Set up Cortex Search:**
   - Run `01_cortex_search_setup.sql`
   - Verify indexing complete

4. **Create agent functions:**
   - Run `03_cortex_agent_functions.sql`
   - Test each function

5. **Create Cortex Agent:**
   - Run `04_create_credit_agent.sql`
   - Test agent in Snowflake UI

6. **Update Streamlit:**
   - Modify AI Credit Agent page
   - Connect to Cortex Agent API

**Estimated Time:** 6-8 hours  
**Priority:** 🟡 Medium (enhances AI capabilities)

---

## 📋 Implementation Order

### Week 1: Foundation
1. ✅ **Data Load** (DONE)
2. 🔴 **ETL Pipelines** (Phase 1) - 4-6 hours
   - Feature engineering
   - Customer 360 view
   - Portfolio analytics

### Week 2: Core ML
3. 🔴 **Machine Learning** (Phase 2) - 3-4 hours
   - Model training
   - Inference UDF
   - Batch scoring

### Week 3: UI Enhancement
4. 🟡 **Dashboards** (Phase 3) - 8-12 hours
   - Executive Dashboard
   - Application Portal/Queue
   - Customer 360
   - Portfolio Analytics

### Week 4: AI Features
5. 🟡 **GenAI** (Phase 4) - 6-8 hours
   - Cortex Search
   - Cortex Agent
   - Policy integration

---

## 🎯 Quick Start Guide

### Step 1: ETL Pipelines (Start Here!)

```bash
# 1. Create ETL directory
mkdir -p snowflake/03_etl

# 2. Create feature engineering script
# File: snowflake/03_etl/01_feature_engineering.sql
# (See implementationplan.md for full SQL)

# 3. Run in Snowflake UI
# Copy SQL from file → Paste in worksheet → Run
```

### Step 2: ML Model Training

```bash
# 1. Create ML directory
mkdir -p snowflake/04_ml

# 2. Open Snowflake Notebooks
# 3. Create new notebook: "Credit Scoring Model Training"
# 4. Copy code from implementationplan.md Section 9
# 5. Run training
```

### Step 3: Streamlit Dashboards

```bash
# 1. Create new page files in streamlit/pages/
# 2. Copy template from existing pages
# 3. Add your SQL queries and visualizations
# 4. Test locally: streamlit run main.py
```

---

## 📚 Reference Documents

- **Full Implementation Plan:** `implementationplan.md`
- **Technical Specs:** `TECHNICAL_SPECS.md`
- **Business Requirements:** `BUSINESS_REQUIREMENTS.md`
- **Architecture:** `TECHNICAL_PRESENTATION.md`

---

## ✅ Success Criteria

### Phase 1 (ETL) - Complete when:
- [ ] Feature store has 50+ features for all customers
- [ ] Customer 360 view shows unified data
- [ ] Portfolio analytics tables populated
- [ ] Dynamic tables refreshing automatically

### Phase 2 (ML) - Complete when:
- [ ] Model trained with >85% accuracy
- [ ] Inference UDF working in SQL
- [ ] Batch scoring complete for all customers
- [ ] Model predictions stored in table

### Phase 3 (Dashboards) - Complete when:
- [ ] All 9 Streamlit pages created
- [ ] Executive dashboard shows real KPIs
- [ ] Customer 360 displays unified profile
- [ ] Application queue functional

### Phase 4 (GenAI) - Complete when:
- [ ] Cortex Search indexing policies
- [ ] Cortex Agent responding to queries
- [ ] AI Credit Agent page using Cortex Agent
- [ ] Policy documents searchable

---

## 🆘 Need Help?

- **SQL Examples:** See `implementationplan.md` Sections 9-10
- **ML Code:** See `implementationplan.md` Section 9
- **Streamlit Patterns:** See existing `4_🤖_AI_Credit_Agent.py`
- **Cortex AI:** See `implementationplan.md` Sections 3-4

---

**Next Action:** Start with Phase 1 - ETL Pipelines! 🚀
