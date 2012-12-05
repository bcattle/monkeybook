# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'InviteRequestSent.facebook_user'
        db.delete_column('yearbook_inviterequestsent', 'facebook_user_id')

        # Deleting field 'InviteRequestSent.user'
        db.delete_column('yearbook_inviterequestsent', 'user_id')

        # Adding field 'InviteRequestSent.from_user'
        db.add_column('yearbook_inviterequestsent', 'from_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='invites_sent', to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'InviteRequestSent.to_facebook_user'
        db.add_column('yearbook_inviterequestsent', 'to_facebook_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['account.FacebookUser']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'InviteRequestSent.facebook_user'
        db.add_column('yearbook_inviterequestsent', 'facebook_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['account.FacebookUser']),
                      keep_default=False)

        # Adding field 'InviteRequestSent.user'
        db.add_column('yearbook_inviterequestsent', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='invites_sent', to=orm['auth.User']),
                      keep_default=False)

        # Deleting field 'InviteRequestSent.from_user'
        db.delete_column('yearbook_inviterequestsent', 'from_user_id')

        # Deleting field 'InviteRequestSent.to_facebook_user'
        db.delete_column('yearbook_inviterequestsent', 'to_facebook_user_id')


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'yearbook.inviterequestsent': {
            'Meta': {'object_name': 'InviteRequestSent'},
            'accepted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invites_sent'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'to_facebook_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.FacebookUser']"})
        },
        'yearbook.topfriendstat': {
            'Meta': {'object_name': 'TopFriendStat'},
            'friend_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tagged_with': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'them_comment_to_link': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'them_comment_to_photo': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'them_comment_to_status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'them_like_link': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'them_like_photo': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'them_like_status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'them_posts_to': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'top_friend_stats'", 'to': "orm['auth.User']"}),
            'you_links_liked': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'you_photos_liked': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'you_posts_to': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'you_statuses_liked': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'})
        },
        'yearbook.yearbooksign': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'YearbookSign'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_facebook_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'yearbook_signs_from'", 'to': "orm['account.FacebookUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'to_facebook_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'yearbook_signs_to'", 'to': "orm['account.FacebookUser']"})
        }
    }

    complete_apps = ['yearbook']