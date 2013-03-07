from voomza.apps.yearbook2012.settings import *

def album_photo_score(photo):
    """
    Calculates the "top photos" ranking score for a photo
    """
    score = \
        ALBUM_POINTS_FOR_COMMENT * photo['comment_count'] + \
        ALBUM_POINTS_FOR_LIKE * photo['like_count']
    return score
