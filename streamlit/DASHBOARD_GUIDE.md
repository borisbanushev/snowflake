# 📊 Streamlit Dashboard Guide

## 🎯 Created Dashboards

### 1. 📊 Executive Dashboard (`1_📊_Executive_Dashboard.py`)
**Purpose:** High-level portfolio overview and KPIs

**Features:**
- Key Performance Indicators (KPIs)
  - Total customers
  - Approval rate
  - Average score band
  - Average default probability
- Credit score distribution (bar chart)
- Decision breakdown (pie chart)
- Score band distribution
- Risk analysis by confidence level
- Default probability distribution
- Recent predictions table

**Data Sources:**
- `ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS` (batch-scored predictions)

---

### 2. 👥 Customer 360 (`2_👥_Customer_360.py`)
**Purpose:** Individual customer profile with credit score and financial data

**Features:**
- Customer search by ID
- Credit score prediction display
  - Credit rating
  - Score band
  - Decision (approve/decline)
  - Max credit limit
- Risk metrics with gauge chart
- Customer features from feature store
- Customer 360 unified view
- Customer list (if no search)

**Data Sources:**
- `ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS` (predictions)
- `ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES` (features)
- `ANALYTICS_CUSTOMER_360.CUSTOMER_360_UNIFIED` (unified view)

---

### 3. 📈 Portfolio Analytics (`3_📈_Portfolio_Analytics.py`)
**Purpose:** Risk analysis, trends, and portfolio metrics

**Features:**
- Portfolio summary metrics
- Score band analysis
  - Customer distribution
  - Approval rate by score band
- Risk distribution
  - By confidence level (pie chart)
  - Default probability histogram
- Credit limit analysis by rating
- Portfolio risk metrics
  - Customers by risk category
  - Total exposure by risk category

**Data Sources:**
- `ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS` (batch-scored predictions)

---

## 🚀 How to Run

### Option 1: Snowflake Streamlit (Recommended)
1. **Open Snowflake Web UI**
2. **Navigate to Streamlit** (in left sidebar)
3. **Create New App** or **Edit Existing**
4. **Set Main File:** `main.py`
5. **Set Pages Directory:** `pages/`
6. **Run the app**

### Option 2: Local Development
```bash
cd streamlit
pip install -r requirements.txt
streamlit run main.py
```

**Note:** For local development, you'll need to configure Snowflake connection:
```python
from snowflake.snowpark import Session

session = Session.builder.configs({
    "account": "your-account",
    "user": "your-user",
    "password": "your-password",
    "warehouse": "COMPUTE_WH",
    "database": "CREDIT_DECISIONING_DB",
    "schema": "PUBLIC"
}).create()
```

---

## 📋 Prerequisites

Before using the dashboards, ensure:

1. ✅ **Batch scoring completed** - Run `snowflake/04_ml/03_batch_scoring.py` in Snowflake Notebooks
2. ✅ **ETL pipelines created** - Run `snowflake/03_etl/*.sql` scripts
3. ✅ **ML model trained** - Run `snowflake/04_ml/01_train_credit_model.py` in Snowflake Notebooks

---

## 🎨 Dashboard Features

### Interactive Charts
- **Plotly charts** for interactive visualizations
- **Hover tooltips** for detailed information
- **Responsive design** for different screen sizes

### Real-time Data
- All dashboards query live data from Snowflake
- No caching - always shows current state
- Fast queries using pre-computed predictions

### Error Handling
- Graceful error messages if data not available
- Helpful suggestions if tables missing
- Fallback to stored procedure for real-time scoring

---

## 🔧 Customization

### Adding New Metrics
Edit the SQL queries in each dashboard file to add:
- New KPIs
- Additional charts
- Custom filters

### Styling
Modify the CSS in the `<style>` tags at the top of each file:
- Colors
- Fonts
- Layout
- Card styles

### Data Sources
Add new data sources by:
1. Creating new SQL queries
2. Converting to pandas DataFrames
3. Displaying with `st.dataframe()` or charts

---

## 📊 Example Queries

### Get Portfolio Summary
```sql
SELECT 
    COUNT(DISTINCT CUSTOMER_ID) AS total_customers,
    SUM(CASE WHEN DECISION = 'APPROVE' THEN 1 ELSE 0 END) AS approved,
    AVG(SCORE_BAND) AS avg_score
FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
```

### Get Customer Prediction
```sql
SELECT *
FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS
WHERE CUSTOMER_ID = 'CUS-000001'
ORDER BY PREDICTION_DATE DESC
LIMIT 1
```

### Real-time Scoring (Alternative)
```sql
CALL ML_INFERENCE.PREDICT_CREDIT_SCORE_BY_ID_V4('CUS-000001');
```

---

## 🐛 Troubleshooting

### "No data available"
- **Check:** Batch scoring has been run
- **Check:** Table `ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS` exists
- **Solution:** Run batch scoring script

### "Not connected to Snowflake"
- **Check:** Running in Snowflake Streamlit environment
- **Check:** Session is active
- **Solution:** Use Snowflake's Streamlit UI, not local

### Charts not displaying
- **Check:** Plotly is installed (`pip install plotly`)
- **Check:** Data is not empty
- **Solution:** Verify data exists in tables

---

## 📝 Next Steps

1. **Test dashboards** - Run each page and verify data displays
2. **Customize** - Add your own metrics and charts
3. **Add more pages** - Create additional dashboards as needed
4. **Integrate GenAI** - Add Cortex AI features for natural language queries

---

**Happy Dashboard Building! 🚀**
