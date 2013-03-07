from celery import task
from voomza.apps.books_common.fql.albums import AlbumInfoTask, AlbumPhotosTask
from voomza.apps.books_common.settings import *


@task.task()
def pull_album_photos(user, album_score_and_date_by_id, exclude_albums=None, album_photo_score_fxn=None):
    album_results = get_album_names(user, album_score_and_date_by_id, exclude_albums)
    albums_ranked = album_results['albums_ranked']
    top_albums = album_results['top_albums']

    # Pull photos for the top albums
    task = AlbumPhotosTask(
        [album['id'] for album in top_albums],
        album_photo_score_fxn=album_photo_score_fxn
    )
    result = task.run(user)     # `process_photo_results` saved photos to db
    top_albums_photos = result['album_photos']

    # All album photos, sorted by score
    album_photos_by_score = [
        [
            {'id': photo['id'], 'score': photo['score'], 'album_name': top_albums[album_index]['name']}
            for photo in getter.order_by('score')
        ] for album_index, getter in enumerate(top_albums_photos)
    ]
    return album_photos_by_score, albums_ranked



@task.task()
def get_album_names(user, album_score_and_date_by_id, exclude_albums=None):
    exclude_albums = exclude_albums or []

    ## Pull album names, and reject any that are banned

    # Sort by year, score
    albums_ranked = sorted(
        album_score_and_date_by_id.iteritems(),
        key=lambda x: (x[1]['created'].year, x[1]['score']),
        reverse=True
    )

    # in order (id, {'created', 'score'})
    results = {}

    # Pull 10 albums at a time from the server
    top_albums = []
    album_ids_to_call = []
    while albums_ranked:
        album = albums_ranked.pop(0)
        album_ids_to_call.append(album[0])
        if len(album_ids_to_call) == ALBUMS_TO_PULL_AT_ONCE or not albums_ranked:
            # Make the API call
            task = AlbumInfoTask(album_ids_to_call)
            task_results = task.run(user)
            # Results came back as a list of getters
            # ea w/ a single element. Flatten to a dictionary
            results_by_id = {}
            for getter in task_results['album_info']:
                # Albums we don't have access to didn't return any items
                # if getter.fields_by_id.iteritems():
                if getter.fields_by_id:
                    # k,v = getter.fields_by_id.iteritems()[0]
                    k,v = getter.fields_by_id.iteritems().next()    # Only need the first one
                    results_by_id[k] = v

            # The albums came back in *random* order
            for album_id in album_ids_to_call:
                # Toss if no results, name banned, or has < 4 photos
                if album_id in results_by_id:
                    album = results_by_id[album_id]
                    if album['name'].lower() not in BANNED_ALBUM_NAMES \
                    and album['name'].lower() not in exclude_albums \
                    and album['size'] >= 4:
                        top_albums.append(album)
                        if len(top_albums) >= NUM_TOP_ALBUMS:
                            # We're done
                            # We need to keep track of what album we stopped on
                            # in case an `edit` link pushes us to the next album
                            results['albums_ranked'] = albums_ranked
                            results['top_albums'] = top_albums
                            return results

            # We pulled the ten albums
            # and didn't get enough, repeat
            album_ids_to_call = []

    # If we got here we ran out of albums
    # Just return what we had
    results['albums_ranked'] = []
    results['top_albums'] = top_albums
    return results


