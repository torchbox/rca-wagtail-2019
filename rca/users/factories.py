import factory

from rca.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user-{n}")
    email = factory.Sequence(lambda n: f"user-{n}@example.com")
    first_name = factory.Faker("text", max_nb_chars=150)
    last_name = factory.Faker("text", max_nb_chars=150)
