from llm import generate_sql
from validator import validate_sql
from executor import execute_sql
from rag import extract_schema_chunks, build_embeddings, retrieve_relevant_schema

DB_PATH = "db.sqlite"

# 🔥 Build schema embeddings ONCE
print("Building schema embeddings...")
schema_chunks = extract_schema_chunks(DB_PATH)
schema_embeddings = build_embeddings(schema_chunks)
print("Ready!\n")


def text_to_sql_pipeline(question: str):
    # 🔍 Step 1: Retrieve relevant schema
    relevant_chunks = retrieve_relevant_schema(
        question,
        schema_chunks,
        schema_embeddings,
        top_k=2
    )

    schema = "\n".join(relevant_chunks)

    print("\nRelevant Schema:\n", schema)

    # 🤖 Step 2: Generate SQL
    sql_query = generate_sql(question, schema)

    print("\nGenerated SQL:\n", sql_query)

    # 🛡️ Step 3: Validate
    if not validate_sql(sql_query):
        return {"error": "Invalid or unsafe SQL query"}

    # 🗄️ Step 4: Execute
    result = execute_sql(DB_PATH, sql_query)

    return {
        "query": sql_query,
        "result": result
    }


if __name__ == "__main__":
    while True:
        question = input("\nAsk: ")
        output = text_to_sql_pipeline(question)
        print("\nOutput:\n", output)
