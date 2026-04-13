import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"


# ---------------- LLM CALL ----------------
def call_llm(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0}
        }
    )
    return response.json()["response"]


# ---------------- EXTRACT COLUMNS ----------------
def extract_columns(schema: str):
    match = re.findall(r"Columns:\s*(.*)", schema)
    if match:
        return [c.strip() for c in match[0].split(",")]
    return []


# ---------------- SAFE COLUMN QUOTING ----------------
def quote_columns(sql: str, schema: str) -> str:
    columns = extract_columns(schema)

    # remove backticks
    sql = sql.replace("`", "")

    for col in columns:
        if " " in col or col.isdigit():
            pattern = rf'\b{re.escape(col)}\b'
            sql = re.sub(pattern, f'"{col}"', sql)

    return sql


# ---------------- CLEAN SQL ----------------
def clean_sql(response: str, schema: str) -> str:

    # extract SQL block
    block = re.search(r"```sql(.*?)```", response, re.DOTALL | re.IGNORECASE)
    if block:
        response = block.group(1)

    # extract SELECT query
    match = re.search(r"(SELECT .*?;)", response, re.IGNORECASE | re.DOTALL)
    sql = match.group(1) if match else response.strip()

    # safe quoting
    sql = quote_columns(sql, schema)

    # remove bad patterns
    sql = re.sub(
        r"WHERE\s+year\s*=\s*\(SELECT.*?\)",
        "",
        sql,
        flags=re.IGNORECASE | re.DOTALL
    )

    # clean spacing safely
    sql = re.sub(r"\s{2,}", " ", sql)

    if not sql.endswith(";"):
        sql += ";"

    return sql.strip()


# ---------------- INTENT DETECTION ----------------
def detect_intent(question: str):
    q = question.lower()

    if any(k in q for k in ["highest", "most", "top", "best", "max"]):
        if "per" in q:
            return "top_per_group"
        return "global_top"

    return "default"


# ---------------- QUESTION ENHANCEMENT ----------------
def enhance_question(question: str) -> str:
    q = question.lower()

    if "month" in q:
        question += " (use strftime('%m', Date))"

    if "year" in q:
        question += " (use strftime('%Y', Date))"

    return question


# ---------------- SQL GENERATION ----------------
def generate_sql(question: str, schema: str) -> str:

    question = enhance_question(question)
    intent = detect_intent(question)

    prompt = f"""
You are a senior SQLite expert.

Think step-by-step internally, but DO NOT output explanation.

STRICT RULES:
- Output ONLY SQL
- Must start with SELECT
- Use ONLY schema columns EXACTLY as given
- Use SQLite syntax ONLY
- Do NOT invent columns

----------------------
COLUMN RULE
----------------------
- Use column names EXACTLY as given
- Use double quotes ONLY if column contains spaces

----------------------
AGGREGATION RULE
----------------------
- Use GROUP BY correctly
- Use AVG, SUM, COUNT appropriately

----------------------
ANALYTICAL REASONING RULE (CRITICAL)
----------------------
Interpret the question carefully:

1. If the query asks for:
   - highest / lowest / most / top / best
   AND includes grouping like:
   - per year, per region, per category

Then:
- You MUST return exactly ONE row per group
- First compute the metric per group (e.g., AVG, SUM)
- Then select the best value within each group

IMPORTANT:
- GROUP BY alone is NOT sufficient
- You MUST use a method that ensures one result per group:
    • window function (RANK, ROW_NUMBER)
    OR
    • subquery filtering

2. If only a global comparison:
- Use ORDER BY + LIMIT

3. Never return multiple rows per group when question implies "most per group"

----------------------
INTENT
----------------------
{intent}

----------------------
SCHEMA
----------------------
{schema}

----------------------
QUESTION
----------------------
{question}

----------------------
SQL
----------------------
"""

    response = call_llm(prompt)
    return clean_sql(response, schema)


# ---------------- SQL FIX ----------------
def fix_sql(question, schema, bad_sql, error):

    intent = detect_intent(question)

    prompt = f"""
You are a SQL expert fixing a broken query.

ERROR:
{error}

BAD SQL:
{bad_sql}

STRICT RULES:
- Output ONLY SQL
- Use SQLite syntax ONLY
- Use EXACT column names from schema
- Fix aggregation and grouping issues
- Ensure correctness of grouping logic

CRITICAL:
- If question implies "top per group", ensure ONLY ONE row per group is returned
- Use ranking or filtering logic if necessary

INTENT:
{intent}

SCHEMA:
{schema}

QUESTION:
{question}

FIXED SQL:
"""

    response = call_llm(prompt)
    return clean_sql(response, schema)


# ---------------- INSIGHTS ----------------
def generate_insights(question, df):
    prompt = f"""
Provide 3 short insights.

Data:
{df.head(10).to_dict()}
"""
    return call_llm(prompt)


# ---------------- CHART ----------------
def choose_chart(question, df):
    numeric = df.select_dtypes(include="number").columns
    categorical = df.select_dtypes(exclude="number").columns

    if len(numeric) > 0 and len(categorical) > 0:
        return "bar", categorical[0], numeric[0]

    if len(numeric) >= 2:
        return "line", numeric[0], numeric[1]

    return None, None, None

# ---------------- DYNAMIC SUGGESTIONS ----------------
def generate_suggestions(schema_chunks):
    schema_text = "\n".join(schema_chunks)

    prompt = f"""
You are a data analyst.

Based on this schema, generate 3 simple business questions.

Rules:
- Keep short
- No SQL terms
- Generic & useful

Schema:
{schema_text}

Output:
- Question 1
- Question 2
- Question 3
"""

    try:
        response = call_llm(prompt)
        suggestions = [
            line.replace("-", "").strip()
            for line in response.split("\n")
            if line.strip()
        ]
        return suggestions[:3]

    except:
        return [
            "Show top categories",
            "Average values by group",
            "Trend over time"
        ]