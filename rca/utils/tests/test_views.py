import json

from django.test import TestCase


class AppleRemoteManagementViewTest(TestCase):
    def test_returns_200(self):
        response = self.client.get("/.well-known/com.apple.remotemanagement")
        self.assertEqual(response.status_code, 200)

    def test_content_type_is_json(self):
        response = self.client.get("/.well-known/com.apple.remotemanagement")
        self.assertEqual(response["Content-Type"], "application/json")

    def test_response_body(self):
        response = self.client.get("/.well-known/com.apple.remotemanagement")
        data = json.loads(response.content)
        self.assertEqual(
            data,
            {
                "Servers": [
                    {
                        "BaseURL": "https://ios-mdm.google.com/userenrollment/enroll",
                        "Version": "mdm-byod",
                    }
                ]
            },
        )
