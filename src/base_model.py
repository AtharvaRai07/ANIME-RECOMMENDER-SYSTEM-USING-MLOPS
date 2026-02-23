import os
import sys
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Flatten, Dot, Dense, Activation, BatchNormalization
from utils.common_functions import read_yaml_file
from src.logger import logging
from src.exception import CustomException

class BaseModel:
    def __init__(self, config_path):
        try:
            self.config = config_path
            logging.info(f"BaseModel initialized with configuration from {config_path}")
        except Exception as e:
            logging.error(f"Error initializing BaseModel: {e}")
            raise CustomException(e, sys)

    def RecommenderNet(self, n_users, n_anime):
        try:
            embedding_size = self.config["embedding_size"]

            user = Input(name="user", shape=[1])

            user_embedding = Embedding(name="user_embedding", input_dim=n_users, output_dim=embedding_size)(user)

            anime = Input(name="anime", shape=[1])

            anime_embedding = Embedding(name="anime_embedding", input_dim=n_anime, output_dim=embedding_size)(anime)

            x = Dot(name="dot_product", normalize=True, axes=2)([user_embedding, anime_embedding])

            x = Flatten()(x)

            x = Dense(1, kernel_initializer="he_normal")(x)
            x = BatchNormalization()(x)
            x = Activation("sigmoid")(x)

            model = Model(inputs=[user, anime], outputs=x)
            model.compile(loss=self.config["loss"], metrics=self.config["metrics"], optimizer=self.config["optimizer"])

            logging.info("RecommenderNet model created and compiled successfully")

            return model
        except Exception as e:
            logging.error(f"Error creating RecommenderNet model: {e}")
            raise CustomException(e, sys)

