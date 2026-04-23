import re

from django.db import migrations

# Matches https?:// URLs or bare www. URLs
URL_RE = re.compile(r"((?:https?://|www\.)\S+)")


def text_to_richtext(text):
    """
    Wrap plain text in a <p> tag, converting bare URLs to <a> links.
    Display text for the link is the URL without the scheme prefix.
    Bare www. URLs get https:// prepended in the href.
    """

    def replace_url(match):
        url = match.group(1)
        # Strip trailing punctuation that isn't part of the URL
        stripped = url.rstrip(".,;:)")
        trailing = url[len(stripped):]
        if stripped.startswith("www."):
            href = f"https://{stripped}"
            display = stripped
        else:
            href = stripped
            display = re.sub(r"^https?://", "", stripped)
        return f'<a href="{href}">{display}</a>{trailing}'

    linked = URL_RE.sub(replace_url, text)
    return f"<p>{linked}</p>"


def migrate_summary_forward(apps, schema_editor):
    Scholarship = apps.get_model("scholarships", "Scholarship")
    for obj in Scholarship.objects.exclude(summary=""):
        if not obj.new_summary:
            obj.new_summary = text_to_richtext(obj.summary)
            obj.save(update_fields=["new_summary"])


class Migration(migrations.Migration):

    dependencies = [
        ("scholarships", "0014_scholarship_new_summary"),
    ]

    operations = [
        migrations.RunPython(migrate_summary_forward, migrations.RunPython.noop),
    ]
