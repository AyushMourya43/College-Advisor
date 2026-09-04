import logging
import requests
import zipfile
import io 

from src import logger
from config.settings import (
    AIKOSH_API_KEY,
    AIKOSH_API_BASE_URL,
    AIKOSH_DATASET_ID,
    AIKOSH_VERSION,
    RAW_DATA_DIR,
)


def get_download_url():

    logging.info("Fetching download URL from AIKosh...")

    try:

        params = {
            "datasetIdentifier": AIKOSH_DATASET_ID,
            "versionNumber": AIKOSH_VERSION,
        }

        headers = {
            "access-key": AIKOSH_API_KEY,
        }

        response = requests.get(
            AIKOSH_API_BASE_URL,
            params=params,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        download_url = data["data"]["downloadUrl"]

        logging.info("Download URL fetched successfully.")

        return download_url

    except requests.exceptions.HTTPError as error:

        if response.status_code in [401, 403]:   # key expired or invalid
            logging.error(
                "AIKosh API key expired or invalid. "
                "Generate a new key and update .env"
            )
        else:
            logging.error(f"AIKosh API HTTP error: {error}")

    except requests.exceptions.Timeout:

        logging.error("AIKosh API request timed out.")

    except requests.exceptions.ConnectionError:

        logging.error("Internet connection error.")

    except requests.exceptions.RequestException as error:

        logging.error(f"AIKosh API request failed: {error}")

    return None


def download_and_extract(download_url):

    logging.info("Downloading AIKosh dataset...")

    try:

        response = requests.get(download_url, timeout=300)

        response.raise_for_status()

        RAW_DATA_DIR.mkdir( parents=True,exist_ok=True )

        with zipfile.ZipFile( io.BytesIO(response.content) ) as zip_file:

            zip_file.extractall(RAW_DATA_DIR)

            files = zip_file.namelist()

        logging.info(f"Dataset extracted successfully: {files}")

        print("Extracted files:")

        for file in files:
            print(file)

    except requests.exceptions.HTTPError as error:

        logging.error(
            f"Download URL expired or download failed: {error}"
        )

    except requests.exceptions.Timeout:

        logging.error("Dataset download timed out.")

    except requests.exceptions.ConnectionError:

        logging.error("Internet connection error.")

    except zipfile.BadZipFile:

        logging.error("Downloaded file is not a valid ZIP file.")

    except requests.exceptions.RequestException as error:

        logging.error(f"Dataset download failed: {error}")


if __name__ == "__main__":

    logging.info("College Advisor scraping started.")

    download_url = get_download_url() 

    if download_url:  # agr kuch milta h toh ye kro 
        download_and_extract(download_url)

    logging.info("College Advisor scraping completed.")