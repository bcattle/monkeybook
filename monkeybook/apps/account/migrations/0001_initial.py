# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table('account_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('about_me', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')(db_index=True, unique=True, null=True, blank=True)),
            ('access_token', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('facebook_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('facebook_profile_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('website_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('blog_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('raw_data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('facebook_open_graph', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('facebook_user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, null=True, to=orm['account.FacebookUser'])),
            ('locale', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('relationship_status', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('significant_other_id', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('current_page', self.gf('django.db.models.fields.CharField')(default='invite_friends_to_sign', max_length=40)),
        ))
        db.send_create_signal('account', ['UserProfile'])

        # Adding model 'FamilyConnection'
        db.create_table('account_familyconnection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='family', to=orm['auth.User'])),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('relationship', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
        ))
        db.send_create_signal('account', ['FamilyConnection'])

        # Adding model 'FacebookUser'
        db.create_table('account_facebookuser', (
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('pic_square', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('account', ['FacebookUser'])

        # Adding model 'FacebookFriend'
        db.create_table('account_facebookfriend', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('facebook_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='friend_of', to=orm['account.FacebookUser'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='friends', to=orm['auth.User'])),
            ('top_friends_order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0, db_index=True)),
        ))
        db.send_create_signal('account', ['FacebookFriend'])

        # Adding unique constraint on 'FacebookFriend', fields ['owner', 'facebook_user']
        db.create_unique('account_facebookfriend', ['owner_id', 'facebook_user_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'FacebookFriend', fields ['owner', 'facebook_user']
        db.delete_unique('account_facebookfriend', ['owner_id', 'facebook_user_id'])

        # Deleting model 'UserProfile'
        db.delete_table('account_userprofile')

        # Deleting model 'FamilyConnection'
        db.delete_table('account_familyconnection')

        # Deleting model 'FacebookUser'
        db.delete_table('account_facebookuser')

        # Deleting model 'FacebookFriend'
        db.delete_table('account_facebookfriend')


    models = {
        'account.facebookfriend': {
            'Meta': {'ordering': "['-top_friends_order']", 'unique_together': "(['owner', 'facebook_user'],)", 'object_name': 'FacebookFriend'},
            'facebook_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'friend_of'", 'to': "orm['account.FacebookUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'friends'", 'to': "orm['auth.User']"}),
            'top_friends_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'db_index': 'True'})
        },
        'account.facebookuser': {
            'Meta': {'ordering': "['-friend_of__top_friends_order']", 'object_name': 'FacebookUser'},
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'pic_square': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'account.familyconnection': {
            'Meta': {'object_name': 'FamilyConnection'},
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'family'", 'to': "orm['auth.User']"}),
            'relationship': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        'account.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'about_me': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'current_page': ('django.db.models.fields.CharField', [], {'default': "'invite_friends_to_sign'", 'max_length': '40'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'facebook_open_graph': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'null': 'True', 'to': "orm['account.FacebookUser']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'relationship_status': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'significant_other_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"}),
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
        }
    }

    complete_apps = ['account']