import os
import sys
import pandas as pd
import yaml
from src.logger import logging
from src.exception import CustomException

def read_yaml_file(file_path: str) -> dict:
    try:
        if not os.path.exists(file_path):
            raise CustomException(f"File not found: {file_path}")

        with open(file_path, 'r') as file:
            content = yaml.safe_load(file)
            return content

    except Exception as e:
        raise CustomException(e, sys)

def load_data(file_path: str) -> pd.DataFrame:
    try:
        if not os.path.exists(file_path):
            raise CustomException(f"File not found: {file_path}")

        data = pd.read_csv(file_path)
        return data
    
    except Exception as e:
        raise CustomException(e, sys)
