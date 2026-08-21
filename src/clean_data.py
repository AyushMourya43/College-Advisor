import pandas as pd
import re
import logging
from pathlib import Path

from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src import logger


def load_raw_data():

    logging.info("Loading raw data...")

    file_path = RAW_DATA_DIR / "All Colleges AISHE Dashboard.xlsx"

    df = pd.read_excel(file_path)

    logging.info(f"Loaded {len(df)} rows")

    return df


def clean_column_names(df):

    df = df.rename(columns={
        "Aishe Code": "Aishe_Code",
        "Manegement": "Management",
        "Year Of Establishment": "Year_Of_Establishment",
        "College Type": "College_Type",
        "University Aishe Code": "University_Aishe_Code",
        "University Name": "University_Name",
        "University Type": "University_Type"
    })

    return df


def clean_website_column(df):

    def extract_url(value):

        if pd.isna(value):
            return None

        match = re.search(r'\((https?://[^\)]+)\)', str(value))

        if match:
            return match.group(1)

        return str(value)

    df["Website"] = df["Website"].apply(extract_url)

    return df


def handle_missing_values(df):

    df["Website"] = df["Website"].fillna("Not Available")

    df["University_Aishe_Code"] = df["University_Aishe_Code"].fillna("Standalone")

    return df


def fix_data_types(df):

    df["Year_Of_Establishment"] = pd.to_numeric(df["Year_Of_Establishment"],
        errors="coerce"
    ).astype("Int64")

    return df


def remove_duplicates(df):

    before = len(df)

    df = df.drop_duplicates( subset="Aishe_Code" )

    after = len(df)

    logging.info( f"Removed {before - after} duplicate rows" )

    return df


def save_cleaned_data(df):

    PROCESSED_DATA_DIR.mkdir( parents=True,exist_ok=True)

    output_path = PROCESSED_DATA_DIR / "colleges_cleaned.csv"

    df.to_csv( output_path,index=False )

    logging.info( f"Saved {len(df)} cleaned rows")


if __name__ == "__main__":

    logging.info("Cleaning pipeline started.")

    df = load_raw_data()

    df = clean_column_names(df)

    df = clean_website_column(df)

    df = handle_missing_values(df)

    df = fix_data_types(df)

    df = remove_duplicates(df)

    save_cleaned_data(df)

    logging.info("Cleaning pipeline completed.")

    