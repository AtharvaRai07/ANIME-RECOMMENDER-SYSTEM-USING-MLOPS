import os
import sys
import pandas as pd
from google.cloud import storage
from src.logger import logging
from src.exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml_file

class DataIngestion:
    def __init__(self, config):
        self.config = read_yaml_file(config)
        self.data_ingestion_config = self.config.get("data_ingestion", {})
        self.bucket_name = self.data_ingestion_config.get("bucket_name", "")
        self.bucket_file_names = self.data_ingestion_config.get("bucket_file_names", [])

        os.makedirs(RAW_DATA_DIR, exist_ok=True)

        logging.info(f"Data Ingestion Started with bucket: {self.bucket_name} and files: {self.bucket_file_names}")

    def download_data_from_gcs(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)

            for file_name in self.bucket_file_names:
                destination_path = os.path.join(RAW_DATA_DIR, file_name)

                if file_name == "animelist.csv":
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(destination_path)
                    data = pd.read_csv(destination_path)
                    data.to_csv(destination_path, index=False)

                    logging.info(f"Downloaded and truncated {file_name} to {destination_path}")

                else:
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(destination_path)

                    logging.info(f"Downloaded {file_name} to {destination_path}")

        except Exception as e:
            logging.error(f"Error during data ingestion: {e}")
            raise CustomException(e, sys)


    def initiate_data_ingestion(self):
        try:
            logging.info("Initiating data ingestion process...")
            self.download_data_from_gcs()
            logging.info("Data ingestion process completed successfully.")
        except Exception as e:
            logging.error(f"Data ingestion failed: {e}")
            raise CustomException(e, sys)
        finally:
            logging.info("Data ingestion process finished.")

if __name__ == "__main__":
    try:
        data_ingestion = DataIngestion(config=CONFIG_FILE_PATH)
        data_ingestion.initiate_data_ingestion()
    except Exception as e:
        logging.error(f"Data ingestion failed: {e}")
        raise CustomException(e, sys)
    finally:
        logging.info("Data ingestion script execution finished.")
