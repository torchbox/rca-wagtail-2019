from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe


class User(AbstractUser):
    def is_student(self):
        return self.groups.filter(name="Students").exists()

    @property
    def student_group_name(self):
        """
        The name of the single student group for this student
        """
        if self.is_student():
            return f"Student: {self.username}"

    def group_links(self):
        groups = self.groups.all()
        if self.is_student():
            groups = self.groups.exclude(name=self.student_group_name)
        return [
            mark_safe(f'<a href="/admin/groups/{ g.pk }/users/">{ g.name }</a>')
            for g in groups
        ]

    class Meta:
        ordering = [
            "username",
        ]
