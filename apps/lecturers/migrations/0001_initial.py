# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Lecturer'
        db.create_table(u'lecturers_lecturer', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('department', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('function', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('main_area', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('subjects', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('office', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal(u'lecturers', ['Lecturer'])

        # Adding model 'LecturerRating'
        db.create_table(u'lecturers_lecturerrating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'LecturerRating', to=orm['front.User'])),
            ('lecturer', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'LecturerRating', to=orm['lecturers.Lecturer'])),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=1, db_index=True)),
            ('rating', self.gf('django.db.models.fields.PositiveSmallIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'lecturers', ['LecturerRating'])

        # Adding unique constraint on 'LecturerRating', fields ['user', 'lecturer', 'category']
        db.create_unique(u'lecturers_lecturerrating', ['user_id', 'lecturer_id', 'category'])

        # Adding model 'Quote'
        db.create_table(u'lecturers_quote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'Quote', null=True, on_delete=models.SET_NULL, to=orm['front.User'])),
            ('lecturer', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'Quote', to=orm['lecturers.Lecturer'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('quote', self.gf('django.db.models.fields.TextField')()),
            ('comment', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal(u'lecturers', ['Quote'])

        # Adding model 'QuoteVote'
        db.create_table(u'lecturers_quotevote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'QuoteVote', to=orm['front.User'])),
            ('quote', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'QuoteVote', to=orm['lecturers.Quote'])),
            ('vote', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'lecturers', ['QuoteVote'])

        # Adding unique constraint on 'QuoteVote', fields ['user', 'quote']
        db.create_unique(u'lecturers_quotevote', ['user_id', 'quote_id'])

        # Adding model 'ModuleReview'
        db.create_table(u'lecturers_modulereview', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Module', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'ModuleReview', to=orm['documents.DocumentCategory'])),
            ('Lecturer', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'ModuleReview', to=orm['lecturers.Lecturer'])),
            ('semester', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('year', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('topic', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('understandability', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('effort', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('difficulty_module', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('difficulty_exam', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'lecturers', ['ModuleReview'])


    def backwards(self, orm):
        # Removing unique constraint on 'QuoteVote', fields ['user', 'quote']
        db.delete_unique(u'lecturers_quotevote', ['user_id', 'quote_id'])

        # Removing unique constraint on 'LecturerRating', fields ['user', 'lecturer', 'category']
        db.delete_unique(u'lecturers_lecturerrating', ['user_id', 'lecturer_id', 'category'])

        # Deleting model 'Lecturer'
        db.delete_table(u'lecturers_lecturer')

        # Deleting model 'LecturerRating'
        db.delete_table(u'lecturers_lecturerrating')

        # Deleting model 'Quote'
        db.delete_table(u'lecturers_quote')

        # Deleting model 'QuoteVote'
        db.delete_table(u'lecturers_quotevote')

        # Deleting model 'ModuleReview'
        db.delete_table(u'lecturers_modulereview')


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
        u'documents.documentcategory': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'DocumentCategory'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('apps.front.fields.CaseInsensitiveSlugField', [], {'unique': 'True', 'max_length': '32'})
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
        },
        u'lecturers.lecturer': {
            'Meta': {'ordering': "[u'last_name']", 'object_name': 'Lecturer'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'function': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'main_area': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'office': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'subjects': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        },
        u'lecturers.lecturerrating': {
            'Meta': {'unique_together': "((u'user', u'lecturer', u'category'),)", 'object_name': 'LecturerRating'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lecturer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'LecturerRating'", 'to': u"orm['lecturers.Lecturer']"}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'LecturerRating'", 'to': u"orm['front.User']"})
        },
        u'lecturers.modulereview': {
            'Lecturer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'ModuleReview'", 'to': u"orm['lecturers.Lecturer']"}),
            'Meta': {'object_name': 'ModuleReview'},
            'Module': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'ModuleReview'", 'to': u"orm['documents.DocumentCategory']"}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'difficulty_exam': ('django.db.models.fields.SmallIntegerField', [], {}),
            'difficulty_module': ('django.db.models.fields.SmallIntegerField', [], {}),
            'effort': ('django.db.models.fields.SmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'topic': ('django.db.models.fields.SmallIntegerField', [], {}),
            'understandability': ('django.db.models.fields.SmallIntegerField', [], {}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'lecturers.quote': {
            'Meta': {'ordering': "[u'-date']", 'object_name': 'Quote'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'Quote'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['front.User']"}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lecturer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'Quote'", 'to': u"orm['lecturers.Lecturer']"}),
            'quote': ('django.db.models.fields.TextField', [], {})
        },
        u'lecturers.quotevote': {
            'Meta': {'unique_together': "((u'user', u'quote'),)", 'object_name': 'QuoteVote'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quote': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'QuoteVote'", 'to': u"orm['lecturers.Quote']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'QuoteVote'", 'to': u"orm['front.User']"}),
            'vote': ('django.db.models.fields.BooleanField', [], {})
        }
    }

    complete_apps = ['lecturers']