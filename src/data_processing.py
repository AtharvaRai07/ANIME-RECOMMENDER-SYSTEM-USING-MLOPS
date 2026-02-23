import os
import sys
import pandas as pd
import joblib
import numpy as np
from src.logger import logging
from src.exception import CustomException
from config.paths_config import *

class DataProcessor:
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir

        self.rating_df = None
        self.anime_df = None
        self.synopsis_df = None
        self.X_train_array = None
        self.X_test_array = None
        self.y_train = None
        self.y_test = None

        self.user2user_encoded = {}
        self.anime2anime_encoded =  {}
        self.user2user_decoded =  {}
        self.anime2anime_decoded =  {}

        os.makedirs(self.output_dir, exist_ok=True)
        logging.info(f"DataProcessor initialized with input file: {self.input_file} and output directory: {self.output_dir}")

    def load_data(self, usecols):
        try:
            self.rating_df = pd.read_csv(self.input_file, low_memory=True, usecols=usecols)

            logging.info(f"Data loaded successfully from {self.input_file} with columns: {usecols}")

        except Exception as e:
            logging.error(f"Error loading data: {e}")
            raise CustomException(e, sys)

    def filter_users(self, min_ratings=400):
        try:
            n_ratings = self.rating_df["user_id"].value_counts()
            self.rating_df = self.rating_df[self.rating_df["user_id"].isin(n_ratings[n_ratings >= min_ratings].index)]

            logging.info(f"Filtered users with at least {min_ratings} ratings. Remaining users: {self.rating_df['user_id'].nunique()}")

        except Exception as e:
            raise CustomException(e, sys)

    def scale_ratings(self):
        try:
            min_rating = self.rating_df["rating"].min()
            max_rating = self.rating_df["rating"].max()

            self.rating_df["rating"] = self.rating_df["rating"].apply(lambda x: (x - min_rating) / (max_rating - min_rating))

            logging.info(f"Ratings scaled to range [0, 1]. Original min: {min_rating}, Original max: {max_rating}")

        except Exception as e:
            raise CustomException(e, sys)

    def encode_data(self):
        try:
            ### Users Encoding
            user_ids = self.rating_df["user_id"].unique().tolist()
            self.user2user_encoded = {x: i for i, x in enumerate(user_ids)}
            self.user2user_decoded = {i: x for i, x in enumerate(user_ids)}
            self.rating_df["user_encoded"] = self.rating_df["user_id"].map(self.user2user_encoded)

            ### Anime Encoding
            anime_ids = self.rating_df["anime_id"].unique().tolist()
            self.anime2anime_encoded = {x: i for i, x in enumerate(anime_ids)}
            self.anime2anime_decoded = {i: x for i, x in enumerate(anime_ids)}
            self.rating_df["anime_decoded"] = self.rating_df["anime_id"].map(self.anime2anime_decoded)

            logging.info(f"Data encoding completed. Unique users: {len(user_ids)}, Unique anime: {len(anime_ids)}")

        except Exception as e:
            raise CustomException(e, sys)

    def split_data(self, test_size=0.2, random_state=42):
        try:
            self.rating_df = self.rating_df.sample(frac=1, random_state=random_state).reset_index(drop=True)

            X = self.rating_df[["user_encoded", "anime_decoded"]].values
            y = self.rating_df["rating"].values

            train_indices = int(self.rating_df.shape[0] * (1 - test_size))

            X_train, X_test, y_train, y_test = (
                X[:train_indices],
                X[train_indices:],
                y[:train_indices],
                y[train_indices:]
            )

            self.X_train_array = [X_train[:, 0], X_train[:, 1]]
            self.X_test_array = [X_test[:, 0], X_test[:, 1]]
            self.y_train = y_train
            self.y_test = y_test

            logging.info(f"Data split into train and test sets. Train size: {len(X_train)}, Test size: {len(X_test)}")

        except Exception as e:
            raise CustomException(e, sys)

    def save_preprocessed_data(self):
        try:
            artifacts = {
                "user2user_encoded": self.user2user_encoded,
                "anime2anime_encoded": self.anime2anime_encoded,
                "user2user_decoded": self.user2user_decoded,
                "anime2anime_decoded": self.anime2anime_decoded,
            }

            for name, data in artifacts.items():
                joblib.dump(data, os.path.join(self.output_dir, f"{name}.pkl"))

            logging.info(f"Preprocessed data saved successfully in {self.output_dir}")

            joblib.dump(self.X_train_array, X_TRAIN_ARRAY)
            joblib.dump(self.X_test_array, X_TEST_ARRAY)
            joblib.dump(self.y_train, Y_TRAIN)
            joblib.dump(self.y_test, Y_TEST)

            self.rating_df.to_csv(RATING_DF, index=False)

            logging.info(f"Train and test arrays saved successfully. X_train: {X_TRAIN_ARRAY}, X_test: {X_TEST_ARRAY}, y_train: {Y_TRAIN}, y_test: {Y_TEST}")
        except Exception as e:
            raise CustomException(e, sys)

    def process_anime_data(self):
        try:
            self.anime_df = pd.read_csv(ANIME_DATA_PATH, low_memory=True)
            self.synopsis_df = pd.read_csv(SYNOPSIS_DATA_PATH, low_memory=True)

            cols = ["anime_id", "eng_version", "Score", "Genres", "Episodes", "Type", "Members", "Premiered"]

            self.anime_df = df = self.anime_df.replace("Unknown", np.nan)

            def getAnimeName(anime_id):
                try:
                    name = self.anime_df[self.anime_df.MAL_ID == anime_id].eng_version.values[0]
                    if pd.isna(name):
                        name = self.anime_df[self.anime_df.MAL_ID == anime_id].Name.values[0]
                    return name
                except Exception as e:
                    logging.error(f"Error fetching anime name for ID {anime_id}: {e}")
                    return CustomException(e, sys)

            self.anime_df["anime_id"] = self.anime_df["MAL_ID"]
            self.anime_df["eng_version"] = self.anime_df["English name"]
            self.anime_df['eng_version'] = self.anime_df['anime_id'].apply(lambda x: getAnimeName(x))

            self.anime_df.sort_values(by="Score", ascending=False, na_position="last",inplace=True)

            self.anime_df = self.anime_df[cols]

            self.anime_df.to_csv(ANIME_DF, index=False)
            self.synopsis_df.to_csv(SYNOPSIS_DF, index=False)

            logging.info(f"Anime data processed and saved successfully. Anime data path: {ANIME_DF}, Synopsis data path: {SYNOPSIS_DF}")

        except Exception as e:
            raise CustomException(e, sys)

    def run(self):
        try:
            self.load_data(["user_id", "anime_id", "rating"])
            self.filter_users()
            self.scale_ratings()
            self.encode_data()
            self.split_data()
            self.save_preprocessed_data()
            self.process_anime_data()

            logging.info("Data processing completed successfully.")
        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    try:
        data_processor = DataProcessor(input_file=ANIMELIST_DATA_PATH, output_dir=PREPROCESSED_DATA_DIR)
        data_processor.run()
    except Exception as e:
        logging.error(f"Error in data processing: {e}")




