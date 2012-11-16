# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TopFriend'
        db.create_table('yearbook_topfriend', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.UserProfile'])),
            ('friend', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.FacebookUserWithPic'])),
            ('rank', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('yearbook', ['TopFriend'])

        # Adding model 'TopFriendStats'
        db.create_table('yearbook_topfriendstats', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('top_friend', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['yearbook.TopFriend'], unique=True)),
            ('tagged_with', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('you_posts_to', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('you_photos_liked', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('you_links_liked', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('you_statuses_liked', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('them_posts_to', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('them_comment_to_photo', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('them_comment_to_link', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('them_comment_to_status', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('them_like_photo', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('them_like_link', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('them_like_status', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('yearbook', ['TopFriendStats'])

        # Adding model 'Badge'
        db.create_table('yearbook_badge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('icon', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('icon_small', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('yearbook', ['Badge'])

        # Adding model 'BadgeVote'
        db.create_table('yearbook_badgevote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('badge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yearbook.Badge'])),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('to_facebook_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.FacebookUserWithPic'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('yearbook', ['BadgeVote'])

        # Adding model 'YearbookSign'
        db.create_table('yearbook_yearbooksign', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('text', self.gf('django.db.models.fields.TextField')(max_length=1000)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('yearbook', ['YearbookSign'])


    def backwards(self, orm):
        # Deleting model 'TopFriend'
        db.delete_table('yearbook_topfriend')

        # Deleting model 'TopFriendStats'
        db.delete_table('yearbook_topfriendstats')

        # Deleting model 'Badge'
        db.delete_table('yearbook_badge')

        # Deleting model 'BadgeVote'
        db.delete_table('yearbook_badgevote')

        # Deleting model 'YearbookSign'
        db.delete_table('yearbook_yearbooksign')


    models = {
        'account.facebookuserwithpic': {
            'Meta': {'object_name': 'FacebookUserWithPic', '_ormbases': ['django_facebook.FacebookUser']},
            'facebookuser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['django_facebook.FacebookUser']", 'unique': 'True', 'primary_key': 'True'}),
            'picture': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'account.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'about_me': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'facebook_open_graph': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'family': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': "orm['account.FacebookUserWithPic']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'significant_other': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['account.FacebookUserWithPic']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'website_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
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
        'django_facebook.facebookuser': {
            'Meta': {'unique_together': "(['user_id', 'facebook_id'],)", 'object_name': 'FacebookUser'},
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'yearbook.badge': {
            'Meta': {'object_name': 'Badge'},
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'icon_small': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'yearbook.badgevote': {
            'Meta': {'object_name': 'BadgeVote'},
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yearbook.Badge']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_facebook_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.FacebookUserWithPic']"})
        },
        'yearbook.topfriend': {
            'Meta': {'object_name': 'TopFriend'},
            'friend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.FacebookUserWithPic']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.UserProfile']"})
        },
        'yearbook.topfriendstats': {
            'Meta': {'object_name': 'TopFriendStats'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tagged_with': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'them_comment_to_link': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'them_comment_to_photo': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'them_comment_to_status': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'them_like_link': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'them_like_photo': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'them_like_status': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'them_posts_to': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'top_friend': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['yearbook.TopFriend']", 'unique': 'True'}),
            'you_links_liked': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'you_photos_liked': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'you_posts_to': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'you_statuses_liked': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
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