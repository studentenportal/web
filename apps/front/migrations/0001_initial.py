# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Lecturer'
        db.create_table('front_lecturer', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('department', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('function', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('main_area', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('subjects', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('office', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal('front', ['Lecturer'])

        # Adding model 'LecturerRating'
        db.create_table('front_lecturerrating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'LecturerRating', to=orm['auth.User'])),
            ('lecturer', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'LecturerRating', to=orm['front.Lecturer'])),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=1, db_index=True)),
            ('rating', self.gf('django.db.models.fields.PositiveSmallIntegerField')(db_index=True)),
        ))
        db.send_create_signal('front', ['LecturerRating'])

        # Adding unique constraint on 'LecturerRating', fields ['user', 'lecturer', 'category']
        db.create_unique('front_lecturerrating', ['user_id', 'lecturer_id', 'category'])

        # Adding model 'Quote'
        db.create_table('front_quote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Quote', null=True, to=orm['auth.User'])),
            ('lecturer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Quote', to=orm['front.Lecturer'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('quote', self.gf('django.db.models.fields.TextField')()),
            ('comment', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal('front', ['Quote'])

        # Adding model 'DocumentCategory'
        db.create_table('front_documentcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('front', ['DocumentCategory'])

        # Adding model 'Document'
        db.create_table('front_document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'Document', null=True, to=orm['front.DocumentCategory'])),
            ('dtype', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('document', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('original_filename', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('uploader', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'Document', null=True, to=orm['auth.User'])),
            ('upload_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('downloadcount', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('front', ['Document'])

        # Adding model 'DocumentRating'
        db.create_table('front_documentrating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'DocumentRating', to=orm['auth.User'])),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(related_name='DocumentRating', to=orm['front.Document'])),
            ('rating', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('front', ['DocumentRating'])

        # Adding unique constraint on 'DocumentRating', fields ['user', 'document']
        db.create_unique('front_documentrating', ['user_id', 'document_id'])

        # Adding model 'Event'
        db.create_table('front_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Event', null=True, to=orm['auth.User'])),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('start_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('front', ['Event'])

        # Adding model 'UserProfile'
        db.create_table('front_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('twitter', self.gf('django.db.models.fields.CharField')(max_length=24, blank=True)),
            ('flattr', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
        ))
        db.send_create_signal('front', ['UserProfile'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'DocumentRating', fields ['user', 'document']
        db.delete_unique('front_documentrating', ['user_id', 'document_id'])

        # Removing unique constraint on 'LecturerRating', fields ['user', 'lecturer', 'category']
        db.delete_unique('front_lecturerrating', ['user_id', 'lecturer_id', 'category'])

        # Deleting model 'Lecturer'
        db.delete_table('front_lecturer')

        # Deleting model 'LecturerRating'
        db.delete_table('front_lecturerrating')

        # Deleting model 'Quote'
        db.delete_table('front_quote')

        # Deleting model 'DocumentCategory'
        db.delete_table('front_documentcategory')

        # Deleting model 'Document'
        db.delete_table('front_document')

        # Deleting model 'DocumentRating'
        db.delete_table('front_documentrating')

        # Deleting model 'Event'
        db.delete_table('front_event')

        # Deleting model 'UserProfile'
        db.delete_table('front_userprofile')


    models = {
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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 26, 13, 2, 10, 98463)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 26, 13, 2, 10, 98311)'}),
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
        'front.document': {
            'Meta': {'ordering': "('-upload_date',)", 'object_name': 'Document'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'Document'", 'null': 'True', 'to': "orm['front.DocumentCategory']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'downloadcount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'dtype': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'upload_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'uploader': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'Document'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'front.documentcategory': {
            'Meta': {'ordering': "['name']", 'object_name': 'DocumentCategory'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'front.documentrating': {
            'Meta': {'unique_together': "(('user', 'document'),)", 'object_name': 'DocumentRating'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'DocumentRating'", 'to': "orm['front.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'DocumentRating'", 'to': "orm['auth.User']"})
        },
        'front.event': {
            'Meta': {'object_name': 'Event'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Event'", 'null': 'True', 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'front.lecturer': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Lecturer'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
        'front.lecturerrating': {
            'Meta': {'unique_together': "(('user', 'lecturer', 'category'),)", 'object_name': 'LecturerRating'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lecturer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'LecturerRating'", 'to': "orm['front.Lecturer']"}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'LecturerRating'", 'to': "orm['auth.User']"})
        },
        'front.quote': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Quote'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Quote'", 'null': 'True', 'to': "orm['auth.User']"}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lecturer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Quote'", 'to': "orm['front.Lecturer']"}),
            'quote': ('django.db.models.fields.TextField', [], {})
        },
        'front.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'flattr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'twitter': ('django.db.models.fields.CharField', [], {'max_length': '24', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['front']
