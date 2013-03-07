from __future__ import division, print_function, unicode_literals
import logging, urllib, cStringIO
from celery import task
from django.core.files.storage import default_storage
from voomza.lib.django_facebook.api import FacebookUserConverter
from voomza.apps.viral.settings import *
from PIL import Image

logger = logging.getLogger(__name__)


@task.task(ignore_result=True)
def accept_invite_requests(invite_requests):
    """
    Send a request to facebook to DELETE the request,
    and update the entry in our db
    """
    for invite_request in invite_requests:
        accepting_user = invite_request.to_facebook_user.profile.user
        graph = accepting_user.profile.get_offline_graph()
        facebook = FacebookUserConverter(graph)
        # Delete the request
        facebook.delete_request(invite_request)
        logger.info('Invite request deleted')


@task.task()
def make_story_image(photo_instance, background_index=0):
    """
    Creates an open graph image by compositing a
    user's photo into a pre-existing frame,
    and shrinking the image.

    The result is saved to S3, and the url of the new image is returned

    :param photo_instance:   The FacebookPhoto instance of a user's image
    :return:                 The url to the newly-created image
    """
    # Load user's image
    user_photo_file = read_image_from_url(photo_url)
    user_img = Image.open(file)

    # Load the backround image and frame image from default_storage
    if user_img is square:
        user_img_aspect = 'square'
    elif user_img is portrait:
        user_img_aspect = 'portrait'
    else:
        user_img_aspect = 'landscape'

    background_image_path   = STORY_IMAGE_BACKGROUNDS[background_index][user_img_aspect]
    frame_image_path        = STORY_IMAGE_FRAMES[user_img_aspect]

    # default_storage.open(background_image_path).read()
    # default_storage.open(frame_image_path).read()


@task.task()
def read_image_from_url(url):
    return cStringIO.StringIO(urllib.urlopen(url).read())

