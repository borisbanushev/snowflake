# TODO: Next Steps

## 🔴 High Priority

### 1. Implement GenAI Phase 1 Features ⭐ **NEW**
**Status:** Ready to Start  
**Files:** `snowflake/06_genai/*.sql`

**Action Required:**
- Run SQL scripts in order:
  1. `00_create_schemas.sql` - Create Cortex schemas
  2. `01_load_policy_documents.sql` - Load policy documents
  3. `02_create_cortex_search.sql` - Create Cortex Search service
  4. `03_create_agent_tools.sql` - Create agent tool functions
  5. `04_create_cortex_agent.sql` - Create Credit Analyst Agent
  6. `05_create_explanation_function.sql` - Create ML explanation function

**What This Implements:**
- ✅ **Cortex Search** - Intelligent policy document search
- ✅ **Cortex Agent** - AI Credit Analyst that analyzes applications conversationally
- ✅ **ML Decision Explanations** - LLM-generated explanations for ML decisions

**Integration:**
- After SQL scripts, update `streamlit/pages/4_AI_Credit_Agent.py` with chat interface
- See `GENAI_PHASE1_IMPLEMENTATION.md` for detailed plan

**Prerequisites:**
- Snowflake Enterprise Edition (Cortex features)
- ML model deployed (`PREDICT_CREDIT_SCORE_BY_ID_V4`)
- Customer 360 data available

---

### 2. Create Hybrid Tables for OLTP Workloads
**Status:** Not Started  
**File:** `snowflake/05_unistore/hybrid_tables.sql`

**Action Required:**
- Run the SQL script to create hybrid tables:
  ```sql
  -- Execute: snowflake/05_unistore/hybrid_tables.sql
  ```
- This creates:
  - `APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS` - For storing credit applications
  - `APP_ZONE.TRANSACTIONAL.CREDIT_DECISIONS` - For storing decisions (OLTP writes)
  - `APP_ZONE.TRANSACTIONAL.AGENT_SESSIONS` - For tracking AI agent sessions

**Why:** The Streamlit AI Credit Agent page (`streamlit/pages/4_AI_Credit_Agent.py`) now performs real-time OLTP updates when users click action buttons. These hybrid tables are required for:
- ✅ Accept Recommendation button - Saves decisions to `CREDIT_DECISIONS`
- ✏️ Override Decision button - Records manual overrides
- 📤 Escalate button - Updates application status
- 🔄 Re-analyze button - Clears and reruns analysis

**Note:** Hybrid tables use Snowflake Unistore for high-performance OLTP workloads (low-latency writes, ACID transactions).

---

## 🟡 Medium Priority

### 3. Verify Hybrid Tables Exist
**Status:** Pending  
**Action:** After running `hybrid_tables.sql`, verify tables exist:
```sql
USE DATABASE CREDIT_DECISIONING_DB;
USE SCHEMA APP_ZONE.TRANSACTIONAL;

SHOW TABLES;
-- Should show: CREDIT_APPLICATIONS, CREDIT_DECISIONS, AGENT_SESSIONS
```

### 4. Test OLTP Functionality
**Status:** Pending  
**Action:** 
1. Open Streamlit app → AI Credit Agent page
2. Select a customer and run AI analysis
3. Click "✅ Accept Recommendation"
4. Verify data was written:
   ```sql
   SELECT * FROM APP_ZONE.TRANSACTIONAL.CREDIT_DECISIONS 
   ORDER BY DECISION_TIMESTAMP DESC LIMIT 5;
   
   SELECT * FROM APP_ZONE.TRANSACTIONAL.CREDIT_APPLICATIONS 
   ORDER BY LAST_UPDATED_AT DESC LIMIT 5;
   ```

### 5. Create Warehouse for OLTP (if not exists)
**Status:** Check Required  
**File:** `snowflake/00_setup/03_create_warehouses.sql`

**Action:** Verify `TRANSACTIONAL_WH` warehouse exists. If not, create it:
```sql
CREATE OR REPLACE WAREHOUSE TRANSACTIONAL_WH WITH
  WAREHOUSE_SIZE = 'SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 1
  COMMENT = 'OLTP workload warehouse for hybrid tables';
```

---

## 🟢 Low Priority / Future Enhancements

### 6. Add Application Queue View
**Status:** Already Created  
**File:** `snowflake/05_unistore/hybrid_tables.sql` (includes `V_APPLICATION_QUEUE` view)

**Action:** Test the view:
```sql
SELECT * FROM APP_ZONE.TRANSACTIONAL.V_APPLICATION_QUEUE 
WHERE STATUS = 'IN_REVIEW'
ORDER BY PRIORITY, SUBMITTED_AT;
```

### 7. Implement Four-Eyes Approval Workflow
**Status:** Not Started  
**Enhancement:** Add support for `FOUR_EYES_REQUIRED` flag in `CREDIT_DECISIONS` table for high-value applications requiring dual approval.

### 8. Add Decision Audit Trail
**Status:** Partial  
**Current:** `CREDIT_DECISIONS` table stores full audit trail  
**Enhancement:** Create a view or dashboard showing decision history and changes over time.

### 9. Integrate with Cortex AI Agent (Phase 1 Complete)
**Status:** Partial  
**Current:** Uses ML predictions from `ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS`  
**Enhancement:** Replace simulated agent with actual Cortex AI Agent calls when available.

---

## 📝 Notes

### Current Implementation Status
- ✅ **Streamlit Dashboards:** All 4 pages working (Executive, Customer 360, Portfolio Analytics, AI Credit Agent)
- ✅ **ML Model:** Trained and deployed (XGBoost credit scoring)
- ✅ **Batch Scoring:** Complete (scores all customers)
- ✅ **Real-time Inference:** Stored Procedure available (`PREDICT_CREDIT_SCORE_BY_ID_V4`)
- ✅ **ETL Pipelines:** Dynamic Tables created and running
- ⚠️ **OLTP Functionality:** Code implemented, but hybrid tables need to be created

### Architecture Overview
```
┌─────────────────────────────────────────────────────────┐
│  Streamlit App (UI Layer)                               │
│  └─ AI Credit Agent Page                                 │
│     └─ Action Buttons → OLTP Writes                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Hybrid Tables (Unistore - OLTP)                        │
│  ├─ CREDIT_APPLICATIONS                                 │
│  ├─ CREDIT_DECISIONS ← Real-time writes here            │
│  └─ AGENT_SESSIONS                                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Analytics Tables (OLAP)                                 │
│  ├─ ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS             │
│  ├─ ANALYTICS_CUSTOMER_360.CUSTOMER_360_UNIFIED        │
│  └─ ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES     │
└─────────────────────────────────────────────────────────┘
```

### Key Files Modified
- `streamlit/pages/4_AI_Credit_Agent.py` - Added real-time OLTP writes to hybrid tables
- `snowflake/05_unistore/hybrid_tables.sql` - Hybrid table definitions (needs to be run)

---

## ✅ Quick Start Checklist

### GenAI Phase 1 (NEW)
- [ ] Run `snowflake/06_genai/00_create_schemas.sql`
- [ ] Run `snowflake/06_genai/01_load_policy_documents.sql`
- [ ] Run `snowflake/06_genai/02_create_cortex_search.sql`
- [ ] Run `snowflake/06_genai/03_create_agent_tools.sql`
- [ ] Run `snowflake/06_genai/04_create_cortex_agent.sql`
- [ ] Run `snowflake/06_genai/05_create_explanation_function.sql`
- [ ] Test Cortex Search: `SELECT * FROM TABLE(APP_ZONE.CORTEX.AGENT_TOOLS.SEARCH_POLICIES('test', 3));`
- [ ] Test Cortex Agent: `SELECT APP_ZONE.CORTEX.CREDIT_ANALYST_AGENT!COMPLETE('test', '') AS RESPONSE;`
- [ ] Update Streamlit AI Credit Agent page with chat interface
- [ ] Test end-to-end: Chat with agent → Get explanation → Accept decision

### OLTP Hybrid Tables
- [ ] Run `snowflake/05_unistore/hybrid_tables.sql` in Snowflake
- [ ] Verify tables created: `SHOW TABLES IN SCHEMA APP_ZONE.TRANSACTIONAL;`
- [ ] Test "Accept Recommendation" button in Streamlit app
- [ ] Verify data appears in `CREDIT_DECISIONS` table
- [ ] Test other action buttons (Override, Escalate, Re-analyze)
- [ ] Check application status updates in `CREDIT_APPLICATIONS` table

---

**Last Updated:** 2026-02-02  
**Status:** Ready for OLTP implementation - hybrid tables need to be created
