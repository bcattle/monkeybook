from voomza.apps.backend.fql import FQLTask

class BasePhotoResultsTask(FQLTask):
    """
    A task that pulls our standard PHOTO_FIELDS
    """
    depends_on = ['photos_i_like']

    def on_results(self, results, photos_i_like):
        getter = process_photo_results(
            results,
            scoring_fxn=lambda photo: _photo_score(photo, photos_i_like.ids)
        )
        return getter
