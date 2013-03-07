from __future__ import division, print_function, unicode_literals
import logging, dateutil.parser
from voomza.apps.books_common.pages import PhotoPage, FieldPage, BookPage
from voomza.apps.account.models import FacebookUser
from voomza.apps.yearbook2012.settings import *

logger = logging.getLogger(__name__)


class TopFriendNamePage(PhotoPage):
    template = 'top_friend_name.html'

    def __init__(self, ranking_name, field_name, stat_field, **kwargs):
        self.stat_field = stat_field
        super(TopFriendNamePage, self).__init__(ranking_name, field_name, **kwargs)

    def page_content(self):
        # De-reference the field and return
        # the user's first name and stat
        friend_id = self.book.get_photo_from_field_string(
            self.ranking_table_name, self.index_field_name
        )
        #        photo_list = self.book.get_photo_from_field_string(
        #            self.ranking_table_name, self.index_field_name
        #        )
        #        if photo_list:
        if friend_id:
            try:
                friend = FacebookUser.objects.get(facebook_id=friend_id)
                friend_stat = getattr(self.book, self.stat_field)
                return {
                    'name': friend.first_name,
                    'pic': friend.pic_square,
                    'friend_stat': friend_stat,
                    }
            except FacebookUser.DoesNotExist:
                return { }


class TopStatusPage(FieldPage):
    template='top_status.html'

    def __init__(self, **kwargs):
        super(FieldPage, self).__init__(**kwargs)

    def page_content(self):
        top_post = self.book.rankings.top_posts[self.book.top_post]
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

    def page_content(self):
        max_posts = min(len(self.book.birthday_posts), NUM_BIRTHDAY_POSTS)
        halfway = max_posts / 2
        if self.first_half:
            birthday_posts = self.book.birthday_posts[:halfway]
        else:
            birthday_posts = self.book.birthday_posts[halfway:max_posts]
        posters = []
        for post in birthday_posts:
            if 'actor_id' in post:
                posters.append(self.get_user_by_id(post['actor_id']))
                #            else:
                #                posters.append(None)

        posts_list = zip(birthday_posts, posters)
        return {
            'posts_list': posts_list,
            'posts_count': len(self.book.birthday_posts)
        }


class FriendsCollagePage(BookPage):
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

