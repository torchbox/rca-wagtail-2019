from rca.utils.models import BasePage


class ShortCoursePage(BasePage):
    parent_page_types = ["guides.GuidePage"]
    template = "patterns/pages/shortcourses/short_course.html"
