#!/bin/bash
# SnowSQL upload with SAML/SSO - Multiple format attempts

cd /Users/boris/Desktop/snowflake/data/generated_csv

echo "🔐 Trying SAML/SSO Authentication"
echo "   Username: BORISBB"
echo "   Authenticator: externalbrowser"
echo ""

# Method 1: organization.account format (most common for SAML)
echo "📋 Attempt 1: Using MZHGUVK.BC67154 format..."
/Applications/SnowSQL.app/Contents/MacOS/snowsql \
  -a MZHGUVK.BC67154 \
  -u BORISBB \
  --authenticator externalbrowser \
  -r ACCOUNTADMIN \
  -d CREDIT_DECISIONING_DB \
  -w COMPUTE_WH \
  -q "PUT file://*.csv @CSV_DATA_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Success with MZHGUVK.BC67154 format!"
    exit 0
fi

echo ""
echo "⚠️  Attempt 1 failed. Trying alternative formats..."
echo ""

# Method 2: Just organization (browser will show account selection)
echo "📋 Attempt 2: Using MZHGUVK format (browser will prompt for account)..."
/Applications/SnowSQL.app/Contents/MacOS/snowsql \
  -a MZHGUVK \
  -u BORISBB \
  --authenticator externalbrowser \
  -r ACCOUNTADMIN \
  -d CREDIT_DECISIONING_DB \
  -w COMPUTE_WH \
  -q "PUT file://*.csv @CSV_DATA_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Success with MZHGUVK format!"
    exit 0
fi

echo ""
echo "❌ Both attempts failed. Please check:"
echo "   1. Your SSO provider is configured correctly"
echo "   2. You have access to the account"
echo "   3. Try connecting via Snowflake UI first to verify SSO works"
echo ""
echo "Alternative: Use the Snowflake Web UI to upload files manually"
echo "   Go to: Data → Databases → CREDIT_DECISIONING_DB → Stages → CSV_DATA_STAGE"
