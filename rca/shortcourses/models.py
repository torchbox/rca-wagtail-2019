from rca.utils.models import BasePage


class ShortCoursePage(BasePage):
    parent_page_types = ["programmes.ProgrammeIndexPage"]
    template = "patterns/pages/shortcourses/short_course.html"
