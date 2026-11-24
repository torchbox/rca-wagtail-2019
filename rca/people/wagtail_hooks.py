from django.templatetags.static import static
from django.utils.safestring import mark_safe
from wagtail import hooks


@hooks.register("insert_editor_js")
def editor_js():
    return mark_safe(  # noqa: S308 -- static asset URL, not user input
        '<script src="{}"></script>'.format(
            static("people/admin/js/update_person_title.js")
        )
    )


@hooks.register("insert_global_admin_js")
def global_admin_js():
    # hide the form once the page has loaded
    return mark_safe(  # noqa: S308 -- static asset URL, not user input
        '<script src="{}"></script>'.format(
            static("people/admin/js/student_side_bar.js")
        )
    )


@hooks.register("insert_global_admin_css")
def global_admin_css():
    # while the page is loading, hide the form to avoid a flash of the form
    return mark_safe(  # noqa: S308 -- static asset URL, not user input
        '<link rel="stylesheet" href="{}">'.format(
            static("people/admin/css/student_side_bar.css")
        )
    )
