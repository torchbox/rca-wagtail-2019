from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def is_student(self):
        return self.groups.filter(name="Students").exists()

    class Meta:
        ordering = [
            "username",
        ]
