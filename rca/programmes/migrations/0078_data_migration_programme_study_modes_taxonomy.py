# Generated by Django 3.2.16 on 2023-08-16 11:16

from django.db import migrations

STUDY_MODES = [
    "Full-time study",
    "Part-time study",
]


def set_programme_study_mode_based_on_programme_details_duration(
    apps, page, duration, cls
):
    ProgrammeStudyModeProgrammePage = apps.get_model(
        "programmes", "ProgrammeStudyModeProgrammePage"
    )

    if int(duration) == 1:  # Full-time study
        study_mode = cls.objects.get(title=STUDY_MODES[0])
        ProgrammeStudyModeProgrammePage.objects.create(
            programme_study_mode=study_mode, page=page
        )

    if int(duration) == 3:  # Part-time study
        study_mode = cls.objects.get(title=STUDY_MODES[1])
        ProgrammeStudyModeProgrammePage.objects.create(
            programme_study_mode=study_mode, page=page
        )

    if int(duration) == 2:  # Full-time study with part-time option
        for study_mode in cls.objects.filter(title__in=STUDY_MODES):
            ProgrammeStudyModeProgrammePage.objects.create(
                programme_study_mode=study_mode, page=page
            )


def set_programme_details_duration_based_on_programme_study_mode(apps, page):
    ProgrammeStudyModeProgrammePage = apps.get_model(
        "programmes", "ProgrammeStudyModeProgrammePage"
    )
    full_time = ProgrammeStudyModeProgrammePage.objects.filter(
        programme_study_mode__title=STUDY_MODES[0],
        page=page,
    ).first()
    part_time = ProgrammeStudyModeProgrammePage.objects.filter(
        programme_study_mode__title=STUDY_MODES[1],
        page=page,
    ).first()

    study_modes = page.programme_study_modes.all()
    if full_time in study_modes and part_time in study_modes:
        page.programme_details_duration = "2"
    elif full_time in study_modes:
        page.programme_details_duration = "1"
    elif part_time in study_modes:
        page.programme_details_duration = "3"
    else:
        page.programme_details_duration = ""


def forward_operation(apps, schema_editor):
    """
    - Create ProgrammeStudyMode objects for each study mode in STUDY_MODES
    - For each ProgrammePage, replace programme_details_duration with
    the appropriate programme study mode(s)
    """
    ProgrammeStudyMode = apps.get_model("programmes", "ProgrammeStudyMode")
    ProgrammePage = apps.get_model("programmes", "ProgrammePage")

    for study_mode in STUDY_MODES:
        ProgrammeStudyMode.objects.create(title=study_mode)

    for page in ProgrammePage.objects.all():
        if duration := page.programme_details_duration:
            set_programme_study_mode_based_on_programme_details_duration(
                apps, page, duration, ProgrammeStudyMode
            )


def reverse_operation(apps, schema_editor):
    """
    - For each ProgrammePage, replace programme study mode(s) with
    the appropriate programme_details_duration
    - Delete ProgrammeStudyMode objects for each study mode in STUDY_MODES
    """
    ProgrammeStudyMode = apps.get_model("programmes", "ProgrammeStudyMode")
    ProgrammePage = apps.get_model("programmes", "ProgrammePage")

    for page in ProgrammePage.objects.all():
        set_programme_details_duration_based_on_programme_study_mode(apps, page)

    for study_mode in STUDY_MODES:
        ProgrammeStudyMode.objects.filter(title=study_mode).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("programmes", "0077_add_programmestudymode"),
    ]

    operations = [
        migrations.RunPython(forward_operation, reverse_operation),
    ]