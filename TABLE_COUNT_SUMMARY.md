# 📊 Complete Table Count - Snowflake Catalog

## Total Tables in Data Pipeline

**Grand Total: 49 tables** across all layers

---

## 🔢 Breakdown by Layer

### ⭐ Layer 1: External Sources (RAW_ZONE) - **14 tables**

#### Oracle T24 (via Openflow CDC) - **6 tables**
1. T24_CUSTOMER
2. T24_ACCOUNT
3. T24_LOAN
4. T24_TRANSACTION
5. T24_PAYMENT_SCHEDULE
6. T24_COLLATERAL

#### MySQL Digital Banking (via Openflow CDC) - **4 tables**
7. DIGITAL_CUSTOMER_PROFILE
8. DIGITAL_SESSION
9. DIGITAL_EVENT
10. DIGITAL_KYC_DOCUMENT

#### Databricks Credit Bureau (via Polaris) - **4 tables**
11. CREDIT_BUREAU_REPORT
12. INCOME_VERIFICATION
13. ALTERNATIVE_DATA
14. FRAUD_INDICATORS

**External Sources Subtotal: 14 tables**

---

### 🔄 Layer 2: Transformations (CURATED_ZONE) - **17 tables**

#### CUSTOMERS Schema - **3 tables**
15. DIM_CUSTOMER
16. DIM_CUSTOMER_DEMOGRAPHICS
17. DIM_CUSTOMER_KYC

#### ACCOUNTS Schema - **3 tables**
18. DIM_ACCOUNT
19. FACT_ACCOUNT_BALANCES
20. BRIDGE_CUSTOMER_ACCOUNT

#### LOANS Schema - **4 tables**
21. DIM_LOAN
22. FACT_LOANS
23. FACT_PAYMENT_SCHEDULE
24. DIM_COLLATERAL

#### TRANSACTIONS Schema - **3 tables**
25. FACT_TRANSACTIONS
26. FACT_DIGITAL_EVENTS
27. AGG_TRANSACTION_SUMMARY

#### CREDIT_BUREAU Schema - **4 tables**
28. DIM_CREDIT_REPORT
29. DIM_INCOME_VERIFICATION
30. FACT_ALTERNATIVE_DATA
31. FACT_FRAUD_INDICATORS

**Transformations Subtotal: 17 tables**

---

### 🎯 Layer 3: Analytics (ANALYTICS_ZONE) - **15 tables**

#### CUSTOMER_360 Schema - **4 tables**
32. CUSTOMER_360_UNIFIED
33. CUSTOMER_FINANCIAL_SUMMARY
34. CUSTOMER_DIGITAL_BEHAVIOR
35. CUSTOMER_RISK_PROFILE

#### CREDIT_SCORING Schema - **3 tables**
36. ML_FEATURE_STORE
37. ML_MODEL_PREDICTIONS
38. CREDIT_SCORE_HISTORY

#### RISK_ANALYTICS Schema - **4 tables**
39. PORTFOLIO_SUMMARY
40. DELINQUENCY_COHORTS
41. RISK_SEGMENTS
42. EARLY_WARNING_ALERTS

#### REPORTING Schema - **4 tables**
43. RPT_DAILY_DASHBOARD
44. RPT_LOAN_PERFORMANCE
45. RPT_CUSTOMER_ACQUISITION
46. RPT_REGULATORY_COMPLIANCE

**Analytics Subtotal: 15 tables**

---

### 🖥️ Application Layer (APP_ZONE) - **3 tables**

#### TRANSACTIONAL Schema (Hybrid Tables) - **3 tables**
47. CREDIT_APPLICATIONS
48. CREDIT_DECISIONS
49. AGENT_SESSIONS

**Application Subtotal: 3 tables**

---

## 📈 Summary Table

| Layer | Schema Count | Table Count | Row Count (Est.) | Purpose |
|-------|--------------|-------------|------------------|---------|
| **External Sources** | 3 | **14** | 58M+ | Raw data from external systems |
| **Transformations** | 5 | **17** | 2M+ | Cleaned, validated, enriched |
| **Analytics** | 4 | **15** | 500K+ | Business-ready analytics |
| **Application** | 1 | **3** | 50K+ | OLTP for applications |
| **TOTAL** | **13** | **49** | **60M+** | Complete data platform |

---

## 🎯 Core Data Lineage Count

**Main Pipeline (External → Transformations → Analytics):**
- **46 tables** (14 + 17 + 15)

**With Application Layer:**
- **49 tables** (46 + 3)

---

## 📊 Visual Breakdown

```
                    TABLE COUNT BY LAYER
                    ═══════════════════════
                    
External Sources    ████████████████ 14 tables (29%)
(RAW_ZONE)          Oracle: 6, MySQL: 4, Databricks: 4

Transformations     ████████████████████ 17 tables (35%)
(CURATED_ZONE)      5 subject areas

Analytics           ████████████████ 15 tables (31%)
(ANALYTICS_ZONE)    4 business domains

Application         ████ 3 tables (6%)
(APP_ZONE)          Hybrid OLTP tables

                    ─────────────────────────────────
                    TOTAL: 49 tables
```

---

## 🔗 Data Flow Counts

### From External to Analytics

**Oracle Path:**
```
6 Oracle tables → 8 Curated tables → 10 Analytics tables
```

**MySQL Path:**
```
4 MySQL tables → 6 Curated tables → 8 Analytics tables
```

**Databricks Path:**
```
4 Databricks tables → 4 Curated tables → 12 Analytics tables
```

**Note:** Analytics tables often join multiple sources, so the counts overlap.

---

## 📋 Additional Objects (Not Counted Above)

These support the main pipeline but aren't in the core lineage:

### ML_ZONE
- Model registry tables
- Training data tables
- Inference logs

### GOVERNANCE
- Tag definitions (metadata)
- Masking policies (metadata)
- Audit views (system tables)

### Dynamic Tables
- Real-time materialized views
- Incremental pipelines

### Views
- 20+ views on top of base tables
- Secure views for data access
- Materialized views for performance

---

## 🎓 Table Type Distribution

| Type | Count | Purpose |
|------|-------|---------|
| **External Tables** | 14 | Connected to external sources |
| **Dimension Tables (DIM_*)** | 7 | Master data, slowly changing |
| **Fact Tables (FACT_*)** | 8 | Transactional, metrics |
| **Aggregate Tables (AGG_*)** | 1 | Pre-computed summaries |
| **Bridge Tables (BRIDGE_*)** | 1 | Many-to-many relationships |
| **Report Tables (RPT_*)** | 4 | Business reports |
| **ML Tables (ML_*)** | 2 | Machine learning |
| **Unified Views (*_360, *_SUMMARY)** | 9 | Consolidated business views |
| **Hybrid Tables** | 3 | OLTP workloads |

**Total: 49 tables**

---

## 🚀 Expected Growth

### Phase 1 (Launch): 49 tables
- Core pipeline operational
- All 3 sources connected
- Basic analytics

### Phase 2 (3 months): ~70 tables
- Additional reporting tables
- More ML feature tables
- Historical snapshots

### Phase 3 (6 months): ~100 tables
- Advanced analytics
- Additional data sources
- Product-specific views

### Steady State (1 year): ~150 tables
- Mature data platform
- Multiple business domains
- Full self-service analytics

---

## 📊 Query to Count All Tables

```sql
-- Count tables by layer
SELECT 
    CASE 
        WHEN table_schema LIKE '%_SRC' THEN 'External Sources'
        WHEN table_schema IN ('CUSTOMERS','ACCOUNTS','LOANS','TRANSACTIONS','CREDIT_BUREAU') 
            THEN 'Transformations'
        WHEN table_schema IN ('CUSTOMER_360','CREDIT_SCORING','RISK_ANALYTICS','REPORTING') 
            THEN 'Analytics'
        WHEN table_schema = 'TRANSACTIONAL' THEN 'Application'
        ELSE 'Other'
    END as layer,
    table_schema,
    COUNT(*) as table_count
FROM CREDIT_DECISIONING_DB.INFORMATION_SCHEMA.TABLES
WHERE table_schema != 'INFORMATION_SCHEMA'
GROUP BY layer, table_schema
ORDER BY 
    CASE layer
        WHEN 'External Sources' THEN 1
        WHEN 'Transformations' THEN 2
        WHEN 'Analytics' THEN 3
        WHEN 'Application' THEN 4
        ELSE 5
    END,
    table_schema;
```

**Expected Output:**
```
LAYER                 | SCHEMA          | TABLE_COUNT
----------------------|-----------------|-------------
External Sources      | DATABRICKS_SRC  | 4
External Sources      | MYSQL_SRC       | 4
External Sources      | ORACLE_T24_SRC  | 6
Transformations       | ACCOUNTS        | 3
Transformations       | CREDIT_BUREAU   | 4
Transformations       | CUSTOMERS       | 3
Transformations       | LOANS           | 4
Transformations       | TRANSACTIONS    | 3
Analytics             | CREDIT_SCORING  | 3
Analytics             | CUSTOMER_360    | 4
Analytics             | REPORTING       | 4
Analytics             | RISK_ANALYTICS  | 4
Application           | TRANSACTIONAL   | 3
                                        --------
                      TOTAL             | 49
```

---

## ✅ Summary

### By Category:
- **14 External Source tables** (3 systems)
- **17 Transformation tables** (5 subject areas)
- **15 Analytics tables** (4 business domains)
- **3 Application tables** (1 OLTP schema)

### **Grand Total: 49 tables**

### Table-to-Source Ratio:
- **3.5x transformation** (49 tables from 14 sources)
- Demonstrates rich data enrichment and analytics

### Coverage:
- ✅ All 3 external sources represented
- ✅ Complete medallion architecture (Bronze → Silver → Gold)
- ✅ Business-ready analytics layer
- ✅ Application layer for OLTP

This is a **comprehensive yet manageable** data platform - large enough for enterprise needs, small enough to understand and maintain! 🎯
