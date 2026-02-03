"""
Snowflake Batch Scoring Script
Run this in Snowflake Notebooks to score all customers
"""

from snowflake.snowpark import Session
from snowflake.ml.registry import Registry
from snowflake.snowpark import functions as F
from snowflake.snowpark.context import get_active_session

# Get active session (works in Snowflake Notebooks)
session = get_active_session()

print("=" * 80)
print("🚀 BATCH CREDIT SCORE PREDICTION")
print("=" * 80)

# ============================================
# Step 1: Load Model
# ============================================
print("\n📦 Loading model from ML Registry...")

registry = Registry(
    session=session,
    database_name="CREDIT_DECISIONING_DB",
    schema_name="ML_MODELS"
)

model = registry.get_model("CREDIT_SCORING_XGBOOST").version("v1").load()
print("✅ Model loaded successfully!")

# ============================================
# Step 2: Load Feature Store
# ============================================
print("\n📊 Loading feature store...")

feature_df = session.table("ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES")
row_count = feature_df.count()
print(f"✅ Loaded {row_count:,} customer records")

# ============================================
# Step 3: Get Features List
# ============================================
NUMERIC_FEATURES = [
    'F_AGE', 'F_RELATIONSHIP_MONTHS',
    'F_TOTAL_ACCOUNTS', 'F_TOTAL_BALANCE', 'F_AVG_BALANCE', 'F_MAX_BALANCE',
    'F_TOTAL_AVAILABLE_LIMIT', 'F_ACCOUNT_UTILIZATION',
    'F_TOTAL_LOANS', 'F_TOTAL_OUTSTANDING', 'F_AVG_LOAN_AMOUNT',
    'F_TOTAL_MONTHLY_PAYMENT', 'F_MAX_DAYS_PAST_DUE', 'F_TOTAL_ARREARS',
    'F_DELINQUENT_LOANS', 'F_DEBT_TO_INCOME',
    'F_TXN_COUNT_3M', 'F_TXN_AMOUNT_3M', 'F_AVG_TXN_AMOUNT_3M',
    'F_DEBIT_COUNT_3M', 'F_CREDIT_COUNT_3M', 'F_TXN_VELOCITY_3M',
    'F_TXN_COUNT_6M', 'F_TXN_AMOUNT_6M', 'F_AVG_TXN_AMOUNT_6M',
    'F_TXN_COUNT_12M', 'F_TXN_AMOUNT_12M',
    'F_CREDIT_SCORE', 'F_CREDIT_UTILIZATION',
    'F_TOTAL_TRADELINES', 'F_OPEN_TRADELINES', 'F_DELINQUENT_TRADELINES',
    'F_PUBLIC_RECORDS', 'F_INQUIRIES_6M', 'F_INQUIRIES_12M',
    'F_LOGIN_COUNT', 'F_SESSION_COUNT_30D', 'F_AVG_SESSION_DURATION',
    'F_EVENT_COUNT_30D', 'F_DAYS_SINCE_LAST_LOGIN',
    'F_YEARS_EMPLOYED', 'F_DAYS_SINCE_KYC_REVIEW'
]

CATEGORICAL_FEATURES = [
    'F_GENDER_ENCODED', 'F_MARITAL_STATUS_ENCODED',
    'F_EMPLOYMENT_STATUS_ENCODED', 'F_PROPERTY_OWNER',
    'F_IS_ACTIVE', 'F_MFA_ENABLED', 'F_BIOMETRIC_ENABLED',
    'F_HIGH_RISK', 'F_KYC_VERIFIED'
]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# ============================================
# Step 4: Make Predictions
# ============================================
print("\n🤖 Generating predictions for all customers...")
print("   This may take a few minutes...")

predictions = model.predict(feature_df.select(ALL_FEATURES + ['CUSTOMER_ID']))

# ============================================
# Step 5: Process Results
# ============================================
print("\n📈 Processing prediction results...")

# Remap score band back to original scale (add 2)
min_target = 2
predictions_processed = predictions.select(
    feature_df['CUSTOMER_ID'],
    (F.col('PREDICTED_SCORE_BAND').cast('INTEGER') + min_target).alias('SCORE_BAND')
)

# Map score band to credit rating and decision
credit_ratings = ['F', 'E', 'D', 'C-', 'C', 'C+', 'B', 'B+', 'A', 'A+']
def map_credit_rating(score_band):
    return credit_ratings[score_band] if score_band < len(credit_ratings) else 'F'

# Add decision field
predictions_with_decision = predictions_processed.select(
    F.col('CUSTOMER_ID'),
    F.col('SCORE_BAND'),
    F.when(F.col('SCORE_BAND') >= 5, 'APPROVE').otherwise('DECLINE').alias('DECISION')
)

# ============================================
# Step 6: Save to Predictions Table
# ============================================
print("\n💾 Saving predictions to ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS...")

# Get feature values for calculations
feature_values = feature_df.select(
    'CUSTOMER_ID',
    'F_TOTAL_BALANCE'
).join(
    predictions_with_decision.select('CUSTOMER_ID', 'SCORE_BAND', 'DECISION'),
    on='CUSTOMER_ID'
)

# Calculate additional fields - create intermediate columns first
predictions_intermediate = feature_values.select(
    F.col('CUSTOMER_ID'),
    F.current_timestamp().alias('PREDICTION_DATE'),
    F.col('SCORE_BAND'),
    # Credit rating mapping
    F.when(F.col('SCORE_BAND') == 2, 'F')
     .when(F.col('SCORE_BAND') == 3, 'E')
     .when(F.col('SCORE_BAND') == 4, 'D')
     .when(F.col('SCORE_BAND') == 5, 'C-')
     .when(F.col('SCORE_BAND') == 6, 'C')
     .when(F.col('SCORE_BAND') == 7, 'C+')
     .when(F.col('SCORE_BAND') == 8, 'B')
     .when(F.col('SCORE_BAND') == 9, 'B+')
     .when(F.col('SCORE_BAND') == 10, 'A')
     .otherwise('A+').alias('CREDIT_RATING'),
    F.col('DECISION'),
    # Max credit limit (simplified calculation) - handle NULLs
    F.coalesce(
        (F.coalesce(F.col('F_TOTAL_BALANCE'), F.lit(0)) * F.lit(12) * 
         F.when(F.col('SCORE_BAND') >= 9, F.lit(3.0))
          .when(F.col('SCORE_BAND') == 8, F.lit(2.0))
          .when(F.col('SCORE_BAND') == 7, F.lit(1.5))
          .when(F.col('SCORE_BAND') == 6, F.lit(1.0))
          .when(F.col('SCORE_BAND') == 5, F.lit(0.75))
          .when(F.col('SCORE_BAND') == 4, F.lit(0.5))
          .when(F.col('SCORE_BAND') == 3, F.lit(0.3))
          .when(F.col('SCORE_BAND') == 2, F.lit(0.2))
          .otherwise(F.lit(0.1))).cast('INTEGER'),
        F.lit(0)
    ).alias('MAX_CREDIT_LIMIT'),
    # Default probability (ensure it's between 0 and 1)
    # Cast to DOUBLE first, then round to 3 decimal places
    F.round(F.least(F.greatest(((F.lit(10) - F.col('SCORE_BAND')) / F.lit(10.0)), F.lit(0.0)), F.lit(1.0)), 3).alias('DEFAULT_PROBABILITY'),
    # Confidence
    F.when((F.col('SCORE_BAND') >= 7) | (F.col('SCORE_BAND') <= 2), 'HIGH')
     .otherwise('MEDIUM').alias('CONFIDENCE'),
    # Note: PREDICTION_DETAILS will be added in next step to avoid circular reference
)

# Write to table without PREDICTION_DETAILS first (to avoid OBJECT_CONSTRUCT issues)
predictions_intermediate.write.mode("overwrite").save_as_table(
    "ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS_TEMP"
)

# Now create PREDICTION_DETAILS using SQL (more reliable for VARIANT types)
print("   Creating PREDICTION_DETAILS variant column...")
session.sql("""
    CREATE OR REPLACE TABLE ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS AS
    SELECT 
        CUSTOMER_ID,
        PREDICTION_DATE,
        SCORE_BAND,
        CREDIT_RATING,
        DECISION,
        MAX_CREDIT_LIMIT,
        DEFAULT_PROBABILITY,
        CONFIDENCE,
        OBJECT_CONSTRUCT(
            'score_band', CAST(SCORE_BAND AS STRING),
            'credit_rating', CREDIT_RATING,
            'decision', DECISION,
            'max_credit_limit', CAST(MAX_CREDIT_LIMIT AS STRING),
            'default_probability', CAST(DEFAULT_PROBABILITY AS STRING),
            'confidence', CONFIDENCE
        ) AS PREDICTION_DETAILS
    FROM ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS_TEMP
""").collect()

# Drop temp table
session.sql("DROP TABLE IF EXISTS ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS_TEMP").collect()

print("✅ Predictions saved successfully!")

# ============================================
# Step 7: Summary Statistics
# ============================================
print("\n📊 Summary Statistics:")
print("=" * 80)

summary = session.table("ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS").agg(
    F.count('*').alias('TOTAL_PREDICTIONS'),
    F.count_distinct('CUSTOMER_ID').alias('CUSTOMERS_SCORED'),
    F.sum(F.when(F.col('DECISION') == 'APPROVE', 1).otherwise(0)).alias('APPROVED_COUNT'),
    F.sum(F.when(F.col('DECISION') == 'DECLINE', 1).otherwise(0)).alias('DECLINED_COUNT'),
    F.avg('SCORE_BAND').alias('AVG_SCORE_BAND'),
    F.avg('DEFAULT_PROBABILITY').alias('AVG_DEFAULT_PROBABILITY')
)

summary.show()

print("\n✅ Batch scoring complete!")
print("=" * 80)
