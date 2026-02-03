# 📤 Manual CSV Upload Guide - Snowflake Web UI

Since CLI upload isn't working with SAML/SSO, here's how to upload files manually via the Snowflake Web UI.

---

## 🎯 Step-by-Step: Upload CSV Files to Stage

### Step 1: Navigate to Your Stage

**Option A: Via Top Navigation**
1. In Snowflake UI, click **"Data"** in the top navigation bar
2. Click **"Databases"** 
3. Click on **`CREDIT_DECISIONING_DB`**
4. Look for tabs: **"Database Details"**, **"Schemas"**, **"Stages"**
5. Click the **"Stages"** tab
6. Click on **`CSV_DATA_STAGE`**

**Option B: Via SQL (If you can't find Stages tab)**
1. Open a SQL worksheet
2. Run: `SHOW STAGES IN DATABASE CREDIT_DECISIONING_DB;`
3. Click on `CSV_DATA_STAGE` from the results

---

### Step 2: Upload Files

1. Once you're viewing `CSV_DATA_STAGE`, look for:
   - **"+ Files"** button, OR
   - **"Upload"** button, OR
   - **"Add Files"** button

2. Click the upload button

3. **Select ALL 19 CSV files** from:
   ```
   /Users/boris/Desktop/snowflake/data/generated_csv/
   ```

4. **Files to upload:**
   - `digital_customer_profile.csv`
   - `digital_session.csv`
   - `digital_event.csv`
   - `digital_kyc_document.csv`
   - `t24_customer.csv`
   - `t24_account.csv`
   - `t24_loan.csv`
   - `t24_transaction.csv`
   - `t24_payment_schedule.csv`
   - `t24_collateral.csv`
   - `credit_score.csv`
   - `credit_inquiry.csv`
   - `tradeline.csv`
   - `public_record.csv`
   - `country_code.csv`
   - `currency_code.csv`
   - `product_catalog.csv`
   - `branch_directory.csv`
   - `relationship_manager.csv`

5. Click **"Upload"** or **"Open"** (depending on your browser)

6. Wait for upload to complete (you'll see progress/status)

---

### Step 3: Verify Files Are Uploaded

**Option A: In the UI**
- After upload, you should see all 19 files listed in the `CSV_DATA_STAGE` view
- Each file should show its size and upload timestamp

**Option B: Via SQL**
Run this in a SQL worksheet:
```sql
USE DATABASE CREDIT_DECISIONING_DB;
LIST @CSV_DATA_STAGE;
```

You should see all 19 CSV files listed.

---

### Step 4: Load Data into Tables

Once files are uploaded, run the load script:

1. Open a SQL worksheet in Snowflake
2. Open the file: `snowflake/02_direct_load/04_load_all_data.sql`
3. Copy and paste the entire script into the worksheet
4. Run it (click "Run" or press Ctrl+Enter / Cmd+Enter)

This will:
- Truncate all tables
- Load data from the CSV files into tables
- Show row counts for validation

---

## 🔍 Troubleshooting

### Can't Find "Stages" Tab?

1. **Try SQL method:**
   ```sql
   USE DATABASE CREDIT_DECISIONING_DB;
   SHOW STAGES;
   ```
   Then click on `CSV_DATA_STAGE` from results

2. **Check if stage exists:**
   ```sql
   SELECT * FROM TABLE(INFORMATION_SCHEMA.STAGES)
   WHERE STAGE_SCHEMA = 'PUBLIC' OR STAGE_DATABASE = 'CREDIT_DECISIONING_DB';
   ```

### Upload Button Not Visible?

- Make sure you have `USAGE` privilege on the stage
- Try refreshing the page
- Check if you're using the correct role (`ACCOUNTADMIN`)

### Files Not Showing After Upload?

- Wait a few seconds and refresh
- Check the stage via SQL: `LIST @CSV_DATA_STAGE;`
- Verify file names match exactly (case-sensitive)

---

## ✅ Quick Checklist

- [ ] Navigated to `CREDIT_DECISIONING_DB` → `CSV_DATA_STAGE`
- [ ] Clicked upload button
- [ ] Selected all 19 CSV files
- [ ] Files uploaded successfully
- [ ] Verified files in stage (via UI or `LIST @CSV_DATA_STAGE`)
- [ ] Ran `04_load_all_data.sql` to load data into tables
- [ ] Verified row counts match expected values

---

## 📋 Expected Row Counts (After Loading)

After running `04_load_all_data.sql`, you should see:

- `DIGITAL_CUSTOMER_PROFILE`: ~3,000 rows
- `DIGITAL_SESSION`: ~15,000 rows
- `DIGITAL_EVENT`: ~60,000 rows
- `DIGITAL_KYC_DOCUMENT`: ~3,000 rows
- `T24_CUSTOMER`: ~3,000 rows
- `T24_ACCOUNT`: ~5,400 rows
- `T24_LOAN`: ~1,200 rows
- `T24_TRANSACTION`: ~30,000 rows
- `T24_PAYMENT_SCHEDULE`: ~15,000 rows
- `T24_COLLATERAL`: ~921 rows
- `CREDIT_SCORE`: ~3,000 rows
- `CREDIT_INQUIRY`: ~12,000 rows
- `TRADELINE`: ~18,000 rows
- `PUBLIC_RECORD`: ~300 rows
- Plus reference data tables

**Total: ~170,341 records**

---

## 🎉 You're Done!

Once files are uploaded and data is loaded, you can proceed with your analysis!
