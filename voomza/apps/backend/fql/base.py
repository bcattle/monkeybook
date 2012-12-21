from voomza.apps.backend.fql import FQLTask
from voomza.apps.backend.getter import process_photo_results

class BasePhotoResultsTask(FQLTask):
    """
    A task that pulls our standard PHOTO_FIELDS
    """
    def on_results(self, results, photos_i_like):
        getter = process_photo_results(
            results,
        )
        return getter
