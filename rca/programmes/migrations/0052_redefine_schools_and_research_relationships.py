# Generated by Django 2.2.9 on 2020-04-17 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0041_group_collection_permissions_verbose_name_plural"),
        ("programmes", "0051_update_revisions"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ProgrammePageRelatedSchoolsAndResearchPage",
            new_name="ProgrammePageRelatedSchoolsAndResearchPages",
        )
    ]
