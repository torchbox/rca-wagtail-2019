# Generated manually as initial migration for search app

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            "DROP EXTENSION IF EXISTS pg_trgm;",
        ),
    ]
