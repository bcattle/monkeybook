# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Badge.message'
        db.add_column('yearbook_badge', 'message',
                      self.gf('django.db.models.fields.CharField')(default='asdf', max_length=100),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Badge.message'
        db.delete_column('yearbook_badge', 'message')


    models = {
        'account.yearbookfacebookuser': {
            'Meta': {'unique_together': "(['user', 'facebook_id'],)", 'object_name': 'YearbookFacebookUser'},
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pic_square': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'top_friends_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
        'yearbook.badge': {
            'Meta': {'object_name': 'Badge'},
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'icon_small': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_tags': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'yearbook.badgevote': {
            'Meta': {'object_name': 'BadgeVote'},
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yearbook.Badge']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_facebook_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.YearbookFacebookUser']"})
        },
        'yearbook.inviterequestsent': {
            'Meta': {'object_name': 'InviteRequestSent'},
            'accepted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invites_sent'", 'to': "orm['auth.User']"})
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
            'Meta': {'object_name': 'YearbookSign'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['yearbook']