# GenAI Features You Can Add Next

You already have: **Cortex Search** (policy), **Cortex Agent** (Snowsight), **Streamlit chat** (analyst-style Q&A), and **EXPLAIN_DECISION** (SQL function). Here are concrete next features, roughly by impact and effort.

---

## 1. **ML decision explanation in the UI** (high impact, low effort)

**What:** When a credit officer views an application, show a “Why did the ML model recommend this?” section that uses your existing `EXPLAIN_DECISION` function.

**Where:** AI Credit Agent page – e.g. under the Decision Assistance Report or next to the chat.

**How:** Call `EXPLAIN_DECISION(customer_id, score_band, credit_rating, decision, default_prob, customer_data)` with data from `ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS` and `GET_CUSTOMER_DATA`, then display the returned text.

**Value:** Makes ML decisions transparent and explainable without leaving the app.

---

## 2. **Policy Q&A in Streamlit** (high impact, medium effort)

**What:** A “Ask about policy” input: user types a question (e.g. “What is our DTI limit for personal loans?”) and sees relevant policy snippets.

**How:** Cortex Search is queried via `SEARCH_PREVIEW`, which in SQL requires a constant query. So either:
- **Option A:** Add a **stored procedure** that takes the user query, builds the search JSON (with escaped query), executes `SEARCH_PREVIEW` via dynamic SQL, and returns results; Streamlit calls that procedure.
- **Option B:** A dropdown of **predefined policy questions**; each option runs a fixed `SEARCH_PREVIEW` query and shows results in the app.

**Value:** Policy lookup without leaving the app or opening Snowsight.

---

## 3. **Conversation memory / follow-up** (medium impact, low effort)

**What:** Keep the last 1–2 turns of the analyst chat and send them to the LLM so the user can ask “Why?” or “What if we offer 60 months?” and get a contextual answer.

**How:** Store `(user, assistant)` pairs in `st.session_state` and pass the last N as a conversation history array to `CORTEX.COMPLETE` (or equivalent) when the user sends a new message.

**Value:** More natural, multi-turn analyst conversation.

---

## 4. **Customer / relationship summary** (medium impact, low effort)

**What:** A short “Relationship summary” or “One-line summary” for the selected customer (e.g. “Long-standing customer, low DTI, 2 active loans; ideal for upsell.”).

**How:** Call your existing UDFs to get customer + credit + transaction snapshot, then pass a short blob to `CORTEX.COMPLETE` or `CORTEX.SUMMARIZE` with a prompt like “Summarize this customer profile in 2–3 sentences for a relationship manager.”

**Value:** Quick context for the officer before diving into the full analysis.

---

## 5. **Batch explanations** (medium impact, medium effort)

**What:** On a portfolio or queue view, a button “Explain last N decisions” that runs `EXPLAIN_DECISION` for the last N applications and shows results in a table or expandable rows.

**How:** Query `ML_PREDICTIONS.CREDIT_SCORE_PREDICTIONS` (and customer data) for N rows, loop in Python or via a Snowpark UDF, call `EXPLAIN_DECISION` for each, and display in a DataFrame or table.

**Value:** Explainability at portfolio level for audits or reviews.

---

## 6. **Natural language to SQL (Cortex Analyst)** (high impact, higher effort)

**What:** User asks in plain English (“How many applications did we approve last month by product?”) and the app runs generated SQL and shows a chart or table.

**How:** Create a **semantic model** over your key tables/views, then use Cortex Analyst (or equivalent) to turn the question into SQL and execute it. Streamlit would call the appropriate API and render results.

**Value:** Self-serve analytics for non-SQL users.

---

## Suggested order

1. **ML decision explanation in the UI** – use what you already have (`EXPLAIN_DECISION`).
2. **Policy Q&A** – start with Option B (predefined questions); add Option A (dynamic procedure) if you need free-form policy search.
3. **Conversation memory** – small change to the existing chat.
4. **Customer summary** – one extra LLM call and a small UI block.

If you tell me which one you want first (e.g. “add ML explanation” or “add policy search”), I can outline the exact code changes in your repo.
