from wagtail.core import hooks

from rca.people.models import StudentPage


@hooks.register("construct_image_chooser_queryset")
def show_my_uploaded_images_only(images, request):
    # Limits the queryset for the image chooser if
    # the request.user is a student
    user = request.user

    if not user.is_student():
        return images

    try:
        # Look up their student page
        student_page = StudentPage.objects.get(student_user_account=user)
        # Get the image collection the user is linked to through their student page
        student_collection = student_page.student_user_image_collection
    except StudentPage.DoesNotExist:
        # This is a student, but a page doesn't exists so return no images
        return images.none()
    else:
        images = images.filter(collection=student_collection)

    return images
