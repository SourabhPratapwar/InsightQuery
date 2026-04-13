import sqlite3
import pandas as pd
import tempfile
from rag import extract_schema_chunks, build_embeddings, detect_relationships


def excel_to_db(file):
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    conn = sqlite3.connect(temp_db.name)

    sheets = pd.read_excel(file, sheet_name=None)
    for name, df in sheets.items():
        df.to_sql(name, conn, index=False, if_exists="replace")

    conn.close()
    return temp_db.name


def load_schema(db_path):
    chunks = extract_schema_chunks(db_path)
    relationships = detect_relationships(db_path)
    embeddings = build_embeddings(chunks)
    return chunks, embeddings, relationships
