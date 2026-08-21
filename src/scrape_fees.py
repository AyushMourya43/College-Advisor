import logging
import psycopg2
from psycopg2.extras import execute_batch

from src import logger
from config.settings import DATABASE_URL


def connect_to_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def generate_search_url(name):
    query = name.replace(" ", "+")
    return f"https://www.google.com/search?q={query}+fees+structure+admission"

def get_all_colleges(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT aishe_code, name FROM colleges;")
    rows = cursor.fetchall()
    cursor.close()
    logging.info(f"Fetched {len(rows)} colleges")
    return rows

def update_all_colleges_batch(conn, colleges):
    cursor = conn.cursor()

    data = [
        (generate_search_url(name), aishe_code)
        for aishe_code, name in colleges
    ]

    execute_batch(
        cursor,
        "UPDATE colleges SET reference_search_url = %s WHERE aishe_code = %s;",
        data,
        page_size=1000
    )

    conn.commit()
    cursor.close()

def run_link_generation():
    conn = connect_to_db()
    colleges = get_all_colleges(conn)

    update_all_colleges_batch(conn, colleges)

    conn.close()
    logging.info(f"Done! {len(colleges)} colleges updated with reference links.")

if __name__ == "__main__":
    logging.info("Reference link generation started")
    run_link_generation()
    logging.info("Reference link generation completed")