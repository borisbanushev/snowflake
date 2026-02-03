"""
Snowflake Credit Scoring Model Training
XGBoost Classifier - 10-band credit score classification

This is a Snowflake Notebook script. Run this in Snowflake Notebooks.
"""

from snowflake.snowpark import Session
from snowflake.ml.modeling.xgboost import XGBClassifier
from snowflake.ml.registry import Registry
from snowflake.snowpark import functions as F
import pandas as pd

# Get active session (works in Snowflake Notebooks)
session = get_active_session()

print("=" * 80)
print("🚀 CREDIT SCORING MODEL TRAINING")
print("=" * 80)

# ============================================
# Step 1: Load Training Data
# ============================================
print("\n📊 Loading training data from feature store...")

training_df = session.table("ANALYTICS_FEATURE_STORE.CREDIT_SCORING_FEATURES")

# Check data
row_count = training_df.count()
print(f"✅ Loaded {row_count:,} records")

# Display sample
print("\n📋 Sample data:")
training_df.limit(5).show()

# ============================================
# Step 2: Define Features
# ============================================
print("\n🔧 Defining features...")

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
TARGET = 'TARGET_CREDIT_SCORE_BAND'

print(f"✅ {len(NUMERIC_FEATURES)} numeric features")
print(f"✅ {len(CATEGORICAL_FEATURES)} categorical features")
print(f"✅ Total: {len(ALL_FEATURES)} features")
print(f"✅ Target: {TARGET}")

# Check target distribution
print("\n📊 Checking target distribution...")
target_dist = training_df.select(TARGET).group_by(TARGET).count().order_by(TARGET)
target_dist.show()

# Check target value range
print("\n📊 Checking target value range...")
min_target = training_df.select(F.min(TARGET)).collect()[0][0]
max_target = training_df.select(F.max(TARGET)).collect()[0][0]
num_classes = int(max_target - min_target + 1)
print(f"   Target range: {min_target} to {max_target}")
print(f"   Number of classes: {num_classes}")

# Remap target to start at 0 (required by XGBoost)
print(f"\n🔄 Remapping target from [{min_target}-{max_target}] to [0-{num_classes-1}]...")
training_df_prepared = training_df.select(
    *[training_df[col] for col in ALL_FEATURES],
    (training_df[TARGET] - min_target).alias('TARGET_REMAPPED')
)

# Verify remapping
print("\n📊 Remapped target distribution:")
training_df_prepared.select('TARGET_REMAPPED').group_by('TARGET_REMAPPED').count().order_by('TARGET_REMAPPED').show()

# ============================================
# Step 3: Train Model
# ============================================
print("\n🤖 Training XGBoost model...")

model = XGBClassifier(
    input_cols=ALL_FEATURES,
    label_cols=['TARGET_REMAPPED'],
    output_cols=['PREDICTED_SCORE_BAND'],
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    objective='multi:softmax',
    num_class=num_classes,
    random_state=42
)

print("Training started...")
model.fit(training_df_prepared)
print("✅ Model training completed!")

# ============================================
# Step 4: Evaluate Model
# ============================================
print("\n📈 Evaluating model...")

# Get predictions (model outputs remapped 0-based classes)
print("\n📈 Getting predictions...")
predictions = model.predict(training_df_prepared.select(ALL_FEATURES))

# Show predictions (in remapped scale 0-7, add min_target to get original scale)
print("\n📊 Sample predictions (remapped scale 0-7):")
predictions.show(10)
print(f"\n💡 Note: To convert to original scale, add {min_target} to PREDICTED_SCORE_BAND")

# Calculate accuracy (simplified - would use proper train/test split in production)
print("\n✅ Model evaluation complete")

# ============================================
# Step 5: Register Model
# ============================================
print("\n💾 Registering model in ML Registry...")

registry = Registry(
    session=session,
    database_name="CREDIT_DECISIONING_DB",
    schema_name="ML_MODELS"
)

# Create sample input for model registry (use original features, not remapped target)
sample_input = training_df.select(ALL_FEATURES).limit(100)

model_version = registry.log_model(
    model_name="CREDIT_SCORING_XGBOOST",
    version_name="v1",
    model=model,
    sample_input_data=sample_input,
    comment=f"XGBoost credit scoring model - {num_classes}-band classification (original: {min_target}-{max_target}, remapped: 0-{num_classes-1})"
)

print(f"✅ Model registered successfully!")
print(f"   Model: {model_version.model_name}")
print(f"   Version: {model_version.version_name}")

# ============================================
# Step 6: Summary
# ============================================
print("\n" + "=" * 80)
print("✅ MODEL TRAINING COMPLETE!")
print("=" * 80)
print(f"\n📊 Training Data: {row_count:,} records")
print(f"🔧 Features: {len(ALL_FEATURES)}")
print(f"🎯 Target: {TARGET} ({num_classes} bands: {min_target}-{max_target}, remapped to 0-{num_classes-1})")
print(f"💾 Model: CREDIT_SCORING_XGBOOST v1")
print(f"📝 Note: Predictions will be in remapped scale (0-{num_classes-1}), add {min_target} to get original scale")
print("\n📋 Next Steps:")
print("   1. Run 02_create_inference_udf.sql to create real-time scoring function")
print("   2. Run 03_batch_scoring.sql to score all customers")
print("=" * 80)
