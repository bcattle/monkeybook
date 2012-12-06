import logging
from backend.api import BackendFacebookUserConverter

logger = logging.getLogger(__name__)


class BaseYearbookPipeline(object):
    """
    The pipeline to assemble a yearbook for one user

    These steps run in order,
    adding processed results to `self.results`
    """
    def __init__(self, user):
        self._user = user
        self._graph = self._user.profile.get_offline_graph()
        self._facebook = BackendFacebookUserConverter(self._graph)

    def run(self):
        bundle = {}
        for step in self.steps:
            the_step = getattr(self, step)
            the_step(bundle)

    def save(self):
        """
        Saves the pipeline to db
        """
        pass


PHOTO_COMMENT_POINTS    = 1     # How many points does it get for each comment on it?
PHOTO_LIKE_POINTS       = 1     # How many points does it get for each like on it?
PHOTO_I_LIKE_POINTS     = 2     # How many points does it get if I like it?

GROUP_PHOTO_IS = 4          # How many people are in a group photo?

class YearbookPipeline(BaseYearbookPipeline):
    steps = (
        'get_all_photos_user_is_in',
        'get_all_group_shots',
        'get_photos_with_family',
        'get_photos_with_gfbf'
    )

    _photos_i_like = None

    def _photo_score(self, photo):
        """
        Calculates the score for a photo
        """
        score =\
            PHOTO_COMMENT_POINTS * photo['comments_count'] +\
            PHOTO_LIKE_POINTS * photo['likes_count'] +\
            PHOTO_I_LIKE_POINTS * (1 if photo['id'] in self._photos_i_like else 0)
        return score

    def get_all_photos_user_is_in(self, bundle):
        pass

    def get_all_group_shots(self, bundle):
        pass

    def get_photos_with_family(self, bundle):
        pass

    def get_photos_family_alone(self, bundle):
        pass

    def get_photos_with_gfbf(self, bundle):
        pass

    def get_photos_gfbf_alone(self, bundle):
        pass

    def get_top_photos_of_year(self, bundle):
        pass

    def get_top_photos_of_first_half(self, bundle):
        pass

    def get_top_photos_of_second_half(self, bundle):
        pass

    def get_photos_back_in_time(self, bundle):
        pass

    def get_group_photos_back_in_time(self, bundle):
        pass

    def get_top_albums(self, bundle):
        # Albums you are tagged in the most,
        # photos in that album in points order
        pass

    def get_top_friends(self, bundle):
        pass

