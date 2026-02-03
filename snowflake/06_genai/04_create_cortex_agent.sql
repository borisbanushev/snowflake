-- ============================================
-- Snowflake Credit Decisioning Platform
-- GenAI Phase 1: Create Cortex Agent
-- ============================================
-- Role: ACCOUNTADMIN
-- Syntax: CREATE AGENT ... FROM SPECIFICATION $$ YAML $$ (no CORTEX keyword)

USE ROLE ACCOUNTADMIN;
USE DATABASE CREDIT_DECISIONING_DB;
USE WAREHOUSE COMPUTE_WH;
USE SCHEMA CORTEX;

-- ============================================
-- CREATE CORTEX AGENT: CREDIT ANALYST
-- ============================================
-- This agent acts as a senior credit analyst
-- It has access to customer data, credit score, transaction history, and policy search

CREATE OR REPLACE AGENT CREDIT_ANALYST_AGENT
  COMMENT = 'Senior credit analyst agent for loan applications'
  FROM SPECIFICATION $$
models:
  orchestration: claude-4-sonnet
orchestration:
  budget:
    seconds: 60
    tokens: 16000
instructions:
  response: |
    You are a senior credit analyst at a bank. Your role is to analyze credit applications and provide clear, actionable recommendations.

    When analyzing an application:
    1. First, get the customer data using GET_CUSTOMER_DATA(customer_id)
    2. Get the credit score using GET_CREDIT_SCORE(customer_id)
    3. Optionally get transaction history using GET_TRANSACTION_HISTORY(customer_id, months)
    4. Search relevant policies using the PolicySearch tool
    5. Synthesize the information and provide a clear recommendation

    Always:
    - Cite specific policy sections when referencing policies
    - Explain your reasoning clearly with numbers and facts
    - Provide actionable recommendations (APPROVE, DECLINE, or REFER)
    - Consider both credit score outputs and policy requirements
    - Be professional, helpful, and concise
    - Format responses clearly with sections

    Response Format:
    **Credit Score Summary:**
    - Credit Score / Rating
    - Key metrics (debt-to-income, utilization, etc.)

    **Policy Compliance Check:**
    - Policy check results and compliance status

    **Risk Assessment:**
    - Key risk factors and mitigating factors

    **Final Recommendation:**
    - Decision: APPROVE/DECLINE/REFER
    - Approved Amount (if approve), Interest Rate, Conditions

    When asked follow-up questions, use the appropriate tool and provide clear, specific answers.
  orchestration: "For customer data use GET_CUSTOMER_DATA; for credit score use GET_CREDIT_SCORE; for transaction history use GET_TRANSACTION_HISTORY; for policy or compliance questions use PolicySearch."
  system: "You are a senior credit analyst. Be precise with numbers and cite policies when relevant."
tools:
  - tool_spec:
      type: generic
      name: GET_CUSTOMER_DATA
      description: "Returns the customer 360 profile (demographics, balances, credit score, risk category) for a given customer_id."
      input_schema:
        type: object
        properties:
          customer_id:
            type: string
            description: "Customer identifier, e.g. CUS-000001"
        required:
          - customer_id
  - tool_spec:
      type: generic
      name: GET_CREDIT_SCORE
      description: "Returns credit score, rating, utilization and debt-to-income for a customer."
      input_schema:
        type: object
        properties:
          customer_id:
            type: string
            description: "Customer identifier"
        required:
          - customer_id
  - tool_spec:
      type: generic
      name: GET_TRANSACTION_HISTORY
      description: "Returns transaction summary for a customer over the last N months (count, total amount, averages)."
      input_schema:
        type: object
        properties:
          customer_id:
            type: string
            description: "Customer identifier"
          months:
            type: integer
            description: "Number of months to look back (default 12)"
        required:
          - customer_id
  - tool_spec:
      type: cortex_search
      name: PolicySearch
      description: "Searches credit and lending policy documents. Use for compliance and policy questions."
tool_resources:
  GET_CUSTOMER_DATA:
    type: function
    execution_environment:
      type: warehouse
      warehouse: COMPUTE_WH
    identifier: CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_CUSTOMER_DATA
  GET_CREDIT_SCORE:
    type: function
    execution_environment:
      type: warehouse
      warehouse: COMPUTE_WH
    identifier: CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_CREDIT_SCORE
  GET_TRANSACTION_HISTORY:
    type: function
    execution_environment:
      type: warehouse
      warehouse: COMPUTE_WH
    identifier: CREDIT_DECISIONING_DB.AGENT_TOOLS.GET_TRANSACTION_HISTORY
  PolicySearch:
    name: CREDIT_DECISIONING_DB.CORTEX.POLICY_SEARCH_SERVICE
    max_results: "5"
$$;

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

GRANT USAGE ON AGENT CREDIT_DECISIONING_DB.CORTEX.CREDIT_ANALYST_AGENT TO ROLE SYSADMIN;

-- ============================================
-- HOW TO TEST THE AGENT
-- ============================================
-- Cortex Agents are NOT invoked from SQL. Use Snowsight or the REST API:
-- 1. Snowsight: Left menu > AI & ML > Agents > select CREDIT_ANALYST_AGENT > use the agent playground (chat).
-- 2. REST API: POST .../agents/CREDIT_ANALYST_AGENT:run (see Cortex Agents REST API docs).

-- ============================================
-- VERIFICATION
-- ============================================

SHOW AGENTS LIKE 'CREDIT_ANALYST_AGENT' IN SCHEMA CREDIT_DECISIONING_DB.CORTEX;
