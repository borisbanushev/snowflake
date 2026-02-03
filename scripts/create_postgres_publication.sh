#!/bin/bash
# ============================================
# Create PostgreSQL Publication for Snowflake Openflow
# ============================================

set -e

echo "======================================================================"
echo "Creating PostgreSQL Publication for CDC"
echo "======================================================================"

# PostgreSQL RDS connection details
PGHOST="snowflake-credit-demo-postgres.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com"
PGPORT="5432"
PGDATABASE="digital_banking"
PGUSER="digitaluser"
PGPASSWORD="DigitalPass123!"

export PGPASSWORD

echo "Connecting to PostgreSQL RDS..."

# Create publication for all tables
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" << 'EOF'

-- Drop publication if it exists
DROP PUBLICATION IF EXISTS snowflake_publication;

-- Create publication for all tables
CREATE PUBLICATION snowflake_publication FOR TABLE
    digital_customer_profile,
    digital_session,
    digital_event,
    digital_kyc_document;

-- Verify publication was created
SELECT * FROM pg_publication WHERE pubname = 'snowflake_publication';

-- Show which tables are in the publication
SELECT schemaname, tablename 
FROM pg_publication_tables 
WHERE pubname = 'snowflake_publication';

EOF

echo ""
echo "======================================================================"
echo "✅ PostgreSQL Publication Created Successfully!"
echo "======================================================================"
echo ""
echo "Publication Name: snowflake_publication"
echo ""
echo "Tables included:"
echo "  - digital_customer_profile"
echo "  - digital_session"
echo "  - digital_event"
echo "  - digital_kyc_document"
echo ""
echo "Next Steps:"
echo "  1. In Snowflake Openflow, set Publication Name to: snowflake_publication"
echo "  2. Apply the parameters"
echo "  3. Enable the PostgreSQL Connection Pool"
echo "  4. Start the connector"
echo ""
