# 🤖 GenAI Features Plan - Credit Decisioning Platform

**Platform:** Snowflake Cortex AI  
**Focus:** End-user features demonstrating Cortex Search, Agents, Analyst, and LLM capabilities  
**Last Updated:** February 2, 2026

---

## 🎯 Overview

This document outlines **demonstrable GenAI features** that showcase Snowflake Cortex capabilities in a credit decisioning context. Each feature is designed to be:
- ✅ **User-facing** - Direct value to credit officers, risk managers, customers
- ✅ **Demo-ready** - Impressive and easy to show in presentations
- ✅ **Production-realistic** - Solves real business problems
- ✅ **Cortex-powered** - Leverages Snowflake's GenAI capabilities

---

## 🚀 Feature Categories

### 1. **Cortex Search** - Intelligent Policy & Document Search
### 2. **Cortex Agents** - Conversational AI Credit Analyst
### 3. **Cortex Analyst** - Natural Language to SQL
### 4. **Cortex LLM Functions** - Text Generation & Analysis
### 5. **Cortex Fine-Tuning** - Custom Models on Bank Data

---

## 1. 🔍 Cortex Search Features

### 1.1 **Intelligent Policy Search**
**User Story:** "I need to find our policy on debt-to-income ratios for personal loans"

**Implementation:**
- Create a **Cortex Search Service** over bank policy documents
- Index documents from:
  - Internal credit policies (PDFs, Word docs)
  - Regulatory guidelines (Basel III, local regulations)
  - Industry best practices
  - ML model interpretation guides

**Demo Flow:**
1. Credit officer types: *"What's our policy for DTI ratios above 40%?"*
2. Cortex Search returns relevant policy sections with citations
3. Shows policy context: *"For DTI > 40%, require additional collateral or co-signer"*
4. Links to full policy document

**Technical:**
```sql
-- Create search service
CREATE SEARCH SERVICE credit_policies_search
  ON APP_ZONE.CORTEX.POLICY_DOCUMENTS
  USING 'snowflake-arctic-embed-v3';

-- Query example
SELECT * FROM SEARCH(
  SERVICE => 'credit_policies_search',
  QUERY => 'debt to income ratio policy for personal loans',
  LIMIT => 5
);
```

**Value:** Instant access to policies without manual document searching

---

### 1.2 **Regulatory Compliance Checker**
**User Story:** "Check if this credit decision complies with fair lending regulations"

**Implementation:**
- Index regulatory documents (CFPB, local banking regulations)
- Search service that checks decision against regulations
- Returns compliance checklist

**Demo Flow:**
1. After ML model recommends a decision
2. Click "Check Compliance"
3. Cortex Search queries regulatory documents
4. Returns:
   - ✅ Compliant with fair lending act
   - ⚠️ Requires documentation for decline reason
   - ✅ Meets minimum credit score requirements

**Value:** Automated compliance checking reduces regulatory risk

---

### 1.3 **ML Model Explanation Search**
**User Story:** "Why did the model give this customer a score of 650?"

**Implementation:**
- Index ML model documentation and feature importance guides
- Search service explains model decisions using policy context

**Demo Flow:**
1. View customer with ML score of 650
2. Click "Explain Score"
3. Cortex Search returns:
   - Feature contributions (e.g., "High DTI ratio reduced score by 50 points")
   - Policy interpretation ("Score of 650 falls in 'Moderate Risk' category per policy")
   - Recommended actions ("Consider requiring co-signer per policy section 4.2")

**Value:** Makes ML decisions transparent and explainable

---

## 2. 🤖 Cortex Agents Features

### 2.1 **AI Credit Analyst Agent** ⭐ **PRIMARY DEMO**
**User Story:** "I want to have a conversation with an AI credit analyst about this application"

**Implementation:**
- Create a **Cortex Agent** that acts as a senior credit analyst
- Agent has access to:
  - **Tool 1:** ML Model Inference (`PREDICT_CREDIT_SCORE_BY_ID_V4`)
  - **Tool 2:** Customer 360 Data (unified customer profile)
  - **Tool 3:** Policy Search (Cortex Search service)
  - **Tool 4:** Transaction History (query recent transactions)
  - **Tool 5:** Regulatory Check (compliance verification)

**Demo Flow:**
```
User: "Analyze customer CUS-000123 for a $50,000 personal loan"

Agent: "I'll analyze this application for you. Let me gather the information..."

[Agent calls ML model]
[Agent retrieves customer profile]
[Agent searches relevant policies]

Agent: "Based on my analysis:
- ML Score: 720 (Good rating)
- DTI Ratio: 32% (Within policy limits)
- Credit History: 5 years, no delinquencies
- Policy Check: ✅ Compliant with personal loan guidelines

**Recommendation: APPROVE**
- Approved Amount: $50,000
- Interest Rate: 8.5% (based on score band)
- Conditions: Standard terms apply

Would you like me to check anything specific?"

User: "What's their payment history?"

Agent: [Queries transaction data]
"Customer has made 60 consecutive on-time payments over the past 5 years. 
Average payment amount: $1,200/month. No late payments detected."

User: "What if we increase to $75,000?"

Agent: [Re-runs analysis with new amount]
"At $75,000, the DTI ratio would increase to 38%, which is still within 
our policy limit of 40%. However, the ML model recommends a maximum 
of $60,000 based on credit score. I recommend staying at $50,000 or 
requiring additional collateral for $75,000."
```

**Technical:**
```sql
-- Create Cortex Agent
CREATE AGENT credit_analyst_agent
  INSTRUCTIONS = 'You are a senior credit analyst at a bank. 
                  Analyze credit applications using ML models, 
                  customer data, and bank policies. Provide 
                  clear, actionable recommendations.'
  
  TOOLS = (
    -- ML Model Tool
    FUNCTION PREDICT_CREDIT_SCORE_BY_ID_V4(customer_id VARCHAR),
    
    -- Data Query Tool
    FUNCTION GET_CUSTOMER_360(customer_id VARCHAR),
    
    -- Policy Search Tool
    SEARCH SERVICE credit_policies_search,
    
    -- Transaction Query Tool
    FUNCTION GET_TRANSACTION_HISTORY(customer_id VARCHAR, months INTEGER)
  );
```

**Value:** Natural language interaction with credit decisioning system

---

### 2.2 **Risk Assessment Agent**
**User Story:** "Give me a comprehensive risk assessment for this customer"

**Implementation:**
- Specialized agent focused on risk analysis
- Uses multiple data sources and risk models
- Generates detailed risk report

**Demo Flow:**
```
User: "Assess risk for customer CUS-000456"

Agent: "**Risk Assessment Report**

**Credit Risk:**
- ML Score: 580 (Moderate-High Risk)
- Default Probability: 18%
- Credit Rating: D

**Financial Risk:**
- DTI Ratio: 45% (Above policy threshold)
- Liquidity: Low (3 months expenses in savings)
- Income Stability: Moderate (2 years at current job)

**Behavioral Risk:**
- Transaction Velocity: High (unusual spending patterns detected)
- Payment History: 2 late payments in past 12 months
- Digital Engagement: Low (infrequent app usage)

**Recommendation: DECLINE**
- Primary Reason: DTI exceeds policy limit
- Secondary Concerns: Payment history and income stability
- Alternative: Consider secured loan with collateral"
```

**Value:** Comprehensive risk analysis in natural language

---

### 2.3 **Customer Communication Agent**
**User Story:** "Generate a personalized credit decision letter for this customer"

**Implementation:**
- Agent generates customer-facing communications
- Uses Cortex LLM functions for text generation
- Personalizes based on customer profile and decision

**Demo Flow:**
```
User: "Generate approval letter for CUS-000789"

Agent: [Generates letter]

"Dear [Customer Name],

We are pleased to inform you that your application for a Personal Loan 
of $25,000 has been approved!

**Loan Details:**
- Approved Amount: $25,000
- Interest Rate: 7.5% APR
- Term: 36 months
- Monthly Payment: $778.50

**Why You Were Approved:**
Your strong credit history (720 credit score), stable income, and 
excellent payment record with our bank made you an ideal candidate.

**Next Steps:**
1. Review and accept the loan terms by [date]
2. Funds will be deposited within 2 business days
3. Set up automatic payments for convenience

Thank you for choosing [Bank Name]!

Sincerely,
Credit Department"
```

**Value:** Automated, personalized customer communications

---

## 3. 📊 Cortex Analyst Features

### 3.1 **Natural Language Portfolio Queries**
**User Story:** "Show me all customers with credit scores below 600 who have been late on payments"

**Implementation:**
- Use **Cortex Analyst** to convert natural language to SQL
- Query Customer 360 and transaction data
- Return results in Streamlit dashboard

**Demo Flow:**
```
User types: "Show me customers with credit scores below 600 who had 
             late payments in the last 3 months"

Cortex Analyst converts to SQL:
```sql
SELECT 
  c.CUSTOMER_ID,
  c.FULL_NAME,
  c.CREDIT_SCORE,
  COUNT(t.TRANSACTION_ID) AS LATE_PAYMENTS
FROM ANALYTICS_CUSTOMER_360.CUSTOMER_360_UNIFIED c
JOIN CURATED_ZONE.TRANSACTIONS.TRANSACTIONS t 
  ON c.CUSTOMER_ID = t.CUSTOMER_ID
WHERE c.CREDIT_SCORE < 600
  AND t.PAYMENT_STATUS = 'LATE'
  AND t.TRANSACTION_DATE >= DATEADD('MONTH', -3, CURRENT_DATE())
GROUP BY c.CUSTOMER_ID, c.FULL_NAME, c.CREDIT_SCORE
ORDER BY LATE_PAYMENTS DESC
```

Results displayed in interactive table/chart
```

**Value:** Business users can query data without SQL knowledge

---

### 3.2 **Ad-Hoc Risk Analysis**
**User Story:** "What's the average default rate for customers in the 25-35 age group?"

**Implementation:**
- Natural language queries against ML predictions and historical data
- Returns insights with visualizations

**Demo Flow:**
```
User: "What's the default rate for customers aged 25-35 with 
       credit scores between 600-700?"

Analyst: [Queries data, generates chart]

"**Analysis Results:**
- Sample Size: 1,247 customers
- Default Rate: 12.3%
- Average Credit Score: 648
- Average DTI Ratio: 35%

**Comparison:**
- Overall Portfolio Default Rate: 8.5%
- This segment is 45% higher risk than average

**Recommendation:** Consider additional underwriting criteria for this segment."
```

**Value:** Self-service analytics for risk managers

---

### 3.3 **Portfolio Health Dashboard Queries**
**User Story:** "Show me portfolio trends over the last 6 months"

**Implementation:**
- Natural language queries generate dashboard visualizations
- Updates in real-time

**Demo Flow:**
```
User: "Show portfolio health trends for the last 6 months"

Analyst: [Generates time series charts]
- Total Portfolio Value Over Time
- Default Rate Trend
- Average Credit Score Trend
- New Applications vs Approvals

User: "Drill down into the default rate spike in November"

Analyst: [Queries and explains]
"The spike in November (15.2% vs 8.5% average) was driven by:
- 45% of defaults came from customers with DTI > 40%
- 30% had credit scores below 600
- 25% had payment history issues"
```

**Value:** Interactive, conversational analytics

---

## 4. ✍️ Cortex LLM Functions Features

### 4.1 **ML Decision Explanation**
**User Story:** "Explain why the ML model recommended decline in plain English"

**Implementation:**
- Use `SNOWFLAKE.CORTEX.COMPLETE()` to generate explanations
- Input: ML model outputs, feature values, policy context
- Output: Human-readable explanation

**Demo Flow:**
```
ML Model Output:
- Score Band: 3 (D Rating)
- Decision: DECLINE
- Default Probability: 65%

[Click "Explain Decision"]

Generated Explanation:
"Based on our credit scoring model, this application has been 
declined due to several risk factors:

1. **High Default Risk (65%)**: The model predicts a 65% 
   probability of default, which exceeds our risk threshold.

2. **Low Credit Score (580)**: The customer's credit score of 
   580 falls in the 'Poor' category, indicating a history of 
   credit challenges.

3. **High Debt-to-Income Ratio (48%)**: With 48% of income 
   going to debt payments, the customer has limited financial 
   flexibility to handle additional debt.

4. **Recent Delinquencies**: The customer has 3 late payments 
   in the past 12 months, indicating payment reliability concerns.

**Recommendation:** The customer may be eligible for a secured 
loan or credit builder product to improve their credit profile 
before reapplying."
```

**Value:** Transparent, explainable AI decisions

---

### 4.2 **Risk Factor Summarization**
**User Story:** "Summarize the top risk factors for this customer"

**Implementation:**
- Use LLM to analyze customer profile and generate risk summary
- Highlight key concerns and opportunities

**Demo Flow:**
```
Customer Profile Data:
- Credit Score: 650
- DTI: 38%
- Payment History: 2 late payments
- Account Age: 3 years
- Income: $75,000/year

[Click "Generate Risk Summary"]

"**Risk Assessment Summary:**

**Strengths:**
- Moderate credit score (650) shows improving creditworthiness
- 3-year relationship with bank demonstrates loyalty
- Stable income source ($75,000/year)

**Concerns:**
- Debt-to-income ratio (38%) is approaching policy limit (40%)
- Recent payment history shows 2 late payments in past year
- Limited credit history (3 years) reduces predictability

**Overall Assessment:** Moderate risk profile. Recommend approval 
with standard terms and monitoring for first 6 months."
```

**Value:** Quick risk assessment summaries

---

### 4.3 **Policy Document Summarization**
**User Story:** "Summarize the key points from our credit policy document"

**Implementation:**
- Use LLM to summarize long policy documents
- Extract key requirements and thresholds

**Demo Flow:**
```
[Upload 50-page credit policy PDF]

[Click "Summarize Policy"]

"**Credit Policy Summary:**

**Key Requirements:**
1. Minimum Credit Score: 600 for unsecured loans
2. Maximum DTI Ratio: 40% (35% preferred)
3. Minimum Income: $50,000/year for personal loans
4. Payment History: No more than 2 late payments in 12 months

**Approval Thresholds:**
- Auto-approve: Score > 750, DTI < 30%
- Manual review: Score 600-750, DTI 30-40%
- Decline: Score < 600 or DTI > 40%

**Special Conditions:**
- Co-signer required for DTI 35-40%
- Collateral required for scores 600-650
- Income verification required for all applications"
```

**Value:** Quick access to policy key points

---

## 5. 🎯 Cortex Fine-Tuning Features

### 5.1 **Bank-Specific Credit Analyst Model**
**User Story:** "Train an AI model on our bank's historical credit decisions"

**Implementation:**
- Fine-tune a Cortex model on:
  - Historical credit decisions
  - Bank-specific terminology
  - Internal policies and procedures
  - Decision patterns and preferences

**Demo Flow:**
```
Training Data:
- 10,000 historical credit decisions
- Bank-specific decision criteria
- Internal policy references
- Risk assessment patterns

[Fine-tune model]

Result:
- Model understands bank-specific terminology
- Aligns with internal decision patterns
- Provides recommendations consistent with bank culture
- Better accuracy on bank-specific scenarios
```

**Value:** AI that understands your bank's unique approach

---

## 6. 🔗 Integrated GenAI Workflows

### 6.1 **End-to-End Credit Decision Workflow** ⭐ **COMPREHENSIVE DEMO**
**User Story:** Complete credit decisioning workflow using all GenAI features

**Workflow:**
1. **Customer Applies** → Application submitted
2. **Cortex Analyst** → Queries customer history: "Show me this customer's payment history"
3. **ML Model** → Generates credit score
4. **Cortex Search** → Searches policies: "What's our policy for this credit score?"
5. **Cortex Agent** → Analyzes application:
   - Calls ML model
   - Retrieves customer data
   - Searches policies
   - Generates recommendation
6. **Cortex LLM** → Explains decision in plain English
7. **Cortex Agent** → Generates customer communication letter
8. **Decision Saved** → Stored in hybrid tables (OLTP)

**Demo Value:** Shows complete GenAI-powered workflow

---

### 6.2 **Regulatory Inquiry Response**
**User Story:** "Generate a response to a regulatory inquiry about our credit decisions"

**Implementation:**
- Cortex Analyst queries decision data
- Cortex Search finds relevant regulations
- Cortex LLM generates compliant response

**Demo Flow:**
```
Regulatory Question: "Explain your credit decision process for 
                     customers with credit scores between 600-700"

System Response:
1. Cortex Analyst queries: "Show all decisions for scores 600-700"
2. Cortex Search: "Find regulations about credit scoring"
3. Cortex LLM generates response:

"Our credit decisioning process for customers with credit scores 
between 600-700 follows these steps:

1. **Initial ML Scoring**: All applications are scored using our 
   XGBoost model trained on 100,000+ historical decisions.

2. **Policy Compliance Check**: Decisions are validated against 
   our credit policy (Section 4.2) which requires:
   - Minimum credit score of 600
   - Maximum DTI ratio of 40%
   - No more than 2 late payments in 12 months

3. **Risk Assessment**: For scores 600-700, we apply moderate 
   risk criteria including:
   - Income verification
   - Employment stability check
   - Debt serviceability analysis

4. **Decision Distribution**: 
   - Approve: 65% (score 650-700, DTI < 35%)
   - Refer: 25% (score 600-650, requires review)
   - Decline: 10% (other risk factors present)

All decisions are logged with full audit trail per regulatory 
requirements."
```

**Value:** Automated regulatory compliance responses

---

## 📋 Implementation Priority

### Phase 1: Core Features (Week 1-2)
1. ✅ **Cortex Search** - Policy document search
2. ✅ **Cortex Agent** - AI Credit Analyst (basic version)
3. ✅ **Cortex LLM** - Decision explanations

### Phase 2: Enhanced Features (Week 3-4)
4. ✅ **Cortex Analyst** - Natural language queries
5. ✅ **Cortex Agent** - Risk assessment agent
6. ✅ **Cortex LLM** - Customer communications

### Phase 3: Advanced Features (Week 5-6)
7. ✅ **Cortex Fine-Tuning** - Bank-specific model
8. ✅ **Integrated Workflows** - End-to-end demos
9. ✅ **Regulatory Features** - Compliance automation

---

## 🎬 Demo Scripts

### Demo 1: "AI Credit Analyst Conversation" (5 minutes)
1. Open Streamlit → AI Credit Agent page
2. Select customer application
3. Start conversation with Cortex Agent
4. Agent analyzes application using ML + policies
5. Agent explains decision
6. Accept recommendation → Saves to hybrid table

### Demo 2: "Policy Search & Compliance" (3 minutes)
1. Credit officer needs policy information
2. Use Cortex Search to find policy
3. Check compliance for decision
4. View policy context and requirements

### Demo 3: "Natural Language Analytics" (3 minutes)
1. Risk manager asks: "Show me high-risk customers"
2. Cortex Analyst converts to SQL
3. Results displayed with visualizations
4. Follow-up questions answered naturally

### Demo 4: "End-to-End Workflow" (7 minutes)
1. Complete credit decision workflow
2. Show all GenAI features working together
3. Demonstrate real-time OLTP writes
4. Show audit trail and compliance

---

## 🛠️ Technical Requirements

### Prerequisites
- Snowflake Enterprise Edition
- Cortex AI enabled
- Hybrid tables created (`APP_ZONE.TRANSACTIONAL`)
- ML model trained and deployed
- Policy documents uploaded

### Data Sources Needed
- Policy documents (PDFs, Word docs)
- Regulatory documents
- ML model documentation
- Customer 360 data
- Transaction history
- Credit decisions history

### Cortex Services to Create
1. `credit_policies_search` - Policy document search
2. `regulatory_docs_search` - Regulatory compliance search
3. `credit_analyst_agent` - Main AI agent
4. `risk_assessment_agent` - Risk analysis agent
5. `customer_comm_agent` - Communication generation

---

## 📊 Success Metrics

### User Adoption
- Credit officers using AI agent: 80%+
- Natural language queries per day: 50+
- Policy searches per day: 100+

### Business Impact
- Decision time reduction: 75%
- Policy compliance: 100%
- User satisfaction: 4.5/5

### Technical Performance
- Agent response time: < 3 seconds
- Search accuracy: 90%+
- SQL generation accuracy: 95%+

---

**Next Steps:**
1. Create Cortex Search services for policy documents
2. Build Cortex Agent with tools
3. Integrate into Streamlit UI
4. Test end-to-end workflows
5. Prepare demo scripts

---

**Questions?** Review `TODO.md` for implementation checklist.
