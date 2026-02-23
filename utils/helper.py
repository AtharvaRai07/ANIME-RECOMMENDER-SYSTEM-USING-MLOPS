import pandas as pd
import numpy as np
import joblib
from config.paths_config import *
from collections import defaultdict, Counter

def _ensure_df(df_or_path):
    if isinstance(df_or_path, pd.DataFrame):
        return df_or_path
    return pd.read_csv(df_or_path)

################## 1. GET_ANIME_FRAME #################

def getAnimeFrame(anime, df_path: str):
    df = _ensure_df(df_path)
    try:
        if isinstance(anime, int):
            return df[df.anime_id == anime]
        if isinstance(anime, str):
            return df[df.eng_version == anime]
    except Exception as e:
        print(f"Error: {e}")

################### 2. GET_ANIME_SYNOPSIS #################

def getSynopsis(anime, df_path: str):
    df = _ensure_df(df_path)
    try:
        if isinstance(anime, int):
            return df[df.MAL_ID == anime].sypnopsis.values[0]
        if isinstance(anime, str):
            return df[df.Name == anime].sypnopsis.values[0]
    except Exception as e:
        print(f"Error: {e}")

#################### 3. CONTENT BASED RECOMMENDATION #################

def find_similar_animes(name, anime_weights_path, anime2anime_encoded_path, anime2anime_decoded_path, anime_df_path, synopsis_df_path, top_n = 10, return_dists = False, neg = False):
    try:
        anime_id = getAnimeFrame(name, anime_df_path).anime_id.values[0]
        encoded_anime_id = joblib.load(anime2anime_encoded_path).get(anime_id, None)

        weights = joblib.load(anime_weights_path)

        dists = np.dot(weights, weights[encoded_anime_id])
        sorted_dist = np.argsort(dists)

        if neg:
            closest_animes = sorted_dist[:top_n]
        else:
            closest_animes = sorted_dist[-(top_n + 1):]

        print(f"Top {top_n} similar animes to '{name}':")

        if return_dists:
            return dists, closest_animes

        similar_animes = []

        for closest in closest_animes:
            decoded_anime_id = joblib.load(anime2anime_decoded_path).get(closest, None)
            synopsis = getSynopsis(decoded_anime_id, synopsis_df_path)
            anime_frame = getAnimeFrame(decoded_anime_id, anime_df_path)
            anime_name = anime_frame.eng_version.values[0]
            genre = anime_frame.Genres.values[0]

            similar_animes.append({
                "anime_id": decoded_anime_id,
                "anime_name": anime_name,
                "genre": genre,
                "synopsis": synopsis,
                "similarity": dists[closest]
            })

        similar_animes_df =  pd.DataFrame(similar_animes).sort_values(by='similarity', ascending=False)
        similar_animes_df = similar_animes_df[similar_animes_df.anime_id != anime_id].reset_index(drop=True)
        return similar_animes_df
    except Exception as e:
        print(f"Error: {e}")

#################### 4. USER BASED RECOMMENDATION #################

def find_similar_users(item_input, user_weights_path, user2user_encoded_path, user2user_decoded_path, top_n = 10, return_dists = False, neg = False):
    user_id = item_input
    encoded_user_id = joblib.load(user2user_encoded_path).get(user_id)
    print(type(encoded_user_id), encoded_user_id)

    weights = joblib.load(user_weights_path)

    dists = np.dot(weights, weights[encoded_user_id])
    sorted_dist = np.argsort(dists)
    if neg:
        closest_users = sorted_dist[:top_n]
    else:
        closest_users = sorted_dist[-(top_n + 1):]

    if return_dists:
        return dists, closest_users

    print(f"Top {top_n} similar users to '{user_id}':")

    similar_users = []

    for closest in closest_users:
        decoded_user_id = joblib.load(user2user_decoded_path).get(closest, None)
        similar_users.append({
            "user_id": decoded_user_id,
            "similarity": dists[closest]
        })

    similar_users_df = pd.DataFrame(similar_users).sort_values(by="similarity", ascending=False)
    similar_users_df = similar_users_df[similar_users_df.user_id != user_id].reset_index(drop=True)
    return similar_users_df

##################### 5. GET_USER_PREFERENCES ######################

def getUserPreferences(user_id, rating_df_path, df_path, plot = False):
    rating_df = _ensure_df(rating_df_path)
    df = _ensure_df(df_path)

    animes_watched_by_user = rating_df[rating_df.user_id == user_id]

    user_rating_percentile = np.percentile(animes_watched_by_user.rating, 75)

    anime_greater_than_percentile = animes_watched_by_user[animes_watched_by_user.rating >= user_rating_percentile]

    top_watched_anime_by_user = anime_greater_than_percentile.sort_values(by='rating', ascending = False).anime_id.values

    anime_df_rows = df[df.anime_id.isin(top_watched_anime_by_user)]
    anime_df_rows  = anime_df_rows[["anime_id", "eng_version", "Genres"]]

    return anime_df_rows

###################### 6. GET_USER_RECOMMENDATION ######################

def getUserRecommendation(similar_users, user_preferences, df_path, rating_df_path, synopsis_df_path, top_n = 10):
    recommendation_anime = []
    anime_pool = []

    df = _ensure_df(df_path)
    rating_df = _ensure_df(rating_df_path)
    synopsis_df = _ensure_df(synopsis_df_path)

    watched_anime = set(user_preferences.eng_version.values)

    for user_id in similar_users.user_id:

        pref_df = getUserPreferences(user_id, rating_df, df, plot = False)

        if pref_df.empty:
            continue

        pref_df = pref_df[~pref_df.eng_version.isin(watched_anime)]

        anime_pool.extend(pref_df.eng_version.values)

    if not anime_pool:
        return pd.DataFrame()

    top_animes = Counter(anime_pool).most_common(top_n)

    for anime_name, count in top_animes:

        frame = getAnimeFrame(anime_name, df)

        if frame.empty:
            continue

        anime_id = frame.anime_id.values[0]
        genre = frame.Genres.values[0]

        recommendation_anime.append({
            "anime_name": anime_name,
            "genre": genre,

            "number_of_similar_users_preferred": count
        })

    recommendation_anime_df = pd.DataFrame(recommendation_anime)
    return recommendation_anime_df
