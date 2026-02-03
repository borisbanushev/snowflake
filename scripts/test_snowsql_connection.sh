#!/bin/bash
# Test SnowSQL connection with different account formats

export SNOWSQL_PWD="L@lolo87Snowflake"

echo "Testing SnowSQL connection..."
echo "Username: ACCOUNTADMIN"
echo "Password: (set via SNOWSQL_PWD)"
echo ""

# Try different account formats
echo "1. Trying account format: MZHGUVK-BC67154"
/Applications/SnowSQL.app/Contents/MacOS/snowsql \
  -a MZHGUVK-BC67154 \
  -u ACCOUNTADMIN \
  -q "SELECT CURRENT_USER(), CURRENT_ACCOUNT();" 2>&1 | head -20

echo ""
echo "---"
echo ""

echo "2. Trying account format: mzhguvk-bc67154 (lowercase)"
/Applications/SnowSQL.app/Contents/MacOS/snowsql \
  -a mzhguvk-bc67154 \
  -u ACCOUNTADMIN \
  -q "SELECT CURRENT_USER(), CURRENT_ACCOUNT();" 2>&1 | head -20

echo ""
echo "---"
echo ""

echo "3. Trying account format: mzhguvk.bc67154 (dot notation)"
/Applications/SnowSQL.app/Contents/MacOS/snowsql \
  -a mzhguvk.bc67154 \
  -u ACCOUNTADMIN \
  -q "SELECT CURRENT_USER(), CURRENT_ACCOUNT();" 2>&1 | head -20

echo ""
echo "If one of these works, use that account format for the upload!"
