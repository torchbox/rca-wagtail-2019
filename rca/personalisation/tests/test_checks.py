import os
import subprocess
import sys
from io import StringIO

from django.core import checks
from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.test import SimpleTestCase, override_settings


class CacheSigningKeyCheckTests(SimpleTestCase):
    def cache_checks(self):
        return [
            issue
            for issue in checks.run_checks(tags=[checks.Tags.security])
            if issue.id.startswith("personalisation.")
        ]

    def test_empty_key_intentionally_disables_caching_without_a_check_error(self):
        with override_settings(PERSONALISATION_CACHE_SIGNING_KEY=""):
            self.assertEqual(self.cache_checks(), [])

    def test_non_empty_keys_below_32_utf8_bytes_fail_the_check(self):
        for key in ["x" * 31, "£" * 15]:
            with self.subTest(key=key), override_settings(
                PERSONALISATION_CACHE_SIGNING_KEY=key
            ):
                issues = self.cache_checks()
                self.assertEqual(len(issues), 1)
                self.assertEqual(issues[0].id, "personalisation.E001")
                self.assertEqual(issues[0].level, checks.ERROR)
                self.assertIn("32 UTF-8 bytes", issues[0].msg)
                self.assertNotIn(key, str(issues[0]))

    def test_keys_at_or_above_32_utf8_bytes_pass_the_check(self):
        for key in ["x" * 32, "£" * 16, "x" * 64]:
            with self.subTest(key=key), override_settings(
                PERSONALISATION_CACHE_SIGNING_KEY=key
            ):
                self.assertEqual(self.cache_checks(), [])

    @override_settings(PERSONALISATION_CACHE_SIGNING_KEY="test-only-short-key")
    def test_management_check_reports_invalid_configuration(self):
        with self.assertRaisesMessage(SystemCheckError, "personalisation.E001"):
            call_command("check", tags=[checks.Tags.security], stderr=StringIO())

    def test_process_startup_warns_for_invalid_configuration_without_disclosing_key(
        self,
    ):
        for key, should_warn in [("test-only-short-key", True), ("", False)]:
            with self.subTest(configured=bool(key)):
                result = subprocess.run(
                    [sys.executable, "-c", "import django; django.setup()"],
                    env={
                        **os.environ,
                        "DJANGO_SETTINGS_MODULE": "rca.settings.test",
                        "PERSONALISATION_CACHE_SIGNING_KEY": key,
                    },
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual("personalisation.E001" in result.stderr, should_warn)
                if should_warn:
                    self.assertIn("WARNING", result.stderr)
                    self.assertIn("caching is disabled", result.stderr)
                    self.assertNotIn(key, result.stderr + result.stdout)
