# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DocumentCategory'
        db.create_table(u'documents_documentcategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('apps.front.fields.CaseInsensitiveSlugField')(unique=True, max_length=32)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'documents', ['DocumentCategory'])

        # Adding model 'Document'
        db.create_table(u'documents_document', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'Document', null=True, on_delete=models.PROTECT, to=orm['documents.DocumentCategory'])),
            ('dtype', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('document', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('original_filename', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('uploader', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'Document', null=True, on_delete=models.SET_NULL, to=orm['front.User'])),
            ('upload_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('license', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'documents', ['Document'])

        # Adding model 'DocumentDownload'
        db.create_table(u'documents_documentdownload', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'DocumentDownload', to=orm['documents.Document'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('ip', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, db_index=True)),
        ))
        db.send_create_signal(u'documents', ['DocumentDownload'])

        # Adding index on 'DocumentDownload', fields ['document', 'timestamp', 'ip']
        db.create_index(u'documents_documentdownload', ['document_id', 'timestamp', 'ip'])

        # Adding model 'DocumentRating'
        db.create_table(u'documents_documentrating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'DocumentRating', to=orm['front.User'])),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'DocumentRating', to=orm['documents.Document'])),
            ('rating', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal(u'documents', ['DocumentRating'])

        # Adding unique constraint on 'DocumentRating', fields ['user', 'document']
        db.create_unique(u'documents_documentrating', ['user_id', 'document_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'DocumentRating', fields ['user', 'document']
        db.delete_unique(u'documents_documentrating', ['user_id', 'document_id'])

        # Removing index on 'DocumentDownload', fields ['document', 'timestamp', 'ip']
        db.delete_index(u'documents_documentdownload', ['document_id', 'timestamp', 'ip'])

        # Deleting model 'DocumentCategory'
        db.delete_table(u'documents_documentcategory')

        # Deleting model 'Document'
        db.delete_table(u'documents_document')

        # Deleting model 'DocumentDownload'
        db.delete_table(u'documents_documentdownload')

        # Deleting model 'DocumentRating'
        db.delete_table(u'documents_documentrating')


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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'documents.document': {
            'Meta': {'ordering': "(u'-change_date',)", 'object_name': 'Document'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'Document'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['documents.DocumentCategory']"}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'dtype': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'upload_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'uploader': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'Document'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['front.User']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'documents.documentcategory': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'DocumentCategory'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('apps.front.fields.CaseInsensitiveSlugField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'documents.documentdownload': {
            'Meta': {'object_name': 'DocumentDownload', 'index_together': "[(u'document', u'timestamp', u'ip')]"},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'DocumentDownload'", 'to': u"orm['documents.Document']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'documents.documentrating': {
            'Meta': {'unique_together': "((u'user', u'document'),)", 'object_name': 'DocumentRating'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'DocumentRating'", 'to': u"orm['documents.Document']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'DocumentRating'", 'to': u"orm['front.User']"})
        },
        u'front.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'flattr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'twitter': ('django.db.models.fields.CharField', [], {'max_length': '24', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['documents']