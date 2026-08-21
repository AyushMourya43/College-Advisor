import pandas as pd
import psycopg2
import logging

from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer
from config.settings import DATABASE_URL, EMBEDDING_MODEL_NAME
from src import logger

def connect_to_db():
    logging.info("Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    logging.info("Connected successfully")
    return conn
    
def fetch_colleges(conn):
    logging.info("Fetching colleges from database...")
    query = """
        SELECT aishe_code, name, state, district, college_type,
               management, university_name
        FROM colleges;
    """
    df = pd.read_sql(query, conn)
    logging.info(f"Fetched {len(df)} colleges")
    return df

def build_profile_text(row):
    return (
        f"{row['name']} is a {row['college_type']} located in "
        f"{row['district']}, {row['state']}. "
        f"Management: {row['management']}. "
        f"Affiliated to {row['university_name']}."
    )

def generate_and_update_embeddings(df, conn):
    logging.info("Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)  # model ko load kro

    logging.info("Building profile texts...")
    df["profile_text"] = df.apply(build_profile_text, axis=1)

    logging.info("Generating embeddings in batch...")
    embeddings = model.encode(
        df["profile_text"].tolist(),
        batch_size=64,
        show_progress_bar=True
    )

    logging.info("Updating database in batches...")
    cursor = conn.cursor()

    records = [
        (df.iloc[i]["aishe_code"], df.iloc[i]["profile_text"], embeddings[i].tolist())
        for i in range(len(df))
    ]

    update_query = """
        UPDATE colleges AS c
        SET profile_text = data.profile_text,
            embedding = data.embedding::vector
        FROM (VALUES %s) AS data(aishe_code, profile_text, embedding)
        WHERE c.aishe_code = data.aishe_code;
    """

    execute_values(cursor, update_query, records, page_size=500)

    conn.commit()
    cursor.close()
    logging.info(f"Finished updating embeddings for {len(records)} colleges")

if __name__ == "__main__":
    logging.info("Embedding generation pipeline started")
    conn = connect_to_db()
    df = fetch_colleges(conn)
    generate_and_update_embeddings(df, conn)
    conn.close()
    logging.info("Embedding generation pipeline completed")