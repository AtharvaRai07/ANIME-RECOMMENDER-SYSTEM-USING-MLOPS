import pandas as pd
from config.paths_config import *
from utils.helper import *

def hybrid_recommendation(user_id, user_weight=0.5, content_weight=0.5):

    # ---------- USER BASED ----------
    similar_users = find_similar_users(
        user_id, USER_WEIGHTS_PATH, USER2USER_ENCODED, USER2USER_DECODED, top_n=10
    )

    user_pref = getUserPreferences(user_id, RATING_DF, ANIME_DF)

    user_recommended_anime = getUserRecommendation(
        similar_users, user_pref, ANIME_DF, RATING_DF, SYNOPSIS_DF
    )

    user_recommended_anime_lst = user_recommended_anime.anime_name.to_list()

    # ---------- CONTENT BASED ----------
    content_recommended_anime_lst = []

    for anime in user_recommended_anime_lst:

        similar_anime = find_similar_animes(
            anime,
            ANIME_WEIGHTS_PATH,
            ANIME2ANIME_ENCODED,
            ANIME2ANIME_DECODED,
            ANIME_DF,
            SYNOPSIS_DF,
            top_n=10
        )

        if similar_anime is not None and not similar_anime.empty:
            content_recommended_anime_lst.extend(
                similar_anime.anime_name.to_list()
            )

    # ---------- COMBINE SCORES ----------
    combined_scores = {}

    for anime in user_recommended_anime_lst:
        combined_scores[anime] = combined_scores.get(anime, 0) + user_weight

    for anime in content_recommended_anime_lst:
        combined_scores[anime] = combined_scores.get(anime, 0) + content_weight

    # ---------- SORT ----------
    sorted_animes = sorted(
        combined_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    anime_lst = [anime for anime, score in sorted_animes[:10]]

    # ---------- BUILD DETAILED RESPONSE ----------
    recommendations = []
    anime_df = pd.read_csv(ANIME_DF)
    synopsis_df = pd.read_csv(SYNOPSIS_DF)

    for anime_name in anime_lst:
        anime_frame = getAnimeFrame(anime_name, anime_df)
        if anime_frame is not None and not anime_frame.empty:
            anime_id = anime_frame.anime_id.values[0]
            genre = anime_frame.Genres.values[0] if pd.notna(anime_frame.Genres.values[0]) else "Various Genres"
            synopsis = getSynopsis(anime_name, synopsis_df)
            mal_rating = anime_frame.Score.values[0]
            if pd.isna(mal_rating):
                mal_rating = None

            recommendations.append({
                "anime_id": anime_id,
                "anime_name": anime_name,
                "genre": genre,
                "synopsis": synopsis if synopsis else "No synopsis available",
                "mal_rating": mal_rating
            })

    return recommendations
