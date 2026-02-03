# GenAI Phase 1 Implementation

**Status:** Ready for Implementation  
**Features:** Cortex Search, AI Credit Analyst Agent, ML Decision Explanations

---

## 📋 Overview

This folder contains SQL scripts to implement Phase 1 GenAI features for the Credit Decisioning Platform:

1. **Cortex Search** - Intelligent policy document search
2. **Cortex Agent** - AI Credit Analyst that analyzes applications
3. **ML Decision Explanations** - LLM-generated explanations for ML decisions

---

## 🚀 Implementation Order

Execute scripts in this order:

### Step 1: Setup
```sql
-- 1. Create schemas
@00_create_schemas.sql
```

### Step 2: Policy Documents
```sql
-- 2. Load policy documents
@01_load_policy_documents.sql
```

### Step 3: Cortex Search
```sql
-- 3. Create search service
@02_create_cortex_search.sql
```

### Step 4: Agent Tools
```sql
-- 4. Create agent tool functions
@03_create_agent_tools.sql
```

### Step 5: Cortex Agent
```sql
-- 5. Create Cortex Agent
@04_create_cortex_agent.sql
```

### Step 6: Explanation Function
```sql
-- 6. Create explanation function
@05_create_explanation_function.sql
```

---

## ✅ Prerequisites

- **Role:** Run all scripts as **ACCOUNTADMIN** (each script sets `USE ROLE ACCOUNTADMIN`).
- Snowflake Enterprise Edition (for Cortex features)
- Cortex AI enabled in your account
- ML model trained and deployed (`PREDICT_CREDIT_SCORE_BY_ID_V4` exists)
- Customer 360 data available (`ANALYTICS_CUSTOMER_360.CUSTOMER_360_UNIFIED`)
- Policy documents loaded

---

## 🧪 Testing

After running all scripts, test each component:

### Test 1: Policy Search (use SEARCH_PREVIEW with literal query; constant required)
```sql
SELECT f.value['DOCUMENT_NAME']::VARCHAR, f.value['CATEGORY']::VARCHAR, f.value['CONTENT']::VARCHAR
FROM (SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW('CREDIT_DECISIONING_DB.CORTEX.POLICY_SEARCH_SERVICE',
  '{"query": "What is the policy for credit score band 8?", "columns": ["DOCUMENT_NAME", "CATEGORY", "CONTENT"], "limit": 3}') AS resp) r,
LATERAL FLATTEN(INPUT => r.resp['results']) f;
```

### Test 2: Agent Tools
```sql
-- Get customer data
SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_CUSTOMER_DATA('CUS-000001');

-- Get credit score
SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_CREDIT_SCORE('CUS-000001');
```

### Test 3: Cortex Agent
Cortex Agents are not invoked from SQL. In Snowsight go to **AI & ML » Agents**, select **CREDIT_ANALYST_AGENT** (CREDIT_DECISIONING_DB.CORTEX), and use the agent playground to send e.g. *"Analyze customer CUS-000001 for a $50,000 personal loan"*. Alternatively use the [Cortex Agents REST API](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-rest-api) (`agents/:run`).

### Test 4: Explanation Function
```sql
SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.EXPLAIN_DECISION(
    'CUS-000001',
    8,
    'B+',
    'APPROVE',
    0.15,
    PARSE_JSON('{"CUSTOMER_ID": "CUS-000001", "CREDIT_SCORE": 720}')
) AS EXPLANATION;
```

---

## 📊 Expected Results

After implementation:

✅ **Cortex Search Service** - `POLICY_SEARCH_SERVICE` created and active  
✅ **Agent Tools** - 4 functions created (GET_CUSTOMER_DATA, GET_CREDIT_SCORE, SEARCH_POLICIES, GET_TRANSACTION_HISTORY)  
✅ **Cortex Agent** - `CREDIT_ANALYST_AGENT` created with tools and search service  
✅ **Explanation Function** - `EXPLAIN_DECISION` function available  

---

## 🔗 Integration with Streamlit

After SQL scripts are run, update `streamlit/pages/4_AI_Credit_Agent.py` to:

1. Call Cortex Agent for chat interface
2. Display agent responses
3. Generate explanations using `EXPLAIN_DECISION` function
4. Show policy references

See `GENAI_PHASE1_IMPLEMENTATION.md` for detailed Streamlit integration steps.

---

## 📚 Documentation

- **Implementation Plan:** `GENAI_PHASE1_IMPLEMENTATION.md`
- **Features Overview:** `GENAI_FEATURES_PLAN.md`
- **TODO:** `TODO.md`

---

## ⚠️ Troubleshooting

### Issue: "Model unavailable in your region" / EMBED_TEXT_768 error
**Cause:** The Cortex embedding model used by the search service is not available in your Snowflake region.

**Solution:** Enable cross-region inference (run once as ACCOUNTADMIN):
```sql
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
```
Then re-run `02_create_cortex_search.sql`. To restrict to specific regions use e.g. `'AWS_US,AWS_EU'`. See [Cross-region inference](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cross-region-inference).

### Issue: Cortex Search Service not created
**Solution:** Verify Enterprise Edition and Cortex AI enabled

### Issue: Agent tools return NULL
**Solution:** Check that customer IDs exist in your data

### Issue: Explanation function fails
**Solution:** Verify LLM model availability (`llama3-70b` or `snowflake-arctic`)

### Issue: Agent not responding
**Solution:** Check agent permissions and tool accessibility

---

## 🎯 What to Do After Running All SQL

### 1. Quick tests in Snowflake (Worksheet)

**Agent tools (use a real customer ID from your data):**
```sql
SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_CUSTOMER_DATA('CUS-000001');
SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_CREDIT_SCORE('CUS-000001');
SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_TRANSACTION_HISTORY('CUS-000001', 12);
```

**Cortex Agent:** Cortex Agents are **not** invoked from SQL. Use one of these:

1. **Snowsight (recommended):** In the left menu go to **AI & ML » Agents**. Select **CREDIT_ANALYST_AGENT** (database: CREDIT_DECISIONING_DB, schema: CORTEX). Use the **agent playground** on the agent details page: type e.g. *"Analyze customer CUS-000001 for a $50,000 personal loan"* and send. Ensure your role has **USAGE** on the agent (e.g. run as ACCOUNTADMIN or grant `GRANT USAGE ON AGENT CREDIT_DECISIONING_DB.CORTEX.CREDIT_ANALYST_AGENT TO ROLE your_role`).
2. **REST API:** Use the [Agents REST API](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-rest-api) (e.g. `POST .../agents/CREDIT_ANALYST_AGENT:run` with messages and optional thread_id).

**Explanation function (optional):**
```sql
SELECT CREDIT_DECISIONING_DB.AGENT_TOOLS.EXPLAIN_DECISION(
  'CUS-000001', 8, 'B+', 'APPROVE', 0.15,
  PARSE_JSON('{"CUSTOMER_ID": "CUS-000001", "CREDIT_SCORE": 720}')
) AS EXPLANATION;
```

Replace `CUS-000001` with a `CUSTOMER_ID` that exists in `ANALYTICS_CUSTOMER_360.CUSTOMER_360_UNIFIED` (e.g. run the first SELECT above to get real IDs).

### 2. Run the Streamlit app

From the project root:
```bash
cd streamlit && streamlit run main.py
```

Open the **AI Credit Agent** page (🤖). You can review applications and use “Analyze Case with Cortex AI”; the app currently uses ML predictions for the decision. To have the **Cortex Agent** generate the full narrative, the Streamlit app would need to call the Cortex Agents REST API (agent `:run` endpoint) and display the response.

### 3. Optional: wire Streamlit to the Cortex Agent

In `streamlit/pages/4_AI_Credit_Agent.py`, when the user clicks “Analyze Case with Cortex AI”, call the Cortex Agent via the REST API (agent `:run` with the user's prompt and optional thread_id) and render the API response in the “Decision Assistance Report” section.

---

**Questions?** See `GENAI_PHASE1_IMPLEMENTATION.md` for detailed instructions.
