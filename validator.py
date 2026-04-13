import sqlparse

FORBIDDEN = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]

def validate_sql(query: str):
    query = query.strip()
    query_upper = query.upper()

    if not query_upper.startswith("SELECT"):
        return False, "Only SELECT queries are allowed", None

    parsed = sqlparse.parse(query)
    if not parsed:
        return False, "Invalid SQL syntax", None

    for keyword in FORBIDDEN:
        if f" {keyword} " in f" {query_upper} ":
            return False, f"Forbidden keyword detected: {keyword}", None

    if query_upper.count("JOIN") > 3:
        return False, "Too many JOINs (limit: 3)", None

    if "LIMIT" not in query_upper:
        query = query.rstrip(";") + " LIMIT 100;"

    return True, "", query
