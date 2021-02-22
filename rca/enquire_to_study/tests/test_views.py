from http import HTTPStatus

from django.test import TestCase, RequestFactory
from django.urls import reverse

from rca.enquire_to_study.views import EnquireToStudyFormView


class EnquireToStudyFormViewTest(TestCase):
    def test_path_existed(self):
        response = self.client.get(reverse("enquire_to_study:enquire_to_study_form"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_environment_set_in_context(self):
        request = RequestFactory().get(reverse("enquire_to_study:enquire_to_study_form"))
        view = EnquireToStudyFormView()
        view.setup(request)

        context = view.get_context_data()
        self.assertIn('form', context)


class EnquireToStudyFormThanksViewTest(TestCase):
    def test_path_existed(self):
        response = self.client.get(reverse("enquire_to_study:enquire_to_study_thanks"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
