# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StoreProfile'
        db.create_table(u'checkout_storeprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'store_profile', unique=True, to=orm['auth.User'])),
            ('stripe_customer_id', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
        ))
        db.send_create_signal(u'checkout', ['StoreProfile'])

        # Adding model 'Order'
        db.create_table(u'checkout_order', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('stripe_single_use_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('charged_total', self.gf('django.db.models.fields.CharField')(max_length=8, blank=True)),
            ('abridged_quantity', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0, blank=True)),
            ('full_quantity', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0, blank=True)),
            ('digital_upgrade', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0, blank=True)),
            ('billing_address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('billing_address2', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('billing_country', self.gf('django_countries.fields.CountryField')(max_length=2)),
            ('billing_city', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('billing_state_province', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('billing_postal', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('shipping_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('shipping_address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('shipping_address2', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('shipping_country', self.gf('django_countries.fields.CountryField')(max_length=2)),
            ('shipping_city', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('shipping_state_province', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('shipping_postal', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'checkout', ['Order'])


    def backwards(self, orm):
        # Deleting model 'StoreProfile'
        db.delete_table(u'checkout_storeprofile')

        # Deleting model 'Order'
        db.delete_table(u'checkout_order')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'checkout.order': {
            'Meta': {'object_name': 'Order'},
            'abridged_quantity': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'billing_address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'billing_address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'billing_city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'billing_country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'billing_postal': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'billing_state_province': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'charged_total': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'digital_upgrade': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'full_quantity': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shipping_address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shipping_address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'shipping_city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'shipping_country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'shipping_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shipping_postal': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'shipping_state_province': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'stripe_single_use_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'checkout.storeprofile': {
            'Meta': {'object_name': 'StoreProfile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stripe_customer_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'store_profile'", 'unique': 'True', 'to': u"orm['auth.User']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['checkout']