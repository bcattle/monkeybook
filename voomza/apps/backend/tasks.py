from celery import task, group, chain
from voomza.apps.backend.api import BackendFacebookUserConverter
from voomza.apps.backend.models import FacebookPhoto
from voomza.apps.backend.settings import *


def _photo_score(photo, photos_i_like_ids):
    """
    Calculates the "top photos" ranking score for a photo
    """
    score = \
        PHOTO_COMMENT_POINTS * photo['comment_count'] +\
        PHOTO_LIKE_POINTS * photo['like_count'] +\
        PHOTO_I_LIKE_POINTS * (1 if photo['id'] in photos_i_like_ids else 0)
    return score


@task.task()
def get_photos_i_like(bundle):
    facebook = bundle['facebook']
    bundle['photos_i_like_ids'] = facebook.get_all_photos_i_like().ids
    return bundle


@task.task()
def get_all_photos_user_is_in(bundle):
    facebook = bundle['facebook']
    user_all_photos = facebook.get_all_photos_i_am_in(scoring_fxn=_photo_score)
    bundle['user_all_photos'] = user_all_photos
    # Save the photos to the db
    # for simplicity, do this now whether we use or not
    FacebookPhoto.objects.from_fb_response(user_all_photos)
    return bundle


@task.task()
def get_all_group_shots(bundle):
    facebook = bundle['facebook']
    # Get all tags of all photos the user is in
    # collapse on object_id, and take the ones over GROUP_PHOTO_IS
    photo_tag_counts = facebook.get_other_tags_of_photos_im_in()
    bundle['user_all_group_photo_ids'] = filter(
        lambda x: x['count'] >= 4,
        photo_tag_counts.fields_ordered_by('count')
    )
    return bundle


def _get_photos_of_user(facebook, user_id, my_photo_ids):
    """
    Returns all photos of a user, split into
    the ones you're in, and the ones you aren't
    """
    photos_of_user = facebook.get_photos_by_user_id(user_id, scoring_fxn=_photo_score)
    both_of_us = photos_of_user | my_photo_ids
    just_them = photos_of_user - my_photo_ids
    return both_of_us, just_them


@task.task()
def get_photos_family(bundle):
    facebook = bundle['facebook']
    user = bundle['user']
    user_all_photo_ids = bundle['user_all_photos'].ids

    # For each family member, get the photos we're in
    # and the photos just they are in
    for fam_member in user.family:
        both_of_us, just_them = _get_photos_of_user(facebook, fam_member.facebook_id,
                                                    my_photo_ids=user_all_photo_ids)
        # pull these photos here?
        pass
    return bundle


@task.task()
def get_photos_gfbf(bundle):
    facebook = bundle['facebook']
    user = bundle['user']
    user_all_photo_ids = bundle['user_all_photos'].ids

    # Get the photos we're in and the photos just they are in
    both_of_us, just_them = _get_photos_of_user(facebook, user.significant_other_id,
                                                my_photo_ids=user_all_photo_ids)
    # pull these photos here?
    pass
    return bundle


@task.task()
def get_top_photos_of_year(bundle):
    facebook = bundle['facebook']
    # Sort the in-memory list in top photos order
    return bundle
#    print 'in get_top_photos_of_year - args: %s, kwargs: %s' % (str(args), str(kwargs))
#    return 'get_top_photos_of_year'



@task.task()
def get_top_photos_of_first_half(bundle):
    facebook = bundle['facebook']
    # Sort the list by date, if needed
    # Filter by time of year
    # Sort by score
    return bundle
#    print 'in get_top_photos_of_first_half - args: %s, kwargs: %s' % (str(args), str(kwargs))
#    return 'get_top_photos_of_first_half'


@task.task()
def get_top_photos_of_second_half(bundle):
    facebook = bundle['facebook']
    # Sort the list by date, if needed
    # Filter by time of year
    # Sort by score
    return bundle
#    print 'in get_top_photos_of_second_half - args: %s, kwargs: %s' % (str(args), str(kwargs))
#    return 'get_top_photos_of_second_half'


@task.task()
def get_photos_back_in_time(bundle):
    facebook = bundle['facebook']
    return bundle
#    print 'in get_group_photos_back_in_time - args: %s, kwargs: %s' % (str(args), str(kwargs))
#    return 'get_photos_back_in_time'


@task.task()
def get_group_photos_back_in_time(bundle):
    facebook = bundle['facebook']
    return bundle
#    print 'in get_group_photos_back_in_time - args: %s, kwargs: %s' % (str(args), str(kwargs))
#    return 'get_group_photos_back_in_time'


@task.task()
def get_top_albums(bundle):
    facebook = bundle['facebook']
    return bundle
#    print 'in get_top_albums - args: %s, kwargs: %s' % (str(args), str(kwargs))
#    return 'get_top_albums'


@task.task()
def get_top_friends(bundle):
    facebook = bundle['facebook']
    # Albums you are tagged in the most,
    # photos in that album in points order
    return bundle
#    print 'in get_top_friends - args: %s, kwargs: %s' % (str(args), str(kwargs))
#    return 'get_top_friends'



## TASK GROUPS


# These need get_all_photos_user_is_in
need_all_photos_group = group([
    get_top_photos_of_year.subtask(),
    get_top_photos_of_first_half.subtask(),
    get_top_photos_of_second_half.subtask(),
    get_photos_back_in_time.subtask(),
    get_group_photos_back_in_time.subtask(),
    get_top_albums.subtask(),
])


@task.task()
def get_all_photos_and_run_group(bundle):
    return chain(
        get_all_photos_user_is_in.subtask(),
        need_all_photos_group
    ).apply_async((bundle,))


# These need _photo_score, which needs photos_i_like_ids
need_photo_score_group = group([
#    get_all_photos_user_is_in.subtask() | tasks.need_all_photos_group,
    get_all_photos_and_run_group.subtask(),
    get_photos_family.subtask(),
    get_photos_gfbf.subtask(),
])


@task.task()
def photos_i_like_and_run_group(bundle):
    return chain(
        get_photos_i_like.subtask(),
        need_photo_score_group
    ).apply_async((bundle,))


## MISSION CONTROL

def get_bundle_for_user(user):
    graph = user.profile.get_offline_graph()
    facebook = BackendFacebookUserConverter(graph)

    bundle = {
        'user': user,
        'graph': graph,
        'facebook': facebook,
    }
    return bundle


@task.task()
def run_yearbook(user):
    bundle = get_bundle_for_user(user)

    # These have no dependencies
    yearbook_job = group([
#        chain([tasks.get_photos_i_like.subtask(), need_photo_score]),
        photos_i_like_and_run_group.subtask(),
        get_all_group_shots.subtask(),
        get_top_friends.subtask(),
    ])
    job_async = yearbook_job.apply_async((bundle,))
    # interval is 0.5 by default
    # at 0.05 we spend 0.2 sec just retrieving the results (empty tasks)
    results = job_async.get(interval=0.05)
    # flatten the results
    flat_results = collapse_results(results)
    # store the results in the appropriate tables
    pass

    return flat_results


def collapse_results(results):
    """
    Recurse through async results,
    combining all values into one flat list
    """
    flat_list = []
    for curr_result in results:
        if hasattr(curr_result, 'join_native'):
            # Element is a GroupResult, call join()
            # note that GroupResult has .children as well
            # default interval is 0.5
            flat_list.extend(collapse_results(curr_result.join_native(interval=0.05)))
        elif hasattr(curr_result, 'children'):
            # Element is an AsyncResult
            flat_list.extend(collapse_results(curr_result.children))
        else:
            # Element is something else
            flat_list.append(curr_result)
    return flat_list
