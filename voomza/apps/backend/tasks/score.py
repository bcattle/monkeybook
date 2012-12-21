from voomza.apps.backend.settings import *

def photo_score(photo, photos_i_like_ids):
    """
    Calculates the "top photos" ranking score for a photo
    """
    score =\
        PHOTO_COMMENT_POINTS * photo['comment_count'] +\
        PHOTO_LIKE_POINTS * photo['like_count'] +\
        PHOTO_I_LIKE_POINTS * (1 if photo['id'] in photos_i_like_ids else 0)
    return score

def post_score(post):
    score =\
        POST_COMMENT_POINTS * post['comment_count'] +\
        POST_LIKE_POINTS * post['like_count']
    return score

def comment_score(comment):
    score =\
        COMMENT_I_LIKE_POINTS * comment['likes'] +\
        COMMENT_LIKE_POINTS * (1 if comment['user_likes'] else 0)
    return score
