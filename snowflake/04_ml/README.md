# Machine Learning - Credit Scoring Model

This directory contains scripts for training and deploying the XGBoost credit scoring model.

## Execution Order

1. **`00_create_schemas.sql`** - Creates ML Zone schemas
2. **`01_train_credit_model.py`** - Train model in Snowflake Notebook
3. **`02_create_inference_udf.sql`** - Create real-time scoring function
4. **`03_batch_scoring.sql`** - Score all customers in batch

## Step-by-Step Guide

### Step 1: Create Schemas

Run in Snowflake UI:
```sql
-- Run: 00_create_schemas.sql
```

### Step 2: Train Model (Snowflake Notebook)

1. **Open Snowflake Notebooks**
   - In Snowflake UI, click "Notebooks" in left sidebar
   - Click "+" to create new notebook
   - Name it: "Credit Scoring Model Training"

2. **Copy Training Script**
   - Open `01_train_credit_model.py`
   - Copy entire contents
   - Paste into Snowflake Notebook

3. **Run Training**
   - Click "Run All" or run cells one by one
   - Training will take 2-5 minutes
   - Model will be registered in ML Registry

4. **Verify Model**
   - Check ML Registry: `ML_MODELS`
   - Should see: `CREDIT_SCORING_XGBOOST` version `v1`

### Step 3: Create Inference UDF

Run in Snowflake UI:
```sql
-- Run: 02_create_inference_udf.sql
```

This creates a SQL function for real-time scoring:
```sql
SELECT ML_INFERENCE.PREDICT_CREDIT_SCORE(
    35, 75000, 0.25, 720, 0.3, 24, ...
) AS prediction;
```

### Step 4: Batch Score Customers

Run in Snowflake UI:
```sql
-- Run: 03_batch_scoring.sql
```

This will:
- Score all customers from feature store
- Store predictions in `ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS`
- Show summary statistics

## Model Details

### Algorithm
- **XGBoost Classifier** (Gradient Boosting)
- **10-band classification** (0-9)
- **100 estimators**, max depth 6, learning rate 0.1

### Features (40+)
- **Demographic**: Age, gender, marital status
- **Financial**: Income, DTI, balances, loans
- **Transaction**: 3M/6M/12M aggregations
- **Credit Bureau**: Scores, tradelines, inquiries
- **Digital**: Logins, sessions, engagement

### Output
- **Score Band**: 0-9 (higher = better)
- **Credit Rating**: F, E, D, C-, C, C+, B, B+, A, A+
- **Decision**: APPROVE (band ≥5) or DECLINE (band <5)
- **Max Credit Limit**: Based on income × multiplier
- **Default Probability**: 0.0-1.0

## Usage Examples

### Real-Time Scoring (Single Customer)

```sql
-- Get features for a customer
SELECT * FROM ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES
WHERE CUSTOMER_ID = 'CUST001';

-- Score the customer
SELECT ML_INFERENCE.PREDICT_CREDIT_SCORE(
    fs.F_AGE, fs.F_ANNUAL_INCOME, fs.F_DEBT_TO_INCOME,
    fs.F_CREDIT_SCORE, fs.F_CREDIT_UTILIZATION, fs.F_RELATIONSHIP_MONTHS,
    -- ... all 40+ features
) AS prediction
FROM ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES fs
WHERE fs.CUSTOMER_ID = 'CUST001';
```

### Batch Scoring (All Customers)

```sql
-- View all predictions
SELECT * FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
ORDER BY SCORE_BAND DESC;

-- Find approved customers
SELECT * FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
WHERE DECISION = 'APPROVE'
ORDER BY MAX_CREDIT_LIMIT DESC;
```

### Join with Customer 360

```sql
SELECT 
    c360.CUSTOMER_ID,
    c360.FULL_NAME,
    c360.CREDIT_SCORE,
    pred.CREDIT_RATING,
    pred.DECISION,
    pred.MAX_CREDIT_LIMIT,
    pred.DEFAULT_PROBABILITY
FROM ANALYTICS_CUSTOMER_360.CUSTOMER_360_UNIFIED c360
JOIN ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS pred
    ON c360.CUSTOMER_ID = pred.CUSTOMER_ID
ORDER BY pred.SCORE_BAND DESC;
```

## Model Performance

After training, check model metrics:

```sql
-- View model versions
SELECT * FROM TABLE(
    ML_MODELS.INFORMATION_SCHEMA.MODEL_VERSIONS()
)
WHERE MODEL_NAME = 'CREDIT_SCORING_XGBOOST';
```

## Troubleshooting

### Model Not Found Error

If you get "Model not found":
1. Verify model is registered: Check `ML_MODELS` schema
2. Check model name: Should be `CREDIT_SCORING_XGBOOST`
3. Check version: Should be `v1`

### Feature Mismatch Error

If features don't match:
1. Verify feature store has all required columns
2. Check feature names match exactly (case-sensitive)
3. Ensure no NULL values in required features

### UDF Creation Fails

If UDF creation fails:
1. Ensure model is trained first
2. Check Python runtime version (3.10)
3. Verify packages are available

## Next Steps

After ML model is deployed:

1. **Phase 3:** Build Streamlit dashboards (use predictions)
2. **Phase 4:** Set up GenAI features (Cortex Search, Agents)

See `NEXT_STEPS_ROADMAP.md` for full plan.
