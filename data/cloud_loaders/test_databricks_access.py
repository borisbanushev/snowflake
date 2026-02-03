#!/usr/bin/env python3
"""
Test Databricks access and find available catalogs
"""

from databricks import sql
from databricks.sdk import WorkspaceClient
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

DATABRICKS_HOST = os.getenv('DATABRICKS_HOST', '').replace('https://', '')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN', '')

print("=" * 70)
print("Databricks Access Test")
print("=" * 70)
print(f"Host: {DATABRICKS_HOST}")
print()

# Get SQL warehouse
w = WorkspaceClient(host=f"https://{DATABRICKS_HOST}", token=DATABRICKS_TOKEN)
warehouses = list(w.warehouses.list())

if not warehouses:
    print("❌ No SQL warehouses found")
    exit(1)

http_path = warehouses[0].odbc_params.path
print(f"✅ Using warehouse: {warehouses[0].name}")
print(f"   Path: {http_path}")
print()

# Connect
connection = sql.connect(
    server_hostname=DATABRICKS_HOST,
    http_path=http_path,
    access_token=DATABRICKS_TOKEN
)

cursor = connection.cursor()

# Show catalogs
print("📚 Available Catalogs:")
print("-" * 70)
cursor.execute("SHOW CATALOGS")
catalogs = cursor.fetchall()

for catalog in catalogs:
    catalog_name = catalog[0]
    print(f"  - {catalog_name}")
    
    try:
        # Try to show schemas
        cursor.execute(f"SHOW SCHEMAS IN {catalog_name}")
        schemas = cursor.fetchall()
        print(f"    Schemas: {[s[0] for s in schemas[:5]]}")
        
        # Try to use catalog
        cursor.execute(f"USE CATALOG {catalog_name}")
        print(f"    ✅ Can USE this catalog")
        
    except Exception as e:
        print(f"    ⚠️  Limited access: {str(e)[:50]}")
    print()

# Recommend catalog
print("=" * 70)
print("Recommendation:")
print("=" * 70)

# Try to find best catalog
for catalog in catalogs:
    catalog_name = catalog[0]
    try:
        cursor.execute(f"USE CATALOG {catalog_name}")
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS test_schema")
        cursor.execute(f"DROP SCHEMA IF EXISTS test_schema")
        print(f"✅ Use catalog: {catalog_name}")
        print(f"   This catalog has full permissions")
        break
    except:
        continue
else:
    print("⚠️  No catalog with CREATE permissions found")
    print("   You may need to:")
    print("   1. Create a new catalog, or")
    print("   2. Request permissions on existing catalog")

cursor.close()
connection.close()
