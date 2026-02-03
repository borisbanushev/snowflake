# 🚀 GenAI Phase 1 Implementation Plan

**Features:** Cortex Search, AI Credit Analyst Agent, ML Decision Explanations  
**Timeline:** 3-5 days  
**Last Updated:** February 2, 2026

---

## 📋 Table of Contents

1. [Final Outcome Overview](#final-outcome-overview)
2. [Architecture & Data Flow](#architecture--data-flow)
3. [Step-by-Step Implementation Plan](#step-by-step-implementation-plan)
4. [Code Structure](#code-structure)
5. [Testing & Validation](#testing--validation)
6. [Demo Script](#demo-script)

---

## 🎯 Final Outcome Overview

### What Users Will See

#### 1. **Enhanced AI Credit Agent Page** (Streamlit)

**Before (Current):**
- Static ML prediction display
- Placeholder "Run AI Agent Analysis" button
- No policy search
- No conversational interface
- Basic decision explanation

**After (Phase 1):**
- **Conversational AI Agent** - Chat interface where users can ask questions
- **Policy Search Integration** - Agent automatically searches policies when needed
- **Rich Decision Explanations** - LLM-generated explanations with context
- **Real-time Analysis** - Agent uses ML model, customer data, and policies
- **Visual Indicators** - Shows which tools agent is using (ML, Search, Data)

#### 2. **User Experience Flow**

```
┌─────────────────────────────────────────────────────────────┐
│  AI Credit Agent Page - Enhanced                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Customer Selection Dropdown]                              │
│  Selected: CUS-000123 - $50,000 Personal Loan              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🤖 AI Credit Analyst                                │  │
│  │                                                       │  │
│  │  [Chat Interface]                                     │  │
│  │                                                       │  │
│  │  👤 User: "Analyze this application"                │  │
│  │                                                       │  │
│  │  🤖 Agent: "I'll analyze this application for you.  │  │
│  │            Let me gather the information..."          │  │
│  │                                                       │  │
│  │  [Agent Status: 🔍 Retrieving customer data...]     │  │
│  │  [Agent Status: 🤖 Running ML model...]            │  │
│  │  [Agent Status: 📚 Searching policies...]           │  │
│  │                                                       │  │
│  │  🤖 Agent: "Based on my analysis:                    │  │
│  │                                                       │  │
│  │  **ML Score:** 720 (B+ Rating)                      │  │
│  │  **DTI Ratio:** 32% (Within policy limits)          │  │
│  │  **Credit History:** 5 years, no delinquencies      │  │
│  │  **Policy Check:** ✅ Compliant                      │  │
│  │                                                       │  │
│  │  **Recommendation: APPROVE**                         │  │
│  │  - Approved Amount: $50,000                          │  │
│  │  - Interest Rate: 8.5%                               │  │
│  │                                                       │  │
│  │  Would you like me to check anything specific?"      │  │
│  │                                                       │  │
│  │  👤 User: "What's their payment history?"          │  │
│  │                                                       │  │
│  │  🤖 Agent: "Customer has made 60 consecutive on-time │  │
│  │            payments over the past 5 years..."        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  📊 ML Decision Explanation                          │  │
│  │                                                       │  │
│  │  [Auto-generated explanation]                        │  │
│  │                                                       │  │
│  │  "Based on our credit scoring model, this           │  │
│  │   application has been **APPROVED** due to:          │  │
│  │                                                       │  │
│  │   1. **Strong Credit Score (720)**: Customer's      │  │
│  │      credit score of 720 falls in the 'Good'        │  │
│  │      category, indicating reliable payment history.  │  │
│  │                                                       │  │
│  │   2. **Low Default Risk (15%)**: The model          │  │
│  │      predicts only a 15% probability of default,    │  │
│  │      well below our risk threshold of 50%.          │  │
│  │                                                       │  │
│  │   3. **Healthy Debt-to-Income Ratio (32%)**:        │  │
│  │      With only 32% of income going to debt          │  │
│  │      payments, the customer has sufficient          │  │
│  │      financial flexibility.                          │  │
│  │                                                       │  │
│  │   4. **Excellent Payment History**: 60 consecutive │  │
│  │      on-time payments demonstrate reliability."      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  📚 Policy References                                │  │
│  │                                                       │  │
│  │  Agent referenced these policies:                    │  │
│  │  • Credit Scoring Model Usage Policy (Section 2)    │  │
│  │  • Personal Loan Guidelines (Section 4.2)           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  [✅ Accept Recommendation] [✏️ Override] [📤 Escalate]     │
└─────────────────────────────────────────────────────────────┘
```

#### 3. **Key Features**

✅ **Conversational Interface**
- Natural language chat with AI agent
- Follow-up questions supported
- Context-aware responses

✅ **Multi-Tool Agent**
- Calls ML model for credit scoring
- Searches customer 360 data
- Queries policy documents via Cortex Search
- Generates explanations using LLM

✅ **Policy Integration**
- Agent automatically searches policies
- Shows policy references in responses
- Validates decisions against policies

✅ **Rich Explanations**
- LLM-generated decision explanations
- Context-aware (uses customer data)
- Cites specific risk factors
- Provides actionable insights

---

## 🏗️ Architecture & Data Flow

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                        │
│  └─ AI Credit Agent Page (Enhanced Chat Interface)         │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ User Query
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Cortex Agent (Credit Analyst)                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  System Prompt: "You are a senior credit analyst..." │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                  │
│        ┌─────────────────┼─────────────────┐              │
│        │                 │                 │                │
│        ▼                 ▼                 ▼                │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │ Tool 1:   │    │ Tool 2:   │    │ Tool 3:   │            │
│  │ ML Model  │    │ Customer  │    │ Policy   │            │
│  │ Inference │    │ 360 Data │    │ Search   │            │
│  └──────────┘    └──────────┘    └──────────┘            │
│        │                 │                 │                │
└────────┼─────────────────┼─────────────────┼────────────────┘
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data & Services Layer                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  ML Model Inference                                    │ │
│  │  └─ PREDICT_CREDIT_SCORE_BY_ID_V4()                  │ │
│  │     Returns: Score Band, Rating, Decision, Limits     │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Customer 360 Data                                   │ │
│  │  └─ ANALYTICS_CUSTOMER_360.CUSTOMER_360_UNIFIED      │ │
│  │     Returns: Profile, Financials, History            │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Cortex Search Service                                │ │
│  │  └─ POLICY_SEARCH_SERVICE                             │ │
│  │     Index: APP_ZONE.CORTEX.CREDIT_POLICIES            │ │
│  │     Returns: Policy chunks with relevance scores      │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Cortex LLM Functions                                 │ │
│  │  └─ SNOWFLAKE.CORTEX.COMPLETE()                      │ │
│  │     Generates: Decision explanations                  │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Example

**User Query:** "Analyze customer CUS-000123 for a $50,000 loan"

1. **Agent receives query** → Parses intent
2. **Agent calls Tool 1 (ML Model)** → Gets credit score: 720, Band 8, B+ Rating
3. **Agent calls Tool 2 (Customer Data)** → Gets DTI: 32%, Payment History: 60 on-time payments
4. **Agent calls Tool 3 (Policy Search)** → Searches: "What's policy for score band 8?"
   - Returns: "Band 8 (B+): AUTO APPROVE, Max limit: 2.0x annual income"
5. **Agent synthesizes response** → Combines all information
6. **Agent generates explanation** → Uses LLM to create human-readable explanation
7. **UI displays** → Shows agent response, explanation, and policy references

---

## 📝 Step-by-Step Implementation Plan

### **Phase 1.1: Setup & Prerequisites** (Day 1, Morning)

#### Step 1.1.1: Create GenAI Schemas
**File:** `snowflake/06_genai/00_create_schemas.sql`

```sql
USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;

-- Cortex schema for AI services
CREATE SCHEMA IF NOT EXISTS APP_ZONE.CORTEX
  COMMENT = 'Cortex AI services - Search, Agents, LLM';

-- Agent tools schema
CREATE SCHEMA IF NOT EXISTS APP_ZONE.CORTEX.AGENT_TOOLS
  COMMENT = 'Functions and tools for Cortex Agents';

-- Grant permissions
GRANT USAGE ON SCHEMA APP_ZONE.CORTEX TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA APP_ZONE.CORTEX.AGENT_TOOLS TO ROLE SYSADMIN;
```

**Action:** Run this SQL script in Snowflake.

---

#### Step 1.1.2: Load Policy Documents
**File:** `snowflake/06_genai/01_load_policy_documents.sql`

**What it does:**
- Creates `CREDIT_POLICIES` table
- Loads policy documents (from `data/policies/credit_scoring_policy.txt`)
- Prepares documents for Cortex Search

**Key Tables:**
- `APP_ZONE.CORTEX.CREDIT_POLICIES` - Policy documents with chunks

**Action:** Run SQL script, verify policies loaded.

---

### **Phase 1.2: Cortex Search Setup** (Day 1, Afternoon)

#### Step 1.2.1: Create Policy Documents Table
**File:** `snowflake/06_genai/01_load_policy_documents.sql`

```sql
-- Create policy documents table
CREATE OR REPLACE TABLE APP_ZONE.CORTEX.CREDIT_POLICIES (
    POLICY_ID VARCHAR(36) DEFAULT UUID_STRING() PRIMARY KEY,
    DOCUMENT_NAME VARCHAR(200) NOT NULL,
    DOCUMENT_TYPE VARCHAR(50),  -- POLICY, GUIDELINE, REGULATION
    CATEGORY VARCHAR(100),       -- CREDIT_SCORING, RISK_MANAGEMENT, etc.
    VERSION VARCHAR(20),
    EFFECTIVE_DATE DATE,
    
    -- Content
    FULL_TEXT TEXT,
    
    -- Metadata
    DEPARTMENT VARCHAR(100),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Load policy document
INSERT INTO APP_ZONE.CORTEX.CREDIT_POLICIES 
(DOCUMENT_NAME, DOCUMENT_TYPE, CATEGORY, VERSION, EFFECTIVE_DATE, FULL_TEXT, DEPARTMENT)
VALUES
('Credit Scoring Model Usage Policy', 'POLICY', 'CREDIT_SCORING', 'v2.1', '2025-01-01',
 '[Content from data/policies/credit_scoring_policy.txt]',
 'Risk Management');
```

**Action:** Run script, verify 1+ policy documents loaded.

---

#### Step 1.2.2: Create Cortex Search Service
**File:** `snowflake/06_genai/02_create_cortex_search.sql`

```sql
-- Create Cortex Search Service for policies
CREATE OR REPLACE CORTEX SEARCH SERVICE APP_ZONE.CORTEX.POLICY_SEARCH_SERVICE
  ON APP_ZONE.CORTEX.CREDIT_POLICIES
  TARGET_LAG = '1 minute'
  AS (
    SELECT 
        POLICY_ID,
        DOCUMENT_NAME,
        DOCUMENT_TYPE,
        CATEGORY,
        FULL_TEXT AS CONTENT,
        EFFECTIVE_DATE
    FROM APP_ZONE.CORTEX.CREDIT_POLICIES
    WHERE IS_ACTIVE = TRUE
  );

-- Test search
SELECT 
    DOCUMENT_NAME,
    CATEGORY,
    CONTENT,
    SCORE
FROM TABLE(
    APP_ZONE.CORTEX.POLICY_SEARCH_SERVICE!SEARCH(
        'What is the policy for credit score band 8?',
        5
    )
);
```

**Action:** Run script, test search returns results.

---

#### Step 1.2.3: Create Search Helper Function
**File:** `snowflake/06_genai/02_create_cortex_search.sql` (continued)

```sql
-- Helper function for agent to search policies
CREATE OR REPLACE FUNCTION APP_ZONE.CORTEX.AGENT_TOOLS.SEARCH_POLICIES(
    query_text VARCHAR,
    num_results INTEGER DEFAULT 3
)
RETURNS TABLE (
    DOCUMENT_NAME VARCHAR,
    CATEGORY VARCHAR,
    CONTENT VARCHAR,
    RELEVANCE_SCORE FLOAT
)
LANGUAGE SQL
AS
$$
    SELECT 
        DOCUMENT_NAME,
        CATEGORY,
        CONTENT,
        SCORE AS RELEVANCE_SCORE
    FROM TABLE(
        APP_ZONE.CORTEX.POLICY_SEARCH_SERVICE!SEARCH(
            query_text,
            num_results
        )
    )
    ORDER BY SCORE DESC
$$;

-- Grant usage
GRANT USAGE ON FUNCTION APP_ZONE.CORTEX.AGENT_TOOLS.SEARCH_POLICIES(VARCHAR, INTEGER) 
  TO ROLE SYSADMIN;
```

**Action:** Run script, test function.

---

### **Phase 1.3: Agent Tools Setup** (Day 2, Morning)

#### Step 1.3.1: Create Customer Data Tool
**File:** `snowflake/06_genai/03_create_agent_tools.sql`

```sql
-- Tool 1: Get Customer 360 Data
CREATE OR REPLACE FUNCTION APP_ZONE.CORTEX.AGENT_TOOLS.GET_CUSTOMER_DATA(
    customer_id VARCHAR
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
    SELECT OBJECT_CONSTRUCT(
        'CUSTOMER_ID', CUSTOMER_ID,
        'FULL_NAME', FULL_NAME,
        'CREDIT_SCORE', CREDIT_SCORE,
        'RISK_CATEGORY', RISK_CATEGORY,
        'VERIFIED_ANNUAL_INCOME', VERIFIED_ANNUAL_INCOME,
        'DEBT_TO_INCOME_RATIO', DEBT_TO_INCOME_RATIO,
        'RELATIONSHIP_TENURE_MONTHS', RELATIONSHIP_TENURE_MONTHS,
        'TOTAL_DEPOSITS', TOTAL_DEPOSITS,
        'TOTAL_LOANS_OUTSTANDING', TOTAL_LOANS_OUTSTANDING
    )
    FROM ANALYTICS_CUSTOMER_360.CUSTOMER_360_UNIFIED
    WHERE CUSTOMER_ID = customer_id
    LIMIT 1
$$;

-- Tool 2: Get ML Credit Score (wrapper for stored procedure)
CREATE OR REPLACE FUNCTION APP_ZONE.CORTEX.AGENT_TOOLS.GET_CREDIT_SCORE(
    customer_id VARCHAR
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
    SELECT ML_INFERENCE.PREDICT_CREDIT_SCORE_BY_ID_V4(customer_id)
$$;

-- Grant usage
GRANT USAGE ON FUNCTION APP_ZONE.CORTEX.AGENT_TOOLS.GET_CUSTOMER_DATA(VARCHAR) 
  TO ROLE SYSADMIN;
GRANT USAGE ON FUNCTION APP_ZONE.CORTEX.AGENT_TOOLS.GET_CREDIT_SCORE(VARCHAR) 
  TO ROLE SYSADMIN;
```

**Action:** Run script, test functions return data.

---

### **Phase 1.4: Create Cortex Agent** (Day 2, Afternoon)

#### Step 1.4.1: Create Credit Analyst Agent
**File:** `snowflake/06_genai/04_create_cortex_agent.sql`

```sql
-- Create Cortex Agent for Credit Analysis
CREATE OR REPLACE CORTEX AGENT APP_ZONE.CORTEX.CREDIT_ANALYST_AGENT
  INSTRUCTIONS = 'You are a senior credit analyst at a bank. Your role is to analyze credit applications and provide recommendations.

When analyzing an application:
1. First, get the customer data using GET_CUSTOMER_DATA
2. Get the ML credit score using GET_CREDIT_SCORE
3. Search relevant policies using SEARCH_POLICIES
4. Synthesize the information and provide a clear recommendation

Always:
- Cite specific policy sections when referencing policies
- Explain your reasoning clearly
- Provide actionable recommendations
- Consider both ML model outputs and policy requirements
- Be professional and helpful

Format your responses clearly with sections for:
- ML Score Summary
- Policy Compliance Check
- Risk Assessment
- Final Recommendation'

  TOOLS = (
    APP_ZONE.CORTEX.AGENT_TOOLS.GET_CUSTOMER_DATA,
    APP_ZONE.CORTEX.AGENT_TOOLS.GET_CREDIT_SCORE,
    APP_ZONE.CORTEX.AGENT_TOOLS.SEARCH_POLICIES
  )
  
  SEARCH_SERVICE = APP_ZONE.CORTEX.POLICY_SEARCH_SERVICE;

-- Grant usage
GRANT USAGE ON AGENT APP_ZONE.CORTEX.CREDIT_ANALYST_AGENT TO ROLE SYSADMIN;
```

**Action:** Run script, verify agent created.

---

### **Phase 1.5: ML Decision Explanations** (Day 3, Morning)

#### Step 1.5.1: Create Explanation Function
**File:** `snowflake/06_genai/05_create_explanation_function.sql`

```sql
-- Function to generate ML decision explanations using Cortex LLM
CREATE OR REPLACE FUNCTION APP_ZONE.CORTEX.AGENT_TOOLS.EXPLAIN_DECISION(
    customer_id VARCHAR,
    ml_score_band INTEGER,
    ml_credit_rating VARCHAR,
    ml_decision VARCHAR,
    ml_default_prob FLOAT,
    customer_data VARIANT
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'snowflake-arctic-llama3-70b-v1-1',  -- or 'llama3-70b' depending on availability
        CONCAT(
            'You are a credit analyst explaining a credit decision to a credit officer. ',
            'Generate a clear, professional explanation in 3-4 paragraphs. ',
            'Be specific about risk factors and cite numbers. ',
            'Use a professional but accessible tone.\n\n',
            'Customer ID: ', customer_id, '\n',
            'ML Score Band: ', ml_score_band, '/9\n',
            'Credit Rating: ', ml_credit_rating, '\n',
            'ML Recommendation: ', ml_decision, '\n',
            'Default Probability: ', ROUND(ml_default_prob * 100, 1), '%\n',
            'Customer Data: ', customer_data::VARCHAR, '\n\n',
            'Explain why the ML model made this recommendation, highlighting ',
            'the key factors that influenced the decision. Be specific about ',
            'what risk factors were considered and why this decision was made.'
        )
    ) AS EXPLANATION
$$;

-- Grant usage
GRANT USAGE ON FUNCTION APP_ZONE.CORTEX.AGENT_TOOLS.EXPLAIN_DECISION(
    VARCHAR, INTEGER, VARCHAR, VARCHAR, FLOAT, VARIANT
) TO ROLE SYSADMIN;
```

**Action:** Run script, test function with sample data.

---

### **Phase 1.6: Streamlit Integration** (Day 3, Afternoon - Day 4)

#### Step 1.6.1: Update AI Credit Agent Page
**File:** `streamlit/pages/4_AI_Credit_Agent.py`

**Changes needed:**
1. Add chat interface (using `st.chat_message`)
2. Integrate Cortex Agent calls
3. Add explanation generation
4. Display policy references
5. Show agent tool usage status

**Key additions:**
```python
# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask the AI agent about this application..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Call Cortex Agent
    agent_response = session.sql(f"""
        SELECT APP_ZONE.CORTEX.CREDIT_ANALYST_AGENT!COMPLETE(
            '{prompt}',
            'customer_id: {customer_id}'
        ) AS RESPONSE
    """).collect()[0]['RESPONSE']
    
    # Add agent response
    st.session_state.messages.append({"role": "assistant", "content": agent_response})
    
    # Generate explanation
    explanation = generate_explanation(customer_id, ml_prediction)
    
    # Display explanation
    st.markdown("### 📊 ML Decision Explanation")
    st.markdown(explanation)
```

**Action:** Update Streamlit file, test chat interface.

---

#### Step 1.6.2: Add Explanation Display
**File:** `streamlit/pages/4_AI_Credit_Agent.py` (continued)

**Add explanation section after agent response:**
```python
def generate_explanation(session, customer_id, ml_prediction):
    """Generate LLM explanation for ML decision"""
    try:
        # Get customer data
        customer_data = session.sql(f"""
            SELECT APP_ZONE.CORTEX.AGENT_TOOLS.GET_CUSTOMER_DATA('{customer_id}') AS DATA
        """).collect()[0]['DATA']
        
        # Generate explanation
        explanation = session.sql(f"""
            SELECT APP_ZONE.CORTEX.AGENT_TOOLS.EXPLAIN_DECISION(
                '{customer_id}',
                {ml_prediction['SCORE_BAND']},
                '{ml_prediction['CREDIT_RATING']}',
                '{ml_prediction['DECISION']}',
                {ml_prediction['DEFAULT_PROBABILITY']},
                PARSE_JSON('{json.dumps(customer_data)}')
            ) AS EXPLANATION
        """).collect()[0]['EXPLANATION']
        
        return explanation
    except Exception as e:
        return f"Error generating explanation: {e}"
```

**Action:** Add function, integrate into UI.

---

### **Phase 1.7: Testing & Refinement** (Day 5)

#### Step 1.7.1: Test Each Component
1. ✅ Test Cortex Search - Verify policy search works
2. ✅ Test Agent Tools - Verify functions return data
3. ✅ Test Cortex Agent - Verify agent responds correctly
4. ✅ Test Explanation Function - Verify explanations generated
5. ✅ Test Streamlit Integration - Verify UI works end-to-end

#### Step 1.7.2: Error Handling
- Add try-catch blocks
- Handle missing data gracefully
- Show helpful error messages

#### Step 1.7.3: Performance Optimization
- Cache agent responses where appropriate
- Optimize search queries
- Add loading indicators

---

## 📁 Code Structure

```
snowflake/
└── 06_genai/
    ├── 00_create_schemas.sql          # Create schemas
    ├── 01_load_policy_documents.sql   # Load policies
    ├── 02_create_cortex_search.sql     # Cortex Search setup
    ├── 03_create_agent_tools.sql      # Agent tool functions
    ├── 04_create_cortex_agent.sql     # Cortex Agent creation
    └── 05_create_explanation_function.sql  # LLM explanation function

streamlit/
└── pages/
    └── 4_AI_Credit_Agent.py           # Updated with chat interface
```

---

## ✅ Testing & Validation

### Test Cases

#### Test 1: Policy Search
```sql
-- Should return policy about credit score bands
SELECT * FROM TABLE(
    APP_ZONE.CORTEX.POLICY_SEARCH_SERVICE!SEARCH(
        'What is the policy for credit score band 8?',
        3
    )
);
-- Expected: Returns policy document chunks about band 8
```

#### Test 2: Agent Tool - Customer Data
```sql
-- Should return customer profile
SELECT APP_ZONE.CORTEX.AGENT_TOOLS.GET_CUSTOMER_DATA('CUS-000001') AS DATA;
-- Expected: Returns JSON with customer data
```

#### Test 3: Agent Tool - Credit Score
```sql
-- Should return ML prediction
SELECT APP_ZONE.CORTEX.AGENT_TOOLS.GET_CREDIT_SCORE('CUS-000001') AS SCORE;
-- Expected: Returns JSON with score, rating, decision
```

#### Test 4: Cortex Agent
```sql
-- Should analyze application
SELECT APP_ZONE.CORTEX.CREDIT_ANALYST_AGENT!COMPLETE(
    'Analyze customer CUS-000001 for a $50,000 personal loan',
    'customer_id: CUS-000001'
) AS RESPONSE;
-- Expected: Returns analysis with ML score, policy check, recommendation
```

#### Test 5: Explanation Function
```sql
-- Should generate explanation
SELECT APP_ZONE.CORTEX.AGENT_TOOLS.EXPLAIN_DECISION(
    'CUS-000001',
    8,
    'B+',
    'APPROVE',
    0.15,
    PARSE_JSON('{"CUSTOMER_ID": "CUS-000001", "CREDIT_SCORE": 720}')
) AS EXPLANATION;
-- Expected: Returns human-readable explanation
```

---

## 🎬 Demo Script

### 5-Minute Demo Flow

1. **Open Streamlit App** (30 sec)
   - Navigate to AI Credit Agent page
   - Show current state

2. **Select Customer** (30 sec)
   - Select customer from dropdown
   - Show customer profile in sidebar

3. **Start Conversation** (2 min)
   - Type: "Analyze this application for a $50,000 personal loan"
   - Show agent thinking (tool usage indicators)
   - Display agent response with:
     - ML score summary
     - Policy compliance check
     - Recommendation

4. **Follow-up Question** (1 min)
   - Type: "What's their payment history?"
   - Show agent retrieving data
   - Display detailed payment history

5. **View Explanation** (1 min)
   - Show auto-generated ML decision explanation
   - Highlight key risk factors
   - Show policy references

6. **Accept Decision** (30 sec)
   - Click "Accept Recommendation"
   - Show success message
   - Verify data saved to hybrid table

---

## 🚨 Common Issues & Solutions

### Issue 1: Cortex Agent not responding
**Solution:** Check agent permissions, verify tools are accessible

### Issue 2: Policy search returns no results
**Solution:** Verify policies loaded, check search service is active

### Issue 3: Explanation function fails
**Solution:** Check LLM model availability, verify input parameters

### Issue 4: Streamlit chat not updating
**Solution:** Ensure `st.session_state.messages` is initialized, use `st.rerun()`

---

## 📊 Success Criteria

✅ **Functional:**
- Agent responds to queries within 5 seconds
- Policy search returns relevant results
- Explanations are coherent and accurate
- Chat interface works smoothly

✅ **User Experience:**
- Natural conversation flow
- Clear agent responses
- Helpful explanations
- Visual indicators for tool usage

✅ **Technical:**
- All components integrated
- Error handling in place
- Performance acceptable
- Code documented

---

## 🎯 Next Steps After Phase 1

1. **Phase 2:** Enhanced features (Risk Assessment Agent, Customer Communications)
2. **Phase 3:** Fine-tuning on bank-specific data
3. **Production:** Deploy to production environment
4. **Monitoring:** Set up AI observability

---

**Ready to start?** Begin with Step 1.1.1: Create GenAI Schemas
