import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import migrations

from rca.programmes.models import ProgrammePage


def update_revisions_with_current_programme_type(apps, schema_editor):
    for page in ProgrammePage.objects.all():
        programme_type = page.programme_type_id
        for revision in page.revisions.all():
            revision_data = json.loads(revision.content_json)
            revision_data["programme_type"] = programme_type
            revision.content_json = json.dumps(revision_data, cls=DjangoJSONEncoder)
            revision.save()


class Migration(migrations.Migration):
    dependencies = [("programmes", "0050_merge_20200206_1206")]
    operations = [migrations.RunPython(update_revisions_with_current_programme_type)]
