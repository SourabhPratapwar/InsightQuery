import sqlite3

def execute_sql(db_path: str, query: str):
    try:
        with sqlite3.connect(db_path, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute(query)

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(1000)

            return {
                "columns": columns,
                "rows": rows
            }

    except Exception as e:
        return {"error": str(e)}
