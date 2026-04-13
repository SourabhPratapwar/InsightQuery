from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

model = SentenceTransformer("all-MiniLM-L6-v2")


def extract_schema_chunks(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    chunks = []

    for table in tables:
        table_name = table[0]

        columns = cursor.execute(
            f"PRAGMA table_info({table_name});"
        ).fetchall()

        col_names = [col[1] for col in columns]

        text = f"""
Table: {table_name}
Columns: {', '.join(col_names)}
"""
        chunks.append(text.strip())

    conn.close()
    return chunks


def detect_relationships(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    relations = []

    for table in tables:
        table_name = table[0]
        fk = cursor.execute(
            f"PRAGMA foreign_key_list({table_name});"
        ).fetchall()

        for rel in fk:
            relations.append(
                f"{table_name}.{rel[3]} -> {rel[2]}.{rel[4]}"
            )

    conn.close()
    return "\n".join(relations)


def build_embeddings(chunks):
    return model.encode(chunks)


def retrieve_relevant_schema(question, chunks, embeddings, top_k=None):
    q_embedding = model.encode([question])
    scores = cosine_similarity(q_embedding, embeddings)[0]

    ranked = sorted(
        list(zip(chunks, scores)),
        key=lambda x: x[1],
        reverse=True
    )

    if top_k is None or top_k >= len(ranked):
        return [item[0] for item in ranked]

    return [item[0] for item in ranked[:top_k]]
