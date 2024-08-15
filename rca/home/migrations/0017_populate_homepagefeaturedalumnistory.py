# Generated by Django 4.2.15 on 2024-08-13 13:59

from django.db import migrations


def migrate_forwards(apps, schema_editor):
    HomePage = apps.get_model("home", "HomePage")
    HomePageFeaturedAlumniStory = apps.get_model("home", "HomePageFeaturedAlumniStory")
    EditorialPage = apps.get_model("editorial", "EditorialPage")
    home = HomePage.objects.only("id").first()
    stories = (
        EditorialPage.objects.filter(editorial_types__type__slug="alumni-story")
        .filter(live=True)
        .order_by("-published_at")[:3]
    )
    for i, story in enumerate(stories, start=1):
        HomePageFeaturedAlumniStory.objects.create(
            source_page=home, story=story, sort_order=i
        )


def migrate_backwards(apps, schema_editor):
    HomePageFeaturedAlumniStory = apps.get_model("home", "HomePageFeaturedAlumniStory")
    HomePageFeaturedAlumniStory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0016_remove_homepage_use_api_for_alumni_stories"),
    ]

    operations = [migrations.RunPython(migrate_forwards, migrate_backwards)]
