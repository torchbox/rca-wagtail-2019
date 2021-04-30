from wagtail.core import hooks

from rca.people.models import StudentPage


@hooks.register("construct_image_chooser_queryset")
def show_my_uploaded_images_only(images, request):
    # Only show uploaded images
    user = request.user
    # is this user a student?
    if not user.groups.filter(name="Students").exists():
        return images

    try:
        # Look up their student page
        student_page = StudentPage.objects.get(student_user_account=user)
        # Get the image collection the user is linked to through their student page
        # Note: for this to work the page must be published
        # TODO - fix - it needs to work with drafts
        student_collection = student_page.student_user_image_collection
    except StudentPage.DoesNotExist:
        # this is a student, but a page doesn't exists
        return images
    else:
        images = images.filter(collection=student_collection)

    return images
