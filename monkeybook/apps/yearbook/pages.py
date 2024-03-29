import logging
from itertools import chain
import dateutil.parser
from monkeybook.apps.account.models import FacebookUser
from monkeybook.apps.backend.models import Yearbook, FacebookPhoto
from monkeybook.apps.backend.settings import *

logger = logging.getLogger(__name__)

# Maximum number of alternate photos to provide.
NUM_ALT_PHOTOS = 25

class PageInvalidError(Exception):
    """
    This exception is raised when a page should be omitted,
    for instance if it is lacking some necessary data
    """


class YearbookPage(object):
    def __init__(self, page, template=None):
        self.page = page
        if template:
            self.template = template
        self.force_landscape = False
        

#    def set_user(self, user):
#        self.user = user
#        # Get the user's PhotoRankings
#        self.yearbook = Yearbook.objects.get(rankings__user=user)

    def get_alternate_photos(self):
        return []

#    def get_page_content(self, user):
    def get_page_content(self):
        """
        If the page raises an exception, kill it
        Any exception other than PageInvalidError, log
        """
#        self.set_user(user)
#        try:
        page_content = self.page_content()
#        except PageInvalidError:
            # The page is no good, return the empty page
#            pass
#        except Exception:
            # Some other error happened, log it
#            logger.error()
        page_content['page'] = self.page
        return page_content

    def update_image(self, index, id):
        # noop
        return
        
class StaticPage(YearbookPage):
    """
    Returns an empty div, the background image is set in CSS
    """
    template = 'full_bleed.html'

    def __init__(self, **kwargs):
        super(StaticPage, self).__init__(**kwargs)

    def page_content(self):
        return { }
        
    def get_alternate_photos(self):
       return []



class PhotoPage(YearbookPage):
    template = 'full_bleed_editable.html'

    def __init__(self, ranking_name, field_name, force_landscape=False, **kwargs):
        self.ranking_table_name = ranking_name
        self.index_field_name = field_name
        self.force_landscape = force_landscape
        super(PhotoPage, self).__init__(**kwargs)
        
    def get_alternate_photos(self):
        """Get a list of alternate photos. If there are not enough photos, pull from other categories"""
        alt_photos = []
        #pdb.set_trace()
        # for top_photos, looking at all rankings. For everything else
        # just looking at one ranking.
        if self.ranking_table_name == 'top_photos':
            ranking_names = Yearbook.lists_to_fields.keys()
            ranking_names.remove(self.ranking_table_name)
            ranking_names.remove('top_albums_photos')
            ranking_names.append(self.ranking_table_name)
        else:
            ranking_names = [self.ranking_table_name]
        
        
        while len(alt_photos) < NUM_ALT_PHOTOS and ranking_names:
            ranking_name = ranking_names.pop()
            ranked_photos = getattr(self.yearbook.rankings, ranking_name)
            photo_ids = self.yearbook.get_n_unused_photos_ids(ranked_photos, NUM_ALT_PHOTOS, force_landscape=self.force_landscape)
        alt_photos += [(i, FacebookPhoto.objects.get(pk=i).fb_url) for i in photo_ids]
        return alt_photos
        
    def get_photo(self, field_name=None):
        field_name = field_name or self.index_field_name
        
        
        photo_id = self.yearbook.get_photo_id_from_field_string(
            self.ranking_table_name, field_name
        )
        if not photo_id:
            photo = None
        else:
            photo = FacebookPhoto.objects.get(facebook_id=photo_id)
        return photo

    def get_photo_content(self, photo):
        return {
            'photo': photo
        }

    def get_next_image(self, next_index):
        # De-reference the field and get the next unallocated image

        next_photo_index = self.yearbook.get_next_unused_photo(
            self.ranking_table_name, self.index_field_name, unused_index=next_index, force_landscape=self.force_landscape
        )
        if not next_photo_index:
            return None
        else:
            next_photo = getattr(self.yearbook.rankings, self.ranking_table_name)[next_photo_index]
            next_photo_db = FacebookPhoto.objects.get(facebook_id=next_photo['id'])
            return next_photo_db

    def get_next_data(self, next_index):
        photo = self.get_next_image(next_index)
        return self.get_photo_content(photo)

    def page_content(self):
        # De-reference the field and return pic url
        photo = self.get_photo()
        return self.get_photo_content(photo)

    def update_image(self, index, id):
        #only 1 page, ignore index
        # Get image
        new_image = FacebookPhoto.objects.get(pk=id)
        new_index = None
        
        # massage image
        new_image_dict = vars(new_image)
        new_image_dict['id'] = new_image_dict['facebook_id']
        for key in new_image_dict.keys():
            if key not in ['id','created','width','fb_url','all_sizes','caption']:
                new_image_dict.pop(key, None)
        # add image to rankings
        rankings = getattr(self.yearbook.rankings, self.ranking_table_name)
        image_exists = False
        for i, photo in enumerate(rankings):
            if photo['id'] == new_image_dict['id']:
                image_exists = True
                new_index = i
                break
            
        if not image_exists:
            rankings.append(new_image_dict)
            new_index = len(rankings) - 1
        self.yearbook.rankings.save()
        
        # find index if not found
        
        # update pointer to last index in rankings
        setattr(self.yearbook, self.index_field_name, new_index)
        self.yearbook.save()
        
        
class PhotoPageDoublePort(PhotoPage):
    template='lands_sq_port_dbl_port.html'

    def __init__(self, field_name_2, **kwargs):
        self.index_field_name_2 = field_name_2
        super(PhotoPageDoublePort, self).__init__(**kwargs)

    def page_content(self):
        # De-reference the field and return pic url
        photo = self.get_photo()
        # Pull the second photo, if any
        # (only applies if first photo was portrait)
        photo_2 = self.get_photo(self.index_field_name_2)
        return {
            'photo': photo,
            'photo_2': photo_2
        }
        
    def update_image(self, index, id):
        #index=1 or 2
        #only 1 page, ignore index
        # Get image
        new_image = FacebookPhoto.objects.get(pk=id)
        new_index = None
        
        # massage image
        new_image_dict = vars(new_image)
        new_image_dict['id'] = new_image_dict['facebook_id']
        for key in new_image_dict.keys():
            if key not in ['id','created','width','fb_url','all_sizes','caption']:
                new_image_dict.pop(key, None)
        # add image to rankings
        rankings = getattr(self.yearbook.rankings, self.ranking_table_name)
        image_exists = False
        
        for i, photo in enumerate(rankings):
            if photo['id'] == new_image_dict['id']:
                image_exists = True
                new_index = i
                break
            
        if not image_exists:
            rankings.append(new_image_dict)
            new_index = len(rankings) - 1
            
        self.yearbook.rankings.save()
        
        # update pointer to last index in rankings
        field_name = self.index_field_name if index==1 else self.index_field_name_2
        setattr(self.yearbook, field_name, 
                len(getattr(self.yearbook.rankings, self.ranking_table_name))-1)
        self.yearbook.save()

#class SinglePhotoVariableLayout(PhotoPage):
#    template = 'lands_sq_port_dbl_port.html'


#class SinglePhotoVariableFullBleed(PhotoPage):
#    template = 'lands_sq_port_dbl_port_full_bleed.html'


class PhotoWithCommentPage(PhotoPage):
    template = 'photo_w_comment.html'

    def page_content(self):
        """
        Add the top comment, commenter's name and photo
        """
        photo = self.get_photo()
        page_content = self.get_photo_content(photo)
        top_comment = photo.get_top_comment()
        if top_comment:
            page_content['comment'] = top_comment['text']
            page_content['comment_name'] = top_comment['user_name']
            page_content['comment_pic'] = top_comment['user_pic']
        return page_content


class TopFriendNamePage(PhotoPage):
    template = 'top_friend_name.html'

    def __init__(self, ranking_name, field_name, stat_field, **kwargs):
        self.stat_field = stat_field
        super(TopFriendNamePage, self).__init__(ranking_name, field_name, **kwargs)

    def page_content(self):
        # De-reference the field and return
        # the user's first name and stat
        friend_id = self.yearbook.get_photo_from_field_string(
            self.ranking_table_name, self.index_field_name
        )
#        photo_list = self.yearbook.get_photo_from_field_string(
#            self.ranking_table_name, self.index_field_name
#        )
#        if photo_list:
        if friend_id:
            try:
                friend = FacebookUser.objects.get(facebook_id=friend_id)
                friend_stat = getattr(self.yearbook, self.stat_field)
                return {
                    'name': friend.first_name,
                    'pic': friend.pic_square,
                    'friend_stat': friend_stat,
                }
            except FacebookUser.DoesNotExist:
                return { }


class AlbumPage(PhotoPage):
    def __init__(self, ranking_name, field_prefix, max_photos, **kwargs):
        self.ranking_table_name = ranking_name
        self.field_prefix = field_prefix
        self.max_photos = max_photos
        # Calls *PhotoPage* constructor!
        super(PhotoPage, self).__init__(**kwargs)

    def get_alternate_photos(self):
        """Get a list of alternate photos. If there are not enough photos, pull from other categories"""
        album_name = self.get_album_name()
        alt_photos = []
        # for top_photos, looking at all rankings. For everything else
        # just looking at one ranking.
        ranked_photos = getattr(self.yearbook.rankings, self.ranking_table_name)
        album = None
        for album in ranked_photos:
            if album and album[0]['album_name'] == album_name:
                ranked_photos = album
        ranked_photos = [photo for photo in ranked_photos if photo['album_name'] == album_name]
        photo_ids = self.yearbook.get_n_unused_photos_ids(ranked_photos, NUM_ALT_PHOTOS, force_landscape=self.force_landscape)
        alt_photos += [(i, FacebookPhoto.objects.get(pk=i).fb_url) for i in photo_ids]
        return alt_photos
 
    def get_album_name(self):
        for photo_num in range(self.max_photos):
            photo = self.yearbook.get_photo_from_field_string(
                self.ranking_table_name, '%s_photo_%d' % (self.field_prefix, (photo_num + 1))
            )
            if photo:
                if 'album_name' in photo:
                    return photo['album_name']
                else:
                    return ''
           
    def update_image(self, index, id):
        #only 1 page, ignore index
        # Get image
        if index > self.max_photos:
            return
        album_name = self.get_album_name()
        new_image = FacebookPhoto.objects.get(pk=id)
        
        # massage image
        new_image_dict = vars(new_image)
        new_image_dict['id'] = new_image_dict['facebook_id']
        for key in new_image_dict.keys():
            if key not in ['id','created','width','fb_url','all_sizes','caption']:
                new_image_dict.pop(key, None)
                
        # find index
        rankings = getattr(self.yearbook.rankings, self.ranking_table_name)
        album = None
        new_index = 0
        for a in rankings:
            if a[0]['album_name'] == album_name:
                album = a
        if not album:
            print 'no album found'
            return
        for i, album_photo in enumerate(album):
            if album_photo['id'] == id:
                new_index = i
        
        print 'new index is ' + str(new_index)
        #[[albumname,...][albumname...]]
        # update pointer to last index in rankings
        field_name = '%s_photo_%d' %(self.field_prefix, index)
        setattr(self.yearbook, field_name.split('.')[1], new_index )
        self.yearbook.save()
         
    def get_album_photos(self, field_prefix):
        photos = []
        album_name = ''
        for photo_num in range(self.max_photos):
            photo = self.yearbook.get_photo_from_field_string(
                self.ranking_table_name, '%s_photo_%d' % (field_prefix, (photo_num + 1))
            )
            if photo:
                if 'album_name' in photo:
                    album_name = photo['album_name']
                else:
                    album_name = ''
                photo_id = self.yearbook._get_id_from_dict_or_int(photo)
                try:
                    photo = FacebookPhoto.objects.get(facebook_id=photo_id)
                    photos.append(photo)
                except FacebookPhoto.DoesNotExist:
                    logger.warn('Tried to get fb photo %s, referenced by album but not in db' % photo_id)
        return photos, album_name

    def get_next_image(self, next_index, photo_index):
        # De-reference the field and get the next unallocated image
        field_name = '%s_photo_%d' % (self.field_prefix, (photo_index+ 1))
        next_photo_index = self.yearbook.get_next_unused_photo(
            self.ranking_table_name, field_name, unused_index=next_index
        )
        album_num = getattr(self.yearbook, self.field_prefix.split('.')[0])
        next_photo = getattr(self.yearbook.rankings, self.ranking_table_name)[album_num][next_photo_index]
        next_photo_db = FacebookPhoto.objects.get(facebook_id=next_photo['id'])
        return self.get_photo_content(next_photo_db)

    def page_content(self):
        # Return up to `max_photos` photos, dereferenced to `ranking_name`
        photos, album_name = self.get_album_photos(self.field_prefix)
        # Sort them according to whether they are portrait or landscape
        photos_portrait = [photo for photo in photos if not photo.is_landscape()]       # includes square
        photos_landscape = [photo for photo in photos if photo.is_landscape()]

#        album_name = ''
#        if self.get_album_name:
#            # Manually get the album index
#            # self.field_prefix = 'top_album_1.top_album_1'
#            album_index = getattr(self.yearbook, self.field_prefix.split('.')[0])
#            album_info = self.yearbook.rankings.top_albums_ranked[album_index]
##            album_name = album_info['name']
#            album_name = ''

        page_content = {
            'photos': photos,
            'photos_portrait': photos_portrait,
            'photos_landscape': photos_landscape,
            'album_name': album_name,
        }
        return page_content


#class TopFriendPhotoPage(AlbumPage):
#    template='lands_sq_port_dbl_port_full_bleed.html'
#
#    def __init__(self, ranking_name, field_name, stat_field, **kwargs):
#        self.stat_field = stat_field
#        super(TopFriendPhotoPage, self).__init__(ranking_name, field_name, **kwargs)
#
#    def page_content(self):
#        pass


class MultiAlbumPage(AlbumPage):
    def __init__(self, max_albums, **kwargs):
        self.max_albums = max_albums
        super(MultiAlbumPage, self).__init__(**kwargs)

    def get_alternate_photos(self):
        """Get a list of alternate photos. If there are not enough photos, pull from other categories"""
        
        alt_photos = []
        # for top_photos, looking at all rankings. For everything else
        # just looking at one ranking.
        ranked_photos = getattr(self.yearbook.rankings, self.ranking_table_name)
        for album in ranked_photos:
            photo_ids = self.yearbook.get_n_unused_photos_ids(album, NUM_ALT_PHOTOS, force_landscape=self.force_landscape)
            alt_photos.append([(i, FacebookPhoto.objects.get(pk=i).fb_url) for i in photo_ids])
        return alt_photos

    def get_album_photos(self, field_prefix):
        photos = []
        for photo_num in range(self.max_photos):
            photo_id = self.yearbook.get_photo_id_from_field_string(
                self.ranking_table_name, '%s_photo_%d' % (field_prefix, (photo_num + 1))
            )
            if photo_id is not None:
                photo = FacebookPhoto.objects.get(facebook_id=photo_id)
                photos.append(photo)
        return photos

    def page_content(self):
        # Dereference up to `max_albums` albums, return up to `max_photos` from each
        albums_photos = []
        for album_index in range(1, self.max_albums + 1):
            album_field_prefix = '%s_%d.%s_%d' % (self.field_prefix, album_index, self.field_prefix, album_index)
            album_photos = self.get_album_photos(field_prefix=album_field_prefix)
            albums_photos.append(album_photos)

        # Flatten the list
        photos = list(chain.from_iterable(albums_photos))

        return {
            'photos': photos,
            'photos_reversed': list(reversed(photos)),
        }


class FieldPage(YearbookPage):
    def __init__(self, field_name, **kwargs):
        self.field_name = field_name
        super(FieldPage, self).__init__(**kwargs)

    def page_content(self):
        if '.' in self.field_name:
            name0, name1 = self.field_name.split('.')
            field0 = getattr(self.yearbook, name0)
            field_value = getattr(field0, name1)
        else:
            field_value = getattr(self.yearbook, self.field_name)
        return {
            self.field_name: field_value
        }

    def get_user_by_id(self, facebook_id):
        """
        Helper that looks up a user by id, where they could be the
        current user or one of the current user's facebook friends
        """
        try:
            fb_user = FacebookUser.objects.get(facebook_id=facebook_id)
            return fb_user
        except FacebookUser.DoesNotExist:
            return None


class TopStatusPage(FieldPage):
    template='top_status.html'

    def __init__(self, **kwargs):
        super(FieldPage, self).__init__(**kwargs)

    def get_alternate_photos(self):
       return []

    def page_content(self):
        top_post = self.yearbook.rankings.top_posts[self.yearbook.top_post]
        # Parse the date into a datetime
        top_post['created_time'] = dateutil.parser.parse(top_post['created_time'])
        # Resolve the user ids of the poster and the people who commented
        poster = None
        if 'actor_id' in top_post:
            poster_id = top_post['actor_id']
            if poster_id:
                poster = self.get_user_by_id(top_post['actor_id'])
                if not poster:
                    logger.warn('Unable to find poster of comment in db, #%d' % top_post['actor_id'])

        commentors = []
        comments_list = []
        if 'comments' in top_post and 'comment_list' in top_post['comments']:
            for comment in top_post['comments']['comment_list']:
                if 'fromid' in comment:
                    commentors.append(self.get_user_by_id(comment['fromid']))
                    # Note that if there wasn't a match, we still want to
                    # append `None` to the list, so it will iterate with the comments themselves

            comments_list = zip(top_post['comments']['comment_list'], commentors)

        page_content = {
            'top_post': top_post,
            'poster': poster,
            'comments_list': comments_list,
        }
        return page_content


class BirthdayPage(FieldPage):
    def __init__(self, first_half, **kwargs):
        self.first_half = first_half
        super(FieldPage, self).__init__(**kwargs)
        
    def get_alternate_photos(self):
       return []

    def page_content(self):
        max_posts = min(len(self.yearbook.birthday_posts), NUM_BIRTHDAY_POSTS)
        halfway = max_posts / 2
        if self.first_half:
            birthday_posts = self.yearbook.birthday_posts[:halfway]
        else:
            birthday_posts = self.yearbook.birthday_posts[halfway:max_posts]
        posters = []
        for post in birthday_posts:
            if 'actor_id' in post:
                posters.append(self.get_user_by_id(post['actor_id']))
#            else:
#                posters.append(None)

        posts_list = zip(birthday_posts, posters)
        return {
            'posts_list': posts_list,
            'posts_count': len(self.yearbook.birthday_posts)
        }


class FriendsCollagePage(YearbookPage):
    def __init__(self, first_half, **kwargs):
        self.first_half = first_half
        super(FriendsCollagePage, self).__init__(**kwargs)

    def page_content(self):
        max_faces = min(self.user.friends.count(), NUM_FRIENDS_IN_FACEPILE)
        halfway = max_faces / 2
        if self.first_half:
            query = self.user.friends.all()[:halfway]
        else:
            query = self.user.friends.all()[halfway:max_faces]
#        facepile_friend_pics = query.values_list('facebook_user__pic_square', flat=True)
        facepile_friends = query.values('facebook_user__pic_square', 'facebook_user__name')

        return {
#            'pics': facepile_friend_pics
            'friends': facepile_friends
        }


class YearbookPageFactory(object):

    def __init__(self, hash=None, user=None):
        assert hash or user

        self._pages = [
    #        FieldPage(            page=3,  field_name='owner.first_name'),
            StaticPage(           page=3,  template='page3.html'),
            # Top photos
            StaticPage(           page=4),
            PhotoPage(            page=5,  ranking_name='top_photos',             field_name='top_photo_1',         force_landscape=True),
            PhotoWithCommentPage( page=6,  ranking_name='top_photos',             field_name='top_photo_2'),
            PhotoWithCommentPage( page=7,  ranking_name='top_photos',             field_name='top_photo_3'),
            PhotoWithCommentPage( page=8,  ranking_name='top_photos',             field_name='top_photo_4'),
            PhotoWithCommentPage( page=9,  ranking_name='top_photos',             field_name='top_photo_5'),
            # Group photos
#            StaticPage(           page=10),
#            PhotoPage(            page=11, ranking_name='group_shots',            field_name='group_photo_1',       force_landscape=True),
#            PhotoWithCommentPage( page=12, ranking_name='group_shots',            field_name='group_photo_2',       template='photo_w_comment_lt.html'),
#            PhotoWithCommentPage( page=13, ranking_name='group_shots',            field_name='group_photo_3'),
            # Year photos
            StaticPage(           page=10),
            PhotoPage(            page=11, ranking_name='top_photos',             field_name='year_photo_1',  force_landscape=True),
            PhotoPageDoublePort(  page=12, ranking_name='top_photos',             field_name='year_photo_2',  field_name_2='year_photo_6'),
            PhotoPageDoublePort(  page=13, ranking_name='top_photos',             field_name='year_photo_3',  field_name_2='year_photo_7'),
            PhotoPageDoublePort(  page=14, ranking_name='top_photos',             field_name='year_photo_4',  field_name_2='year_photo_8'),
            PhotoPageDoublePort(  page=15, ranking_name='top_photos',             field_name='year_photo_5',  field_name_2='year_photo_9'),

            StaticPage(           page=16),
            AlbumPage(            page=17, ranking_name='top_albums_photos',    field_prefix='top_album_1.top_album_1', max_photos=ALBUM_PHOTOS_TO_SHOW, template='album_page_1.html'),
            AlbumPage(            page=18, ranking_name='top_albums_photos',    field_prefix='top_album_2.top_album_2', max_photos=ALBUM_PHOTOS_TO_SHOW, template='album_page_2.html'),
            AlbumPage(            page=19, ranking_name='top_albums_photos',    field_prefix='top_album_3.top_album_3', max_photos=ALBUM_PHOTOS_TO_SHOW, template='album_page_3.html'),
            StaticPage(           page=20),
            StaticPage(           page=21),
            StaticPage(           page=22),
            # Top status message
            TopStatusPage(        page=23),

            # Birthday comments
            # really a two-page spread
            BirthdayPage(         page=24, first_half=True,     template='birthday_left.html'),
            BirthdayPage(         page=25, first_half=False,    template='birthday_right.html'),

            # Top photos back in time
            # really a two-page spread
            MultiAlbumPage(       page=26, ranking_name='back_in_time', field_prefix='back_in_time', max_photos=1, max_albums=NUM_PREV_YEARS,   template='back_in_time_left.html'),
            MultiAlbumPage(       page=27, ranking_name='back_in_time', field_prefix='back_in_time', max_photos=1, max_albums=NUM_PREV_YEARS,   template='back_in_time_right.html'),
#            StaticPage(           page=32),
#            StaticPage(           page=33),
#            TopFriendNamePage(    page=34, ranking_name='top_friends_ids', field_name='top_friend_1',      stat_field='top_friend_1_stat'),
#            AlbumPage(            page=35, ranking_name='top_friends_photos', field_prefix='top_friend_1.top_friend_1', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
#            TopFriendNamePage(    page=36, ranking_name='top_friends_ids', field_name='top_friend_2',      stat_field='top_friend_2_stat'),
#            AlbumPage(            page=37, ranking_name='top_friends_photos', field_prefix='top_friend_2.top_friend_2', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
#            TopFriendNamePage(    page=38, ranking_name='top_friends_ids', field_name='top_friend_3',      stat_field='top_friend_3_stat'),
#            AlbumPage(            page=39, ranking_name='top_friends_photos', field_prefix='top_friend_3.top_friend_3', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
#            TopFriendNamePage(    page=40, ranking_name='top_friends_ids', field_name='top_friend_4',      stat_field='top_friend_4_stat'),
#            AlbumPage(            page=41, ranking_name='top_friends_photos', field_prefix='top_friend_4.top_friend_4', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
#            TopFriendNamePage(    page=42, ranking_name='top_friends_ids', field_name='top_friend_5',      stat_field='top_friend_5_stat'),
#            AlbumPage(            page=43, ranking_name='top_friends_photos', field_prefix='top_friend_5.top_friend_5', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),

            # Friends collage
            # really a two-page spread
            FriendsCollagePage(   page=28, first_half=True,     template='friends_collage_left.html'),
            FriendsCollagePage(   page=29, first_half=False,    template='friends_collage_right.html'),

            # Yearbook signs
#            StaticPage(           page=46),
#            StaticPage(           page=47),
#            StaticPage(           page=48),
#            StaticPage(           page=49),

            StaticPage(           page=30),
        ]
        # Set the user and yearbook on each Page instance
        if hash:
            yearbook = Yearbook.objects.get(hash=hash)
            user = yearbook.rankings.user
        else:
            yearbook = Yearbook.objects.filter(rankings__user=user)[0]
        for page in self._pages:
            page.user = user
            page.yearbook = yearbook

    def pages(self):
        return self._pages

    def get_page(self, page_num):
        for page in self._pages:
            if page.page == page_num:
                return page
        return None
