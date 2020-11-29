from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunSQL('CREATE EXTENSION IF NOT EXISTS citext;')
    ]
