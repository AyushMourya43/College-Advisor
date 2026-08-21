import logging
from src import logger

from src.scrape_colleges import get_download_url, download_and_extract
from src.clean_data import (
    load_raw_data, clean_column_names, clean_website_column,
    handle_missing_values, fix_data_types, remove_duplicates, save_cleaned_data
)
from src.load_to_db import (
    load_cleaned_data, connect_to_db as connect_load_db, insert_colleges
)
from src.generate_embeddings import (
    connect_to_db as connect_embed_db, fetch_colleges, generate_and_update_embeddings
)
from src.scrape_fees import (
    connect_to_db as connect_links_db, run_link_generation
)


def run_pipeline():
    logging.info("===== STEP 1: Scraping AISHE data =====")
    download_url = get_download_url()
    if download_url:
        download_and_extract(download_url)

    logging.info("===== STEP 2: Cleaning data =====")
    df = load_raw_data()
    df = clean_column_names(df)
    df = clean_website_column(df)
    df = handle_missing_values(df)
    df = fix_data_types(df)
    df = remove_duplicates(df)
    save_cleaned_data(df)

    logging.info("===== STEP 3: Loading to database =====")
    df = load_cleaned_data()
    conn = connect_load_db()
    insert_colleges(df, conn)
    conn.close()

    logging.info("===== STEP 4: Generating embeddings =====")
    conn = connect_embed_db()
    df = fetch_colleges(conn)
    generate_and_update_embeddings(df, conn)
    conn.close()

    logging.info("===== STEP 5: Generating reference links =====")
    run_link_generation()

    logging.info("===== Pipeline complete =====")


if __name__ == "__main__":
    run_pipeline()