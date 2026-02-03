#!/usr/bin/env python3
"""
Create PostgreSQL Publication for Snowflake Openflow CDC
"""

import psycopg2

# PostgreSQL RDS connection details
POSTGRES_HOST = "snowflake-credit-demo-postgres.c7yg0uyimv09.ap-southeast-1.rds.amazonaws.com"
POSTGRES_PORT = 5432
POSTGRES_DATABASE = "digital_banking"
POSTGRES_USER = "digitaluser"
POSTGRES_PASSWORD = "DigitalPass123!"

print("=" * 70)
print("Creating PostgreSQL Publication for Snowflake Openflow")
print("=" * 70)
print()

try:
    # Connect to PostgreSQL
    print(f"Connecting to PostgreSQL RDS...")
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DATABASE,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    conn.autocommit = True
    cursor = conn.cursor()
    print("✅ Connected successfully")
    print()
    
    # Drop existing publication if it exists
    print("Dropping existing publication (if any)...")
    try:
        cursor.execute("DROP PUBLICATION IF EXISTS snowflake_publication;")
        print("✅ Existing publication dropped")
    except Exception as e:
        print(f"⚠️  No existing publication to drop: {e}")
    print()
    
    # Create publication for all tables
    print("Creating publication for all tables...")
    cursor.execute("""
        CREATE PUBLICATION snowflake_publication FOR TABLE
            digital_customer_profile,
            digital_session,
            digital_event,
            digital_kyc_document;
    """)
    print("✅ Publication 'snowflake_publication' created successfully")
    print()
    
    # Verify publication was created
    print("Verifying publication...")
    cursor.execute("SELECT pubname FROM pg_publication WHERE pubname = 'snowflake_publication';")
    result = cursor.fetchone()
    if result:
        print(f"✅ Publication verified: {result[0]}")
    print()
    
    # Show which tables are in the publication
    print("Tables included in publication:")
    cursor.execute("""
        SELECT schemaname, tablename 
        FROM pg_publication_tables 
        WHERE pubname = 'snowflake_publication'
        ORDER BY tablename;
    """)
    tables = cursor.fetchall()
    for schema, table in tables:
        print(f"  ✓ {schema}.{table}")
    print()
    
    cursor.close()
    conn.close()
    
    print("=" * 70)
    print("🎉 PostgreSQL Publication Setup Complete!")
    print("=" * 70)
    print()
    print("Publication Name: snowflake_publication")
    print()
    print("Next Steps in Snowflake Openflow:")
    print("  1. Set 'Publication Name' to: snowflake_publication")
    print("  2. Click 'Apply' to save parameters")
    print("  3. Enable the 'PostgreSQL Connection Pool' controller service")
    print("  4. Start the connector")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Troubleshooting:")
    print("  - Check PostgreSQL RDS is accessible")
    print("  - Verify credentials are correct")
    print("  - Ensure database 'digital_banking' exists")
    exit(1)
