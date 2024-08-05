# Generated by Django 4.2.14 on 2024-08-02 16:35

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("enquire_to_study", "0012_alter_enquiretostudysettings_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="enquiretostudysettings",
            name="intro_text",
            field=wagtail.fields.RichTextField(
                default=(
                    "<p>We are very much looking forward to hearing more from you. The RCA offers a unique and life changing way of thinking about and approaching art and design study and practice. If you would like to find out more about studying at the RCA, please fill out your details below and we will be in touch. Fields marked * are required.</p>"
                )
            ),
        ),
    ]
