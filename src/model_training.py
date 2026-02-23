import joblib
import numpy as np
import comet_ml
import os
import sys
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, LearningRateScheduler
from src.base_model import BaseModel
from src.logger import logging
from src.exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml_file

class ModelTrainer:
    def __init__(self, config_path):
        self.config_path = read_yaml_file(config_path)
        self.config_path = self.config_path["model_training"]
        self.experiment = comet_ml.Experiment(api_key="CaLMe9hKJaq7t5kvfUD02gDT6", project_name="recommender_system", workspace="atharvarai07")

        os.makedirs(MODEL_DIR, exist_ok=True)
        os.makedirs(WEIGHTS_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(CHECKPOINT_DIR), exist_ok=True)

    def load_data(self):
        try:
            X_train_array = joblib.load(X_TRAIN_ARRAY)
            X_test_array = joblib.load(X_TEST_ARRAY)
            y_train = joblib.load(Y_TRAIN)
            y_test = joblib.load(Y_TEST)

            logging.info("Data loaded successfully for model training")

            return X_train_array, X_test_array, y_train, y_test
        except Exception as e:
            logging.error(f"Error loading data for model training: {e}")
            raise CustomException(e, sys)


    def train_model(self, X_train_array, X_test_array, y_train, y_test):
        try:
            # Use max id + 1 to avoid out-of-range indices from sparse ids.
            n_users = int(max(np.max(X_train_array[0]), np.max(X_test_array[0]))) + 1
            n_anime = int(max(np.max(X_train_array[1]), np.max(X_test_array[1]))) + 1

            base_model = BaseModel(config_path=self.config_path)

            model = base_model.RecommenderNet(n_users=n_users, n_anime=n_anime)
            start_learing_rate = self.config_path['start_learning_rate']
            min_lr = self.config_path['min_learning_rate']
            max_lr = self.config_path['max_learning_rate']

            batch_size = self.config_path['batch_size']

            ramup_epochs = self.config_path['ramup_epochs']
            sustain_epochs = self.config_path['sustain_epochs']
            exp_decay = self.config_path['exp_decay']

            def lrfn(epoch):
                if epoch < ramup_epochs:
                    lr = (max_lr - start_learing_rate) / ramup_epochs * epoch + start_learing_rate
                elif epoch < ramup_epochs + sustain_epochs:
                    lr = max_lr
                else:
                    lr = (max_lr - min_lr) * exp_decay**(epoch - ramup_epochs - sustain_epochs) + min_lr
                return lr

            lr_callback = LearningRateScheduler(lambda epoch: lrfn(epoch), verbose=0)

            model_checkpoint = ModelCheckpoint(filepath=CHECKPOINT_DIR, save_weights_only=True, monitor='val_loss', mode='min', save_best_only=True)

            early_stopping = EarlyStopping(monitor='val_loss', patience=1, restore_best_weights=True, mode='min')

            my_callbacks = [lr_callback, model_checkpoint, early_stopping]

            history = model.fit(
                x = X_train_array,
                y = y_train,
                batch_size=batch_size,
                epochs=self.config_path['epochs'],
                validation_data=(X_test_array, y_test),
                verbose=self.config_path['verbose'],
                callbacks=my_callbacks
            )

            for epoch in range(len(history.history['loss'])):
                self.experiment.log_metric("loss", history.history['loss'][epoch], step=epoch)
                self.experiment.log_metric("val_loss", history.history['val_loss'][epoch], step=epoch)


            logging.info("Model trained successfully")
            return model
        except Exception as e:
            logging.error(f"Error during model training: {e}")
            raise CustomException(e, sys)

    def extract_weights(self, layer_name, model):
        try:
            weights = model.get_layer(layer_name).get_weights()[0]
            weights = weights / np.linalg.norm(weights, axis=1, keepdims=True)

            logging.info("Extracting and saving user and anime weights")
            return weights
        except Exception as e:
            logging.error(f"Error extracting weights: {e}")
            raise CustomException(e, sys)

    def save_model_and_weights(self, model):
        try:
            model.save(MODEL_PATH)
            logging.info("Model saved successfully")

            user_weights = self.extract_weights(layer_name=self.config_path["model_training"]["user_layer_name"], model=model)
            anime_weights = self.extract_weights(layer_name=self.config_path["model_training"]["anime_layer_name"], model=model)

            joblib.dump(user_weights, USER_WEIGHTS_PATH)
            joblib.dump(anime_weights, ANIME_WEIGHTS_PATH)

            self.experiment.log_asset(MODEL_PATH)
            self.experiment.log_asset(USER_WEIGHTS_PATH)
            self.experiment.log_asset(ANIME_WEIGHTS_PATH)

            logging.info(f"User and anime weights saved successfully. User weights: {USER_WEIGHTS_PATH}, Anime weights: {ANIME_WEIGHTS_PATH}")
        except Exception as e:
            logging.error(f"Error saving model: {e}")
            raise CustomException(e, sys)

    def train(self):
        try:
            X_train_array, X_test_array, y_train, y_test = self.load_data()
            model = self.train_model(X_train_array, X_test_array, y_train, y_test)
            model.load_weights(CHECKPOINT_DIR)
            self.save_model_and_weights(model)
            logging.info("Model training process completed successfully")

        except Exception as e:
            logging.error(f"Error in the model training process: {e}")
            raise CustomException(e, sys)

if __name__ == "__main__":
    try:
        model_trainer = ModelTrainer(config_path=CONFIG_FILE_PATH)
        model_trainer.train()
        logging.info("Model training execution completed successfully")
    except Exception as e:
        logging.error(f"Error in model training execution: {e}")
        raise CustomException(e, sys)
