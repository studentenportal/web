# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'front_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('twitter', self.gf('django.db.models.fields.CharField')(max_length=24, blank=True)),
            ('flattr', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
        ))
        db.send_create_signal(u'front', ['User'])

        # Create fake entries in the user table (HUGE HACK!)
        UserModel = orm.models['front.user']
        fakeusers = [UserModel(id=i, username='test%u' % i, password='test')
                     for i in range(10000)]
        UserModel.objects.bulk_create(fakeusers)

        # Adding M2M table for field groups on 'User'
        db.create_table(u'front_user_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'front.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(u'front_user_groups', ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        db.create_table(u'front_user_user_permissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'front.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(u'front_user_user_permissions', ['user_id', 'permission_id'])


        # Changing field 'QuoteVote.user'
        db.alter_column(u'front_quotevote', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['front.User']))

        # Changing field 'DocumentRating.user'
        db.alter_column(u'front_documentrating', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['front.User']))

        # Changing field 'LecturerRating.user'
        db.alter_column(u'front_lecturerrating', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['front.User']))

        # Changing field 'Quote.author'
        db.alter_column(u'front_quote', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['front.User']))

        # Changing field 'Event.author'
        db.alter_column(u'front_event', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['front.User']))

        # Changing field 'Document.uploader'
        db.alter_column(u'front_document', 'uploader_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['front.User']))

        # Changing field 'UserProfile.user'
        db.alter_column(u'front_userprofile', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['front.User'], unique=True))

    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'front_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table('front_user_groups')

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table('front_user_user_permissions')


        # Changing field 'QuoteVote.user'
        db.alter_column(u'front_quotevote', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'DocumentRating.user'
        db.alter_column(u'front_documentrating', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'LecturerRating.user'
        db.alter_column(u'front_lecturerrating', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'Quote.author'
        db.alter_column(u'front_quote', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'Event.author'
        db.alter_column(u'front_event', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'Document.uploader'
        db.alter_column(u'front_document', 'uploader_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'UserProfile.user'
        db.alter_column(u'front_userprofile', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True))

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
        u'front.document': {
            'Meta': {'ordering': "('-change_date',)", 'object_name': 'Document'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'Document'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['front.DocumentCategory']"}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'dtype': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'upload_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'uploader': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'Document'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['front.User']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'front.documentcategory': {
            'Meta': {'ordering': "['name']", 'object_name': 'DocumentCategory'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_module': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('apps.front.fields.CaseInsensitiveSlugField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'front.documentdownload': {
            'Meta': {'object_name': 'DocumentDownload'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'DocumentDownload'", 'to': u"orm['front.Document']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'front.documentrating': {
            'Meta': {'unique_together': "(('user', 'document'),)", 'object_name': 'DocumentRating'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'DocumentRating'", 'to': u"orm['front.Document']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'DocumentRating'", 'to': u"orm['front.User']"})
        },
        u'front.event': {
            'Meta': {'object_name': 'Event'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Event'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['front.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'front.lecturer': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Lecturer'},
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
        u'front.lecturerrating': {
            'Meta': {'unique_together': "(('user', 'lecturer', 'category'),)", 'object_name': 'LecturerRating'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lecturer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'LecturerRating'", 'to': u"orm['front.Lecturer']"}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'LecturerRating'", 'to': u"orm['front.User']"})
        },
        u'front.modulereview': {
            'Lecturer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'ModuleReview'", 'to': u"orm['front.Lecturer']"}),
            'Meta': {'object_name': 'ModuleReview'},
            'Module': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'ModuleReview'", 'to': u"orm['front.DocumentCategory']"}),
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
        u'front.quote': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Quote'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Quote'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['front.User']"}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lecturer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Quote'", 'to': u"orm['front.Lecturer']"}),
            'quote': ('django.db.models.fields.TextField', [], {})
        },
        u'front.quotevote': {
            'Meta': {'unique_together': "(('user', 'quote'),)", 'object_name': 'QuoteVote'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quote': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'QuoteVote'", 'to': u"orm['front.Quote']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'QuoteVote'", 'to': u"orm['front.User']"}),
            'vote': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'front.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'flattr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'twitter': ('django.db.models.fields.CharField', [], {'max_length': '24', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'front.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'flattr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'twitter': ('django.db.models.fields.CharField', [], {'max_length': '24', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['front.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['front']
