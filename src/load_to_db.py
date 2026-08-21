import pandas as pd
import psycopg2
import logging

from psycopg2.extras import execute_values
from config.settings import PROCESSED_DATA_DIR, DATABASE_URL
from src import logger


def load_cleaned_data():

    logging.info("Loading cleaned data...")

    file_path = PROCESSED_DATA_DIR / "colleges_cleaned.csv"

    df = pd.read_csv(file_path)

    logging.info(f"Loaded {len(df)} rows")

    return df


def connect_to_db():

    logging.info("Connecting to database...")

    conn = psycopg2.connect(DATABASE_URL)

    logging.info("Connected successfully")

    return conn


def insert_colleges(df, conn):

    cursor = conn.cursor()

    query = """
        INSERT INTO colleges (
            aishe_code,
            name,
            state,
            district,
            website,
            year_of_establishment,
            location,
            college_type,
            management,
            university_aishe_code,
            university_name,
            university_type
        )
        VALUES %s
        ON CONFLICT (aishe_code) DO NOTHING;
    """

    records = []

    for _, row in df.iterrows():

        year = row["Year_Of_Establishment"]
        
        if pd.notna(year):
           year = int(year)
        else:
           year = None

        records.append((
            row["Aishe_Code"],
            row["Name"],
            row["State"],
            row["District"],
            row["Website"],
            year,
            row["Location"],
            row["College_Type"],
            row["Management"],
            row["University_Aishe_Code"],
            row["University_Name"],
            row["University_Type"]
        ))

    execute_values(cursor, query, records, page_size=1000)

    conn.commit()

    cursor.close()

    logging.info(f"Inserted {len(records)} rows")


if __name__ == "__main__":

    logging.info("Load pipeline started")

    df = load_cleaned_data()

    conn = connect_to_db()

    insert_colleges(df, conn)

    conn.close()

    logging.info("Load pipeline completed")