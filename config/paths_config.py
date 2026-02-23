import os

##################################### DATA INGESTION ######################################

RAW_DATA_DIR = "artifacts/raw_data"
CONFIG_FILE_PATH = "config/config.yaml"

#################################### DATA PREPROCESSING ######################################

PREPROCESSED_DATA_DIR = "artifacts/preprocessed_data"
ANIMELIST_DATA_PATH = os.path.join(RAW_DATA_DIR, "animelist.csv")
ANIME_DATA_PATH = os.path.join(RAW_DATA_DIR, "anime.csv")
SYNOPSIS_DATA_PATH = os.path.join(RAW_DATA_DIR, "anime_with_synopsis.csv")

X_TRAIN_ARRAY = os.path.join(PREPROCESSED_DATA_DIR, "X_train_array.pkl")
X_TEST_ARRAY = os.path.join(PREPROCESSED_DATA_DIR, "X_test_array.pkl")
Y_TRAIN = os.path.join(PREPROCESSED_DATA_DIR, "y_train.pkl")
Y_TEST = os.path.join(PREPROCESSED_DATA_DIR, "y_test.pkl")

RATING_DF = os.path.join(PREPROCESSED_DATA_DIR, "rating_df.csv")
ANIME_DF = os.path.join(PREPROCESSED_DATA_DIR, "anime_df.csv")
SYNOPSIS_DF = os.path.join(PREPROCESSED_DATA_DIR, "synopsis_df.csv")

USER2USER_ENCODED = os.path.join(PREPROCESSED_DATA_DIR, "user2user_encoded.pkl")
USER2USER_DECODED = os.path.join(PREPROCESSED_DATA_DIR, "user2user_decoded.pkl")

ANIME2ANIME_ENCODED = os.path.join(PREPROCESSED_DATA_DIR, "anime2anime_encoded.pkl")
ANIME2ANIME_DECODED = os.path.join(PREPROCESSED_DATA_DIR, "anime2anime_decoded.pkl")

#################################### MODEL TRAINING ######################################
MODEL_DIR = "artifacts/model"
CHECKPOINT_DIR = os.path.join("artifacts","model_checkpoints", "weights.weights.h5")
WEIGHTS_DIR = os.path.join("artifacts", "weights")
MODEL_PATH = os.path.join(MODEL_DIR, "recommender_model.keras")
ANIME_WEIGHTS_PATH = os.path.join(WEIGHTS_DIR, "anime_weights.h5")
USER_WEIGHTS_PATH = os.path.join(WEIGHTS_DIR, "user_weights.h5")
