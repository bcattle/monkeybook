from voomza.apps.books_common.page_factory import BaseBookPageFactory
from voomza.apps.books_common.pages import *
from voomza.apps.yearbook2012.pages import *
from voomza.apps.yearbook2012.settings import *


class Yearbook2012PageFactory(BaseBookPageFactory):
    _pages = [
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
        StaticPage(           page=10),
        PhotoPage(            page=11, ranking_name='group_shots',            field_name='group_photo_1',       force_landscape=True),
        PhotoWithCommentPage( page=12, ranking_name='group_shots',            field_name='group_photo_2',       template='photo_w_comment_lt.html'),
        PhotoWithCommentPage( page=13, ranking_name='group_shots',            field_name='group_photo_3'),
        # Year photos
        StaticPage(           page=14),
        PhotoPage(            page=15, ranking_name='top_photos',             field_name='year_photo_1',  force_landscape=True),
        PhotoPageDoublePort(  page=16, ranking_name='top_photos',             field_name='year_photo_2',  field_name_2='year_photo_6'),
        PhotoPageDoublePort(  page=17, ranking_name='top_photos',             field_name='year_photo_3',  field_name_2='year_photo_7'),
        PhotoPageDoublePort(  page=18, ranking_name='top_photos',             field_name='year_photo_4',  field_name_2='year_photo_8'),
        PhotoPageDoublePort(  page=19, ranking_name='top_photos',             field_name='year_photo_5',  field_name_2='year_photo_9'),

        StaticPage(           page=20),
        AlbumPage(            page=21, ranking_name='top_albums_photos',    field_prefix='top_album_1.top_album_1', max_photos=ALBUM_PHOTOS_TO_SHOW, template='album_page_1.html'),
        AlbumPage(            page=22, ranking_name='top_albums_photos',    field_prefix='top_album_2.top_album_2', max_photos=ALBUM_PHOTOS_TO_SHOW, template='album_page_2.html'),
        AlbumPage(            page=23, ranking_name='top_albums_photos',    field_prefix='top_album_3.top_album_3', max_photos=ALBUM_PHOTOS_TO_SHOW, template='album_page_3.html'),
        StaticPage(           page=24),
        StaticPage(           page=25),
        StaticPage(           page=26),
        # Top status message
        TopStatusPage(        page=27),

        # Birthday comments
        # really a two-page spread
        BirthdayPage(         page=28, first_half=True,     template='birthday_left.html'),
        BirthdayPage(         page=29, first_half=False,    template='birthday_right.html'),

        # Top photos back in time
        # really a two-page spread
        MultiAlbumPage(       page=30, ranking_name='back_in_time', field_prefix='back_in_time', max_photos=1, max_albums=NUM_PREV_YEARS,   template='back_in_time_left.html'),
        MultiAlbumPage(       page=31, ranking_name='back_in_time', field_prefix='back_in_time', max_photos=1, max_albums=NUM_PREV_YEARS,   template='back_in_time_right.html'),
        StaticPage(           page=32),
        StaticPage(           page=33),
        TopFriendNamePage(    page=34, ranking_name='top_friends_ids', field_name='top_friend_1',      stat_field='top_friend_1_stat'),
        AlbumPage(            page=35, ranking_name='top_friends_photos', field_prefix='top_friend_1.top_friend_1', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
        TopFriendNamePage(    page=36, ranking_name='top_friends_ids', field_name='top_friend_2',      stat_field='top_friend_2_stat'),
        AlbumPage(            page=37, ranking_name='top_friends_photos', field_prefix='top_friend_2.top_friend_2', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
        TopFriendNamePage(    page=38, ranking_name='top_friends_ids', field_name='top_friend_3',      stat_field='top_friend_3_stat'),
        AlbumPage(            page=39, ranking_name='top_friends_photos', field_prefix='top_friend_3.top_friend_3', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
        TopFriendNamePage(    page=40, ranking_name='top_friends_ids', field_name='top_friend_4',      stat_field='top_friend_4_stat'),
        AlbumPage(            page=41, ranking_name='top_friends_photos', field_prefix='top_friend_4.top_friend_4', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
        TopFriendNamePage(    page=42, ranking_name='top_friends_ids', field_name='top_friend_5',      stat_field='top_friend_5_stat'),
        AlbumPage(            page=43, ranking_name='top_friends_photos', field_prefix='top_friend_5.top_friend_5', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),

        # Friends collage
        # really a two-page spread
        FriendsCollagePage(   page=44, first_half=True,     template='friends_collage_left.html'),
        FriendsCollagePage(   page=45, first_half=False,    template='friends_collage_right.html'),

        # Yearbook signs
        StaticPage(           page=46),
        StaticPage(           page=47),
        StaticPage(           page=48),
        StaticPage(           page=49),

        StaticPage(           page=50),
    ]
