#!/bin/bash
# SnowSQL upload with External Browser Authentication (SAML/SSO)

cd /Users/boris/Desktop/snowflake/data/generated_csv

echo "🔐 Using External Browser Authentication (SAML/SSO)"
echo "   Organization: MZHGUVK"
echo "   Account: BC67154"
echo "   Username: BORISBB"
echo "   Authenticator: externalbrowser"
echo ""
echo "📤 Uploading CSV files..."
echo "⚠️  A browser window will open for SSO authentication..."
echo ""

# For SAML/SSO accounts, use organization.account format
# Try Method 1: organization.account format
echo "Trying organization.account format..."
/Applications/SnowSQL.app/Contents/MacOS/snowsql \
  -a MZHGUVK.BC67154 \
  -u BORISBB \
  --authenticator externalbrowser \
  -r ACCOUNTADMIN \
  -d CREDIT_DECISIONING_DB \
  -w COMPUTE_WH \
  -q "PUT file://*.csv @CSV_DATA_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;" 2>&1

# If that fails, the error will show. Alternative formats to try:
# Method 2: Just organization name (let browser discover account)
# /Applications/SnowSQL.app/Contents/MacOS/snowsql \
#   -a MZHGUVK \
#   -u BORISBB \
#   --authenticator externalbrowser \
#   -r ACCOUNTADMIN \
#   -d CREDIT_DECISIONING_DB \
#   -w COMPUTE_WH \
#   -q "PUT file://*.csv @CSV_DATA_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"

echo ""
echo "✅ Upload complete! Check Snowflake UI to verify files are in CSV_DATA_STAGE"
