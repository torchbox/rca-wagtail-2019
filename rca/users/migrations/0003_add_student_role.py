from django.db import migrations


def create_student_role(apps, schema_editor):
    Group = apps.get_model("auth.Group")
    Permission = apps.get_model("auth.Permission")
    ContentType = apps.get_model("contenttypes.ContentType")

    # Create auth groups
    students = Group.objects.create(name="Students")

    try:
        # Create admin permission
        admin_permission = Permission.objects.get(codename="access_admin",)
        area_of_expertise_permission = Permission.objects.get(
            codename="add_areaofexpertise",
        )
    except Permission.DoesNotExist:
        pass
    else:
        # Add permissions to the new students group
        students.permissions.add(admin_permission, area_of_expertise_permission)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_django_upgrade_user_fname"),
    ]

    operations = [
        migrations.RunPython(create_student_role),
    ]
