# Generated by Django 4.2.16 on 2025-01-13 15:08
import json

from django.db import migrations
from wagtail.blocks import StreamValue
from django.core.serializers.json import DjangoJSONEncoder


def migrate_further_information_to_block(apps, schema_editor):
    # Get the model where the fields are defined
    GuidePage = apps.get_model('guides', 'GuidePage')

    for page in GuidePage.objects.all():
        # Create an empty list to hold the StreamField data
        new_stream_data = []

        # If there's a further_information_title and/or further_information, add them to the new block
        if page.further_information_title or page.further_information:
            accordion_data = []

            # Add each item from `further_information` StreamField to `AccordionBlockWithTitle`
            for item in page.further_information:
                accordion_data.append({
                    'heading': item.value.get('heading', ''),
                    'preview_text': item.value.get('preview_text', ''),
                    'body': item.value.get('body').source if item.value.get('body') else '',
                    'link': {
                        'title': item.value.get('link').get('title', ''),
                        'url': item.value.get('link').get('url', ''),
                    },
                })

            # Add the title as the `AccordionBlock` heading
            accordion_block = {
                'type': 'accordion',
                'value': {
                    'heading': page.further_information_title,
                    'items': accordion_data,
                },
            }
            
            # Append the new block data to the StreamField
            new_stream_data.append(accordion_block)

            # Assign the new StreamField value to `further_information_block`
            page.further_information_block = StreamValue(
                page.further_information_block.stream_block,
                new_stream_data,
                is_lazy=True,
            )

            # Save the instance
            page.save()

class Migration(migrations.Migration):

    dependencies = [
        ("guides", "0030_guidepage_further_information_block"),
    ]

    operations = [
        migrations.RunPython(migrate_further_information_to_block, reverse_code=migrations.RunPython.noop),
    ]
