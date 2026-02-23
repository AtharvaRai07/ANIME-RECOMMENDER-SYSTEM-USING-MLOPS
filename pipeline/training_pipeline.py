import sys
from src.data_ingestion import DataIngestion
from src.data_processing import DataProcessor
from src.model_training import ModelTrainer
from config.paths_config import *
from src.logger import logging
from src.exception import CustomException

class TrainingPipeline:
    def __init__(self, config_path):
        self.config_path = config_path

    def run_pipeline(self):

        data_processor = DataProcessor(input_file=ANIMELIST_DATA_PATH, output_dir=PREPROCESSED_DATA_DIR)
        data_processor.run()

        model_trainer = ModelTrainer(config_path=self.config_path)
        model_trainer.train()

if __name__ == "__main__":
    try:
        training_pipeline = TrainingPipeline(config_path=CONFIG_FILE_PATH)
        training_pipeline.run_pipeline()

        logging.info("Training pipeline executed successfully")
    except Exception as e:
        logging.error(f"Error in training pipeline execution: {e}")
        raise CustomException(e, sys)
