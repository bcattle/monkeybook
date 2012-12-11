# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Yearbook.top_album_1_index'
        db.delete_column('backend_yearbook', 'top_album_1_index')

        # Deleting field 'Yearbook.top_album_3_index'
        db.delete_column('backend_yearbook', 'top_album_3_index')

        # Deleting field 'Yearbook.top_album_2_index'
        db.delete_column('backend_yearbook', 'top_album_2_index')

        # Adding field 'Yearbook.top_album_1'
        db.add_column('backend_yearbook', 'top_album_1',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Yearbook.top_album_2'
        db.add_column('backend_yearbook', 'top_album_2',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Yearbook.top_album_3'
        db.add_column('backend_yearbook', 'top_album_3',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Yearbook.top_album_1_index'
        db.add_column('backend_yearbook', 'top_album_1_index',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Yearbook.top_album_3_index'
        db.add_column('backend_yearbook', 'top_album_3_index',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Yearbook.top_album_2_index'
        db.add_column('backend_yearbook', 'top_album_2_index',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True),
                      keep_default=False)

        # Deleting field 'Yearbook.top_album_1'
        db.delete_column('backend_yearbook', 'top_album_1')

        # Deleting field 'Yearbook.top_album_2'
        db.delete_column('backend_yearbook', 'top_album_2')

        # Deleting field 'Yearbook.top_album_3'
        db.delete_column('backend_yearbook', 'top_album_3')


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
            'photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
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
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'photo_rankings'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'you_back_in_time_year_1': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_2': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_3': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_4': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_5': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_6': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'you_back_in_time_year_7': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'})
        },
        'backend.yearbook': {
            'Meta': {'object_name': 'Yearbook'},
            'back_in_time_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'back_in_time_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'back_in_time_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'back_in_time_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'back_in_time_photo_5': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'back_in_time_photo_6': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'back_in_time_photo_7': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'back_in_time_photo_8': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'birthday_posts': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'}),
            'family_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'family_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'family_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'family_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'first_half_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'first_half_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'first_half_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'gfbf_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'gfbf_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'gfbf_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'gfbf_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'group_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'group_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'group_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'group_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'yearbooks'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'second_half_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'second_half_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'second_half_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_1': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'top_album_1_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_1_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_1_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_1_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_2': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'top_album_2_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_2_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_2_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_2_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_3': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'top_album_3_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_3_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_3_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_album_3_photo_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_1_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_1_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_1_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_2_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_2_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_2_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_3_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_3_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_3_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_4': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_4_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_4_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_4_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_5': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_5_photo_1': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_5_photo_2': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_friend_5_photo_3': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_photo': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'top_post': ('jsonfield.fields.JSONField', [], {'default': '[]', 'max_length': '100000'})
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