import pandas as pd
from executor import execute_sql
from validator import validate_sql
from llm import generate_sql, fix_sql


def run_query(question, schema, db_path, auto_fix=True):
    # ---------------- STEP 1: Generate SQL ----------------
    sql = generate_sql(question, schema)

    # ---------------- STEP 2: Validate SQL ----------------
    valid, msg, safe_sql = validate_sql(sql)
    if not valid:
        return {"error": msg}

    sql = safe_sql

    # ---------------- STEP 3: Execute SQL ----------------
    result = execute_sql(db_path, sql)

    # ---------------- STEP 4: Auto-Fix if needed ----------------
    if "error" in result and auto_fix:
        for _ in range(2):  # retry max 2 times
            sql = fix_sql(question, schema, sql, result["error"])

            valid, _, safe_sql = validate_sql(sql)
            if not valid:
                continue

            sql = safe_sql
            result = execute_sql(db_path, sql)

            if "error" not in result:
                break

    # ---------------- STEP 5: Final Error Handling ----------------
    if "error" in result:
        return {"error": result["error"]}

    # ---------------- STEP 6: Convert to DataFrame ----------------
    df = pd.DataFrame(result["rows"], columns=result["columns"])

    # Remove duplicate columns (edge case fix)
    df = df.loc[:, ~df.columns.duplicated()]

    return {
        "df": df,
        "sql": sql
    }