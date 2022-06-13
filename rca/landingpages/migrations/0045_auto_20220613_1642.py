# Generated by Django 3.2.12 on 2022-06-13 15:42

from django.db import migrations
import rca.navigation.models
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('landingpages', '0044_merge_20210910_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumnilandingpage',
            name='additional_links',
            field=wagtail.fields.StreamField([('link', wagtail.blocks.StructBlock([('url', rca.navigation.models.URLOrRelativeURLBLock(required=False)), ('page', wagtail.blocks.PageChooserBlock(required=False)), ('title', wagtail.blocks.CharBlock(help_text="Leave blank to use the page's own title, required if using a URL", required=False))]))], blank=True, use_json_field=True, verbose_name='Additional Links'),
        ),
        migrations.AlterField(
            model_name='alumnilandingpage',
            name='collaborators',
            field=wagtail.fields.StreamField([('Collaborator', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))])), ('page', wagtail.blocks.PageChooserBlock(required=False))]))], blank=True, help_text='You can add up to 9 collaborators. Minimum 200 x 200 pixels.             Aim for logos that sit on either a white or transparent background.', use_json_field=True),
        ),
        migrations.AlterField(
            model_name='alumnilandingpage',
            name='latest_cta_block',
            field=wagtail.fields.StreamField([('call_to_action', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='A large heading diplayed at the top of block', required=False)), ('description', wagtail.blocks.CharBlock(required=False)), ('page', wagtail.blocks.PageChooserBlock(required=False)), ('link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))], help_text='An optional link to display below the expanded content', required=False))], label='text promo'))], blank=True, use_json_field=True, verbose_name='Text promo'),
        ),
        migrations.AlterField(
            model_name='alumnilandingpage',
            name='social_links',
            field=wagtail.fields.StreamField([('Link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='developmentlandingpage',
            name='help_cta_block',
            field=wagtail.fields.StreamField([('call_to_action', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='A large heading diplayed at the top of block', required=False)), ('description', wagtail.blocks.CharBlock(required=False)), ('page', wagtail.blocks.PageChooserBlock(required=False)), ('link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))], help_text='An optional link to display below the expanded content', required=False))], label='text promo'))], blank=True, use_json_field=True, verbose_name='Text promo'),
        ),
        migrations.AlterField(
            model_name='developmentlandingpage',
            name='social_links',
            field=wagtail.fields.StreamField([('Link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='developmentlandingpage',
            name='stories_cta_block',
            field=wagtail.fields.StreamField([('call_to_action', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='A large heading diplayed at the top of block', required=False)), ('description', wagtail.blocks.CharBlock(required=False)), ('page', wagtail.blocks.PageChooserBlock(required=False)), ('link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))], help_text='An optional link to display below the expanded content', required=False))], label='text promo'))], blank=True, use_json_field=True, verbose_name='Text promo'),
        ),
        migrations.AlterField(
            model_name='eelandingpage',
            name='cta_block',
            field=wagtail.fields.StreamField([('call_to_action', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='A large heading diplayed at the top of block', required=False)), ('description', wagtail.blocks.CharBlock(required=False)), ('page', wagtail.blocks.PageChooserBlock(required=False)), ('link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))], help_text='An optional link to display below the expanded content', required=False))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='landingpage',
            name='cta_block',
            field=wagtail.fields.StreamField([('call_to_action', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='A large heading diplayed at the top of block', required=False)), ('description', wagtail.blocks.CharBlock(required=False)), ('page', wagtail.blocks.PageChooserBlock(required=False)), ('link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))], help_text='An optional link to display below the expanded content', required=False))], label='text promo'))], blank=True, use_json_field=True, verbose_name='Text promo'),
        ),
        migrations.AlterField(
            model_name='landingpage',
            name='page_list',
            field=wagtail.fields.StreamField([('page_list', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(help_text='A large heading diplayed at the top of block', required=False)), ('page', wagtail.blocks.StreamBlock([('page', wagtail.blocks.PageChooserBlock()), ('custom_teaser', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('meta', wagtail.blocks.CharBlock(help_text='Small tag value displayed below the title', required=False)), ('text', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock()), ('link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))], required=False))]))])), ('link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))], help_text='An optional link to display below the expanded content', required=False)), ('page_link', wagtail.blocks.PageChooserBlock(required=False))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='landingpagepageslideshowblock',
            name='slides',
            field=wagtail.fields.StreamField([('slide', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('title', wagtail.blocks.CharBlock(required=False)), ('type', wagtail.blocks.CharBlock(required=False)), ('summary', wagtail.blocks.TextBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='landingpagestatsblock',
            name='statistics',
            field=wagtail.fields.StreamField([('statistic', wagtail.blocks.StructBlock([('summary', wagtail.blocks.CharBlock(help_text='E.g.  1 in 3 of our graduates are business owners or independent professionals', required=False)), ('before', wagtail.blocks.CharBlock(required=False)), ('after', wagtail.blocks.CharBlock(help_text="E.g. '%'", max_length=2, required=False)), ('number', wagtail.blocks.IntegerBlock(help_text="E.g. '33'", required=False)), ('meta', wagtail.blocks.CharBlock(help_text="Small title below the number, e.g 'Nationalities'", required=False))]))], use_json_field=True),
        ),
    ]
