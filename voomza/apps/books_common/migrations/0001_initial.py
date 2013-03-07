# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FacebookPhoto'
        db.create_table(u'books_common_facebookphoto', (
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('people_in_photo', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('fb_url', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('local_url', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200)),
            ('caption', self.gf('django.db.models.fields.CharField')(default=u'', max_length=1000)),
            ('comments', self.gf('jsonfield.fields.JSONField')(default=u'[]', max_length=100000)),
        ))
        db.send_create_signal(u'books_common', ['FacebookPhoto'])

        # Adding model 'YearbookSign'
        db.create_table(u'books_common_yearbooksign', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_facebook_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'yearbook_signs_from', to=orm['account.FacebookUser'])),
            ('to_facebook_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'yearbook_signs_to', to=orm['account.FacebookUser'])),
            ('text', self.gf('django.db.models.fields.TextField')(max_length=1000)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('read', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'books_common', ['YearbookSign'])


    def backwards(self, orm):
        # Deleting model 'FacebookPhoto'
        db.delete_table(u'books_common_facebookphoto')

        # Deleting model 'YearbookSign'
        db.delete_table(u'books_common_yearbooksign')


    models = {
        u'account.facebookuser': {
            'Meta': {'ordering': "[u'-friend_of__top_friends_order']", 'object_name': 'FacebookUser'},
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'pic_square': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'books_common.facebookphoto': {
            'Meta': {'object_name': 'FacebookPhoto'},
            'caption': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '1000'}),
            'comments': ('jsonfield.fields.JSONField', [], {'default': "u'[]'", 'max_length': '100000'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'fb_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'local_url': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200'}),
            'people_in_photo': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'books_common.yearbooksign': {
            'Meta': {'ordering': "[u'-created_at']", 'object_name': 'YearbookSign'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_facebook_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'yearbook_signs_from'", 'to': u"orm['account.FacebookUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'to_facebook_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'yearbook_signs_to'", 'to': u"orm['account.FacebookUser']"})
        }
    }

    complete_apps = ['books_common']