# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TopFriendStat'
        db.delete_table('backend_topfriendstat')

        # Deleting field 'PhotoRankings.top_friend_5'
        db.delete_column('backend_photorankings', 'top_friend_5')

        # Deleting field 'PhotoRankings.gfbf_alone'
        db.delete_column('backend_photorankings', 'gfbf_alone')

        # Deleting field 'PhotoRankings.group_back_in_time_year_8'
        db.delete_column('backend_photorankings', 'group_back_in_time_year_8')

        # Deleting field 'PhotoRankings.group_back_in_time_year_1'
        db.delete_column('backend_photorankings', 'group_back_in_time_year_1')

        # Deleting field 'PhotoRankings.group_back_in_time_year_3'
        db.delete_column('backend_photorankings', 'group_back_in_time_year_3')

        # Deleting field 'PhotoRankings.group_back_in_time_year_2'
        db.delete_column('backend_photorankings', 'group_back_in_time_year_2')

        # Deleting field 'PhotoRankings.group_back_in_time_year_5'
        db.delete_column('backend_photorankings', 'group_back_in_time_year_5')

        # Deleting field 'PhotoRankings.group_back_in_time_year_4'
        db.delete_column('backend_photorankings', 'group_back_in_time_year_4')

        # Deleting field 'PhotoRankings.group_back_in_time_year_7'
        db.delete_column('backend_photorankings', 'group_back_in_time_year_7')

        # Deleting field 'PhotoRankings.group_back_in_time_year_6'
        db.delete_column('backend_photorankings', 'group_back_in_time_year_6')

        # Deleting field 'PhotoRankings.family_alone'
        db.delete_column('backend_photorankings', 'family_alone')

        # Deleting field 'PhotoRankings.top_friend_4'
        db.delete_column('backend_photorankings', 'top_friend_4')

        # Deleting field 'PhotoRankings.top_friend_1'
        db.delete_column('backend_photorankings', 'top_friend_1')

        # Deleting field 'PhotoRankings.top_friend_3'
        db.delete_column('backend_photorankings', 'top_friend_3')

        # Deleting field 'PhotoRankings.top_friend_2'
        db.delete_column('backend_photorankings', 'top_friend_2')

        # Adding field 'PhotoRankings.top_friends'
        db.add_column('backend_photorankings', 'top_friends',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Deleting field 'Yearbook.top_friend_2_photo_1'
        db.delete_column('backend_yearbook', 'top_friend_2_photo_1')

        # Adding field 'Yearbook.top_friend_1'
        db.add_column('backend_yearbook', 'top_friend_1',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Yearbook.top_friend_2'
        db.add_column('backend_yearbook', 'top_friend_2',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Yearbook.top_friend_3'
        db.add_column('backend_yearbook', 'top_friend_3',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Yearbook.top_friend_4'
        db.add_column('backend_yearbook', 'top_friend_4',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Yearbook.top_friend_5'
        db.add_column('backend_yearbook', 'top_friend_5',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'TopFriendStat'
        db.create_table('backend_topfriendstat', (
            ('them_like_status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('you_statuses_liked', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('you_links_liked', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('them_posts_to', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('them_comment_to_photo', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('friend_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('them_like_photo', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('them_comment_to_link', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('you_photos_liked', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('tagged_with', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='top_friend_stats', to=orm['auth.User'])),
            ('them_like_link', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('you_posts_to', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('them_comment_to_status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
        ))
        db.send_create_signal('backend', ['TopFriendStat'])

        # Adding field 'PhotoRankings.top_friend_5'
        db.add_column('backend_photorankings', 'top_friend_5',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.gfbf_alone'
        db.add_column('backend_photorankings', 'gfbf_alone',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.group_back_in_time_year_8'
        db.add_column('backend_photorankings', 'group_back_in_time_year_8',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.group_back_in_time_year_1'
        db.add_column('backend_photorankings', 'group_back_in_time_year_1',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.group_back_in_time_year_3'
        db.add_column('backend_photorankings', 'group_back_in_time_year_3',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.group_back_in_time_year_2'
        db.add_column('backend_photorankings', 'group_back_in_time_year_2',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.group_back_in_time_year_5'
        db.add_column('backend_photorankings', 'group_back_in_time_year_5',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.group_back_in_time_year_4'
        db.add_column('backend_photorankings', 'group_back_in_time_year_4',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.group_back_in_time_year_7'
        db.add_column('backend_photorankings', 'group_back_in_time_year_7',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.group_back_in_time_year_6'
        db.add_column('backend_photorankings', 'group_back_in_time_year_6',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.family_alone'
        db.add_column('backend_photorankings', 'family_alone',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.top_friend_4'
        db.add_column('backend_photorankings', 'top_friend_4',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.top_friend_1'
        db.add_column('backend_photorankings', 'top_friend_1',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.top_friend_3'
        db.add_column('backend_photorankings', 'top_friend_3',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Adding field 'PhotoRankings.top_friend_2'
        db.add_column('backend_photorankings', 'top_friend_2',
                      self.gf('jsonfield.fields.JSONField')(default=[], max_length=100000),
                      keep_default=False)

        # Deleting field 'PhotoRankings.top_friends'
        db.delete_column('backend_photorankings', 'top_friends')

        # Adding field 'Yearbook.top_friend_2_photo_1'
        db.add_column('backend_yearbook', 'top_friend_2_photo_1',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'Yearbook.top_friend_1'
        db.delete_column('backend_yearbook', 'top_friend_1')

        # Deleting field 'Yearbook.top_friend_2'
        db.delete_column('backend_yearbook', 'top_friend_2')

        # Deleting field 'Yearbook.top_friend_3'
        db.delete_column('backend_yearbook', 'top_friend_3')

        # Deleting field 'Yearbook.top_friend_4'
        db.delete_column('backend_yearbook', 'top_friend_4')

        # Deleting field 'Yearbook.top_friend_5'
        db.delete_column('backend_yearbook', 'top_friend_5')


    models = {
        'account.facebookuser': {
            'Meta': {'ordering': "['-friend_of__top_friends_order']", 'object_name': 'FacebookUser'},
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True', 'db_index': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pic_square': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'backend.facebookphoto': {
            'Meta': {'object_name': 'FacebookPhoto'},
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'fb_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'local_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'backend.minibook': {
            'Meta': {'object_name': 'Minibook'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'minibooks_from'", 'to': "orm['auth.User']"}),
            'photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'minibooks_to'", 'to': "orm['account.FacebookUser']"})
        },
        'backend.minibookrankings': {
            'Meta': {'object_name': 'MinibookRankings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minibook': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'photo_rankings'", 'unique': 'True', 'to': "orm['backend.Minibook']"}),
            'with_target': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'your_photos': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'})
        },
        'backend.photorankings': {
            'Meta': {'object_name': 'PhotoRankings'},
            'family_with': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'gfbf_with': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'group_shots': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'top_albums': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'top_friends': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'top_photos': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'top_photos_first_half': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'top_photos_second_half': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'photo_rankings'", 'to': "orm['auth.User']"}),
            'you_back_in_time_year_1': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_2': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_3': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_4': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_5': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_6': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_7': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_8': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'})
        },
        'backend.yearbook': {
            'Meta': {'object_name': 'Yearbook'},
            'back_in_time_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'back_in_time_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'back_in_time_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'back_in_time_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'back_in_time_photo_5': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'back_in_time_photo_6': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'back_in_time_photo_7': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'back_in_time_photo_8': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'family_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'family_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'family_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'family_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'first_half_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'first_half_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'first_half_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'gfbf_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'gfbf_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'gfbf_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'gfbf_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'group_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'group_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'group_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'group_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'yearbooks'", 'to': "orm['auth.User']"}),
            'second_half_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'second_half_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'second_half_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_1_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'top_album_1_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_1_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_1_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_1_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_2_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'top_album_2_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_2_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_2_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_2_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_3_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'top_album_3_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_3_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_3_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_album_3_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_1_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_1_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_1_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_2_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_2_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_3_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_3_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_3_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_4_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_4_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_4_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_5': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_5_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_5_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_friend_5_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'top_photo': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['backend']